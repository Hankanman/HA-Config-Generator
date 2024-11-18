from collections.abc import Iterable
from typing import Any, Dict, List, TypeGuard, Union, cast

import click

from ..generators import climate, occupancy, power
from ..utils.types import (
    AreaConfigType,
    DeviceOptionsType,
    EntityConfig,
    EntityIds,
    EntityType,
    Features,
    InputBooleanConfig,
    InputNumberConfig,
    LightingDefaults,
    TemplateConfigItem,
    convert_area_config_to_config,
    convert_template_config_to_item,
)
from ..utils.yaml_writer import write_yaml_config


def confirm_entity_id(domain: EntityType, suggested_id: str, description: str) -> str:
    """Confirm entity ID with user."""
    # Ensure entity ID is lowercase
    suggested_id = suggested_id.lower()
    default_id = f"{domain}.{suggested_id}"

    # First try with just a prompt that allows empty (default) value
    entity_id = click.prompt(
        f"Please confirm the {description} entity ID", default=default_id, show_default=True, type=str
    ).strip()

    # If they just hit enter or entered the default exactly, return it
    if not entity_id or entity_id == default_id:
        return default_id

    # Otherwise validate their custom entry
    while True:
        # Strip any quotes they may have added
        entity_id = entity_id.strip('"').strip("'")
        # Ensure entity ID is lowercase
        entity_id = entity_id.lower()

        # Validate format
        if "." not in entity_id:
            click.echo(f"Invalid format. Must be in format: {domain}.entity_id")
            entity_id = click.prompt("Please try again", default=default_id, type=str)
            continue

        prefix = entity_id.split(".", 1)[0]
        if prefix != domain:
            click.echo(f"Invalid domain. Must start with: {domain}")
            entity_id = click.prompt("Please try again", default=default_id, type=str)
            continue

        return entity_id


def get_entity_config(area_name: str, features: Features) -> EntityIds:
    """Get and confirm all entity IDs for the area."""
    # Explicitly type the list of entities
    entities: List[EntityConfig] = []
    confirmed_entities: EntityIds = {}

    # Normalize area_name for entity IDs while preserving original for display
    normalized_area_name = area_name.lower()

    # Basic entities
    if features.get("climate_control"):
        entities.append({"domain": "climate", "suggested_id": normalized_area_name, "description": "climate control"})

    if features.get("motion_sensor"):
        entities.append(
            {
                "domain": "binary_sensor",
                "suggested_id": f"{normalized_area_name}_motion",
                "description": "motion sensor",
            }
        )

    if features.get("door_sensor"):
        entities.append(
            {
                "domain": "binary_sensor",
                "suggested_id": f"{normalized_area_name}_door_contact",
                "description": "door contact sensor",
            }
        )

    if features.get("temperature_sensor"):
        entities.append(
            {
                "domain": "sensor",
                "suggested_id": f"{normalized_area_name}_temperature",
                "description": "temperature sensor",
            }
        )

    # Lighting entities
    if features.get("smart_lighting"):
        # Explicitly type the light and scene entities
        light_group_entity: EntityConfig = {
            "domain": "light",
            "suggested_id": f"{normalized_area_name}_lights",
            "description": "area light group",
        }
        light_scene_entity: EntityConfig = {
            "domain": "scene",
            "suggested_id": f"{normalized_area_name}_light_scene",
            "description": "default light scene",
        }
        entities.extend([light_group_entity, light_scene_entity])

    # Device-specific entities
    devices = features.get("devices", [])
    for device in devices:
        if device == "computer":
            entities.extend(
                [
                    {
                        "domain": "sensor",
                        "suggested_id": f"{normalized_area_name}_pc_power",
                        "description": "PC power sensor",
                    },
                    {
                        "domain": "binary_sensor",
                        "suggested_id": f"{normalized_area_name}_pc_active",
                        "description": "PC state sensor",
                    },
                ]
            )
        elif device == "tv":
            entities.extend(
                [
                    {
                        "domain": "sensor",
                        "suggested_id": f"{normalized_area_name}_tv_power",
                        "description": "TV power sensor",
                    },
                    {
                        "domain": "binary_sensor",
                        "suggested_id": f"{normalized_area_name}_tv_active",
                        "description": "TV state sensor",
                    },
                ]
            )
        elif device in ["appliance", "bathroom", "kitchen"]:
            entities.extend(
                [
                    {
                        "domain": "sensor",
                        "suggested_id": f"{normalized_area_name}_{device}_power",
                        "description": f"{device.title()} power sensor",
                    },
                    {
                        "domain": "binary_sensor",
                        "suggested_id": f"{normalized_area_name}_{device}_active",
                        "description": f"{device.title()} state sensor",
                    },
                ]
            )

    # Add input_boolean entities
    entities.append(
        {
            "domain": "input_boolean",
            "suggested_id": f"{normalized_area_name}_occupied_override",
            "description": "occupancy override switch",
        }
    )

    # Get confirmation for each entity
    click.echo("\nPlease confirm the entity IDs for your configuration:")
    for entity_config in entities:
        # Use a more robust key extraction method
        key = entity_config["suggested_id"].split("_")[-1]

        # Ensure the key is unique
        base_key = key
        counter = 1
        while key in confirmed_entities:
            key = f"{base_key}_{counter}"
            counter += 1

        confirmed_entities[key] = confirm_entity_id(
            entity_config["domain"], entity_config["suggested_id"], entity_config["description"]
        )

    return confirmed_entities


