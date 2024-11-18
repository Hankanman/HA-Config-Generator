# area_config_generator/cli/interface.py

import click

from ..devices.manager import DeviceManager
from ..generators import climate, occupancy, power
from ..utils.types import AreaConfigType, Features, TemplateItem
from ..utils.validation import ensure_template_items
from ..utils.yaml_writer import write_yaml_config
from .entity_config import get_entity_config
from .feature_config import get_area_features
from .input_config import generate_input_controls

# Initialize the device manager
device_manager = DeviceManager()


@click.command()
@click.argument("area_name")
def main(area_name: str) -> None:
    """Generate a Home Assistant area configuration."""
    click.echo(f"Generating configuration for {area_name}")

    # Get features using normalized area name
    features: Features = get_area_features(area_name, device_manager)

    # Store both original and normalized area names in features
    features["area_name"] = area_name
    features["normalized_area_name"] = area_name.lower()

    # Get entity confirmations using normalized area name
    features["entity_ids"] = get_entity_config(area_name, features)

    config: AreaConfigType = generate_area_config(area_name, features)
    write_yaml_config(area_name.lower(), config)

    click.echo(f"Configuration generated for {area_name}")


def generate_area_config(area_name: str, features: Features) -> AreaConfigType:
    """Generate the complete area configuration.

    Args:
        area_name: The name of the area
        features: The features configuration

    Returns:
        Complete area configuration
    """
    templates: list[TemplateItem] = []

    # Generate occupancy config if needed
    if features.get("motion_sensor") or features.get("door_sensor"):
        occupancy_configs = ensure_template_items(occupancy.generate_occupancy_config(features))
        templates.extend(occupancy_configs)

    # Generate device configurations
    if features.get("power_monitoring"):
        device_configs = device_manager.generate_all_device_configs(features)
        for device_config in device_configs:
            if "template" in device_config:
                templates.extend(ensure_template_items(device_config["template"]))

        # Generate power monitoring config
        power_configs = ensure_template_items(power.generate_power_config(features))
        templates.extend(power_configs)

    # Generate climate control config if needed
    if features.get("climate_control"):
        climate_configs = ensure_template_items(climate.generate_climate_config(features))
        templates.extend(climate_configs)

    # Generate input controls
    input_controls = generate_input_controls(features)

    # Create area configuration
    area_config: AreaConfigType = {
        area_name: {
            "template": templates,
            "input_number": input_controls["input_number"],
            "input_boolean": input_controls["input_boolean"],
        }
    }

    return area_config


if __name__ == "__main__":
    main()
