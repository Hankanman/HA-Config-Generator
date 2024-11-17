# area_config_generator/cli/interface.py
from typing import Dict, List
import click
from ..generators import occupancy, power, climate
from ..utils.yaml_writer import write_yaml_config


@click.command()
@click.argument("area_name")
def main(area_name: str):
    """Generate a Home Assistant area configuration."""
    click.echo(f"Generating configuration for {area_name}")

    # Get area features
    features = get_area_features()

    # Generate configurations
    config = generate_area_config(area_name, features)

    # Write configuration
    write_yaml_config(area_name, config)

    click.echo(f"Configuration generated for {area_name}")


def get_area_features() -> Dict[str, bool]:
    """Interactive CLI to determine area features."""
    features = {}

    # Basic features
    features["motion_sensor"] = click.confirm(
        "Does this area have motion sensors?", default=True
    )
    features["door_sensor"] = click.confirm(
        "Does this area have door sensors?", default=True
    )
    features["window_sensor"] = click.confirm(
        "Does this area have window sensors?", default=False
    )
    features["temperature_sensor"] = click.confirm(
        "Does this area have temperature sensors?", default=True
    )

    # Device types
    if click.confirm("Does this area have powered devices?", default=True):
        features["power_monitoring"] = True
        features["devices"] = get_device_types()
    else:
        features["power_monitoring"] = False
        features["devices"] = []

    # Climate control
    features["climate_control"] = click.confirm(
        "Does this area have climate control?", default=True
    )

    return features


def get_device_types() -> List[str]:
    """Get specific devices in the area."""
    devices = []

    device_options = {
        "computer": "Computer/PC setup",
        "tv": "Television/Entertainment system",
        "appliance": "Major appliances (washing machine, dishwasher, etc)",
        "lighting": "Smart lighting",
        "bathroom": "Bathroom fixtures (shower, toilet, etc)",
        "kitchen": "Kitchen appliances (fridge, oven, etc)",
    }

    click.echo("\nSelect devices present in this area:")
    for key, desc in device_options.items():
        if click.confirm(f"Is there a {desc}?", default=False):
            devices.append(key)

    return devices


def generate_area_config(area_name: str, features: Dict[str, bool]) -> Dict:
    """Generate the complete area configuration."""
    config = {area_name: {}}

    # Add template section
    config[area_name]["template"] = []

    # Add occupancy detection if motion or door sensors present
    if features["motion_sensor"] or features["door_sensor"]:
        config[area_name]["template"].extend(
            occupancy.generate_occupancy_config(features)
        )

    # Add power monitoring if required
    if features["power_monitoring"]:
        config[area_name]["template"].extend(
            power.generate_power_config(features["devices"])
        )

    # Add climate control if present
    if features["climate_control"]:
        config[area_name]["template"].extend(climate.generate_climate_config(features))

    # Add input controls
    config[area_name].update(generate_input_controls(features))

    return config


def generate_input_controls(features: Dict[str, bool]) -> Dict:
    """Generate input_number and input_boolean configurations."""
    controls = {}

    # Add power threshold if power monitoring enabled
    if features["power_monitoring"]:
        controls["input_number"] = {
            f"{features['area_name']}_power_threshold": {
                "name": f"{features['area_name'].title()} Power Alert Threshold",
                "min": 100,
                "max": 1000,
                "step": 50,
                "unit_of_measurement": "W",
                "icon": "mdi:flash-alert",
                "initial": 400,
            }
        }

    # Add temperature controls if climate control present
    if features["climate_control"]:
        if "input_number" not in controls:
            controls["input_number"] = {}

        controls["input_number"][f"{features['area_name']}_temp_threshold"] = {
            "name": f"{features['area_name'].title()} Temperature Threshold",
            "min": 19,
            "max": 25,
            "step": 0.5,
            "unit_of_measurement": "°C",
            "icon": "mdi:thermometer",
            "initial": 23,
        }

    # Add basic controls
    controls["input_boolean"] = {
        f"{features['area_name']}_occupied_override": {
            "name": f"{features['area_name'].title()} Manual Occupancy Override",
            "icon": "mdi:account-check",
        },
        f"{features['area_name']}_sleep_mode": {
            "name": f"{features['area_name'].title()} Sleep Mode",
            "icon": "mdi:power-sleep",
        },
    }

    return controls