def is_dict(value: Any) -> TypeGuard[Dict[str, Any]]:
    """Check if a value is a dictionary."""
    return isinstance(value, dict)


def is_list(value: Any) -> TypeGuard[List[Any]]:
    """Check if a value is a list."""
    return isinstance(value, list)


def extract_template_list(items: Iterable[Any]) -> List[TemplateConfigItem]:
    """Extract valid template items from an iterable."""
    return [item for item in items if is_valid_template_item(item)]


def is_valid_template_item(item: Any) -> TypeGuard[TemplateConfigItem]:
    """Check if an item is a valid template configuration item."""
    if not is_dict(item):
        return False

    valid_keys = {"binary_sensor", "sensor", "fan", "state_template"}
    for key in item:
        if key not in valid_keys:
            continue
        if not is_list(item[key]):
            return False
        if not all(is_dict(subitem) for subitem in item[key]):
            return False

    return True


def extract_template(config: Union[Dict[str, Any], List[Any]]) -> List[TemplateConfigItem]:
    """Extract template configuration from config."""
    if is_dict(config):
        return extract_template_list(config.get("template", []))
    if is_list(config):
        return extract_template_list(config)
    return []


@click.command()
@click.argument("area_name")
def main(area_name: str) -> None:
    """Generate a Home Assistant area configuration."""
    click.echo(f"Generating configuration for {area_name}")

    # Keep original area_name for display purposes but normalize for entity IDs
    features: Features = get_area_features(area_name)

    # Store both original and normalized area names in features
    features["area_name"] = area_name
    features["normalized_area_name"] = area_name.lower()

    # Get entity confirmations using normalized area name
    features["entity_ids"] = get_entity_config(area_name, features)

    config: AreaConfigType = generate_area_config(area_name, features)
    write_yaml_config(area_name.lower(), convert_area_config_to_config(config))

    click.echo(f"Configuration generated for {area_name}")


def get_area_features(area_name: str) -> Features:
    """Interactive CLI to determine area features."""
    features: Features = {"area_name": area_name, "devices": []}

    features["motion_sensor"] = click.confirm("Does this area have motion sensors?", default=True)
    features["door_sensor"] = click.confirm("Does this area have door sensors?", default=True)
    features["window_sensor"] = click.confirm("Does this area have window sensors?", default=False)
    features["temperature_sensor"] = click.confirm("Does this area have temperature sensors?", default=True)
    features["humidity_sensor"] = click.confirm("Does this area have humidity sensors?", default=False)

    # Add smart lighting as a feature
    features["smart_lighting"] = click.confirm("Does this area have smart lighting?", default=True)
    if features["smart_lighting"]:
        features["lighting_defaults"] = get_lighting_defaults()

    if click.confirm("Does this area have powered devices?", default=True):
        features["power_monitoring"] = True
        features["devices"] = get_device_types()
    else:
        features["power_monitoring"] = False
        features["devices"] = []

    features["climate_control"] = click.confirm("Does this area have climate control?", default=True)

    return features


def get_lighting_defaults() -> LightingDefaults:
    """Get default lighting configuration."""
    click.echo("\nConfigure default lighting settings:")

    # Create a LightingDefaults dictionary with explicit type hints
    defaults: LightingDefaults = {
        "brightness": click.prompt("Default brightness (0-100%)", type=int, default=50, show_default=True),
        "color_temp": click.prompt(
            "Default color temperature (warm/cool/neutral)",
            type=click.Choice(["warm", "cool", "neutral"]),
            default="neutral",
        ),
        "transition": click.prompt("Default transition time (seconds)", type=int, default=1, show_default=True),
    }

    return defaults


def get_device_types() -> List[str]:
    """Get specific devices in the area."""
    devices: List[str] = []

    device_options: DeviceOptionsType = {
        "computer": "Computer/PC setup",
        "tv": "Television/Entertainment system",
        "appliance": "Major appliances (washing machine, dishwasher, etc)",
        "bathroom": "Bathroom fixtures (shower, toilet, etc)",
        "kitchen": "Kitchen appliances (fridge, oven, etc)",
    }

    click.echo("\nSelect devices present in this area:")
    for key, desc in device_options.items():
        if click.confirm(f"Is there a {desc}?", default=False):
            devices.append(key)

    return devices


