# area_config_generator/cli/input_config.py

from typing import Dict, Union

from ..utils.types import Features, InputBooleanConfig, InputNumberConfig


def generate_input_controls(features: Features) -> Dict[str, Dict[str, Union[InputNumberConfig, InputBooleanConfig]]]:
    """Generate input_number and input_boolean configurations.

    Args:
        features: Feature configuration containing device list and area details

    Returns:
        Dictionary of input controls configuration
    """
    controls: Dict[str, Dict[str, Union[InputNumberConfig, InputBooleanConfig]]] = {
        "input_number": {},
        "input_boolean": {},
    }

    # Get both original and normalized area names
    area_name = str(features.get("area_name", "unknown_area"))
    normalized_area_name = str(features.get("normalized_area_name", area_name.lower()))

    # Generate power monitoring controls
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

    # Generate climate controls
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

    # Generate lighting controls
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

    # Generate device-specific controls
    for device in features.get("devices", []):
        if device == "computer":
            controls["input_boolean"][f"{normalized_area_name}_pc_power_management"] = {
                "name": f"{area_name.title()} PC Power Management",
                "icon": "mdi:desktop-classic",
            }
        elif device == "tv":
            controls["input_boolean"][f"{normalized_area_name}_tv_power_management"] = {
                "name": f"{area_name.title()} TV Power Management",
                "icon": "mdi:television",
            }
        elif device == "appliance":
            controls["input_boolean"][f"{normalized_area_name}_appliance_monitoring"] = {
                "name": f"{area_name.title()} Appliance Monitoring",
                "icon": "mdi:washing-machine",
            }
            controls["input_number"][f"{normalized_area_name}_appliance_power_threshold"] = {
                "name": f"{area_name.title()} Appliance Power Threshold",
                "min": 50.0,
                "max": 2000.0,
                "step": 50.0,
                "unit_of_measurement": "W",
                "icon": "mdi:flash-alert",
                "initial": 200.0,
            }

    # Add boolean controls using confirmed entity IDs if available
    entity_ids = features.get("entity_ids", {})
    override_id = entity_ids.get("occupied_override", f"input_boolean.{normalized_area_name}_occupied_override")

    # Add occupancy override control
    controls["input_boolean"][override_id.split(".")[-1]] = {
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

    # Add humidity controls if needed
    if features.get("humidity_sensor"):
        controls["input_number"][f"{normalized_area_name}_humidity_threshold"] = {
            "name": f"{area_name.title()} Humidity Threshold",
            "min": 30.0,
            "max": 80.0,
            "step": 1.0,
            "unit_of_measurement": "%",
            "icon": "mdi:water-percent",
            "initial": 60.0,
        }

    return controls