def generate_area_config(area_name: str, features: Features) -> AreaConfigType:
    """Generate the complete area configuration."""
    config: AreaConfigType = {area_name: {"template": [], "input_number": {}, "input_boolean": {}}}

    # Generate occupancy config if needed
    if features.get("motion_sensor") or features.get("door_sensor"):
        occupancy_config = occupancy.generate_occupancy_config(features)
        for item in extract_template(occupancy_config):
            config[area_name]["template"].append(convert_template_config_to_item(item))

    # Generate power monitoring config if needed
    if features.get("power_monitoring"):
        power_config = power.generate_power_config(features)
        for item in extract_template(power_config):
            config[area_name]["template"].append(convert_template_config_to_item(item))

    # Generate climate control config if needed
    if features.get("climate_control"):
        climate_config = climate.generate_climate_config(features)
        for item in extract_template(climate_config):
            config[area_name]["template"].append(convert_template_config_to_item(item))

    # Generate input controls
    input_controls = generate_input_controls(features)

    # Separate input_number and input_boolean configurations
    input_number_configs: Dict[str, InputNumberConfig] = {}
    input_boolean_configs: Dict[str, InputBooleanConfig] = {}

    for key, value in input_controls.get("input_number", {}).items():
        if all(
            k in value and (isinstance(value[k], (int, float)) or isinstance(value[k], str))
            for k in ["name", "min", "max", "step", "unit_of_measurement", "icon", "initial"]
        ):
            input_number_configs[key] = cast(InputNumberConfig, value)

    for key, value in input_controls.get("input_boolean", {}).items():
        if all(k in value and isinstance(value[k], str) for k in ["name", "icon"]):
            input_boolean_configs[key] = cast(InputBooleanConfig, value)

    config[area_name]["input_number"] = input_number_configs
    config[area_name]["input_boolean"] = input_boolean_configs

    return config


def generate_input_controls(features: Features) -> Dict[str, Dict[str, Union[InputNumberConfig, InputBooleanConfig]]]:
    """Generate input_number and input_boolean configurations."""
    controls: Dict[str, Dict[str, Union[InputNumberConfig, InputBooleanConfig]]] = {
        "input_number": {},
        "input_boolean": {},
    }

    # Get both original and normalized area names
    area_name = str(features.get("area_name", "unknown_area"))
    normalized_area_name = str(features.get("normalized_area_name", area_name.lower()))

    if features.get("power_monitoring"):
        controls["input_number"][f"{normalized_area_name}_power_threshold"] = {
            "name": f"{area_name.title()} Power Alert Threshold",
            "min": 100.0,
            "max": 1000.0,
            "step": 50.0,
            "unit_of_measurement": "W",
            "icon": "mdi:flash-alert",
            "initial": 400.0,
        }

    if features.get("climate_control"):
        controls["input_number"][f"{normalized_area_name}_temp_threshold"] = {
            "name": f"{area_name.title()} Temperature Threshold",
            "min": 19.0,
            "max": 25.0,
            "step": 0.5,
            "unit_of_measurement": "°C",
            "icon": "mdi:thermometer",
            "initial": 23.0,
        }

    # Add lighting controls if smart lighting is enabled
    if features.get("smart_lighting"):
        lighting_defaults = features.get("lighting_defaults", {})
        controls["input_number"][f"{normalized_area_name}_light_brightness"] = {
            "name": f"{area_name.title()} Light Brightness",
            "min": 0.0,
            "max": 100.0,
            "step": 5.0,
            "unit_of_measurement": "%",
            "icon": "mdi:brightness-6",
            "initial": float(lighting_defaults.get("brightness", 50)),
        }
        controls["input_number"][f"{normalized_area_name}_light_transition"] = {
            "name": f"{area_name.title()} Light Transition Time",
            "min": 0.0,
            "max": 10.0,
            "step": 0.5,
            "unit_of_measurement": "s",
            "icon": "mdi:transition",
            "initial": float(lighting_defaults.get("transition", 1)),
        }
        controls["input_boolean"][f"{normalized_area_name}_light_color_mode"] = {
            "name": f"{area_name.title()} Light Color Mode",
            "icon": "mdi:palette",
        }

    # Add boolean controls using confirmed entity IDs if available
    entity_ids = features.get("entity_ids", {})
    override_id = entity_ids.get("occupied_override", f"{normalized_area_name}_occupied_override")

    # Add occupancy override control
    controls["input_boolean"][override_id] = {
        "name": f"{area_name.title()} Manual Occupancy Override",
        "icon": "mdi:account-check",
    }

    # Add sleep mode control
    controls["input_boolean"][f"{normalized_area_name}_sleep_mode"] = {
        "name": f"{area_name.title()} Sleep Mode",
        "icon": "mdi:power-sleep",
    }

    # Add automation control
    controls["input_boolean"][f"{normalized_area_name}_automations"] = {
        "name": f"{area_name.title()} Automations",
        "icon": "mdi:robot",
    }

    return controls


if __name__ == "__main__":
    main()
