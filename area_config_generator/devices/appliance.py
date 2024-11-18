# area_config_generator/devices/appliance.py

from ..utils.types import BinarySensorTemplate, DeviceConfig, DeviceConfigReturn, FanTemplate, SensorTemplate
from ..utils.validation import ensure_valid_config


def generate_appliance_config(
    area_name: str, normalized_area_name: str, appliance_type: str = "generic"
) -> DeviceConfigReturn:
    """Generate configuration for major appliances.

    Args:
        area_name: The display name of the area
        normalized_area_name: The normalized (lowercase, underscored) area name
        appliance_type: The type of appliance (washing_machine, dishwasher, dryer, etc.)

    Returns:
        Dictionary containing template configurations for appliance devices

    Raises:
        ValidationError: If the generated configuration is invalid
    """
    # Create appliance active sensor
    appliance_active: BinarySensorTemplate = {
        "name": f"{area_name.title()} {appliance_type.title()} Active",
        "unique_id": f"{normalized_area_name}_{appliance_type}_active",
        "device_class": "running",
        "state": f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_power')|float(0) > 10 }}}}",
        "attributes": {"power_draw": (f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_power')|float(0) }}}}")},
    }

    # Create state sensor
    state_sensor: SensorTemplate = {
        "name": f"{area_name.title()} {appliance_type.title()} State",
        "unique_id": f"{normalized_area_name}_{appliance_type}_state",
        "unit_of_measurement": "state",
        "state": "\n".join(
            [
                f"{{% set power = states('sensor.{normalized_area_name}_{appliance_type}_power')|float(0) %}}",
                "{% if power > 50 %}running{% elif power > 10 %}standby{% else %}off{% endif %}",
            ]
        ),
    }

    # Create fan configuration
    fan_config: FanTemplate = {
        "platform": "template",
        "fans": {
            f"{normalized_area_name}_{appliance_type}_fan": {
                "friendly_name": f"{area_name.title()} {appliance_type.title()} Fan",
                "value_template": (f"{{{{ states('switch.{normalized_area_name}_{appliance_type}_fan') }}}}"),
                "speed_template": (f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_fan_speed') }}}}"),
                "turn_on": {
                    "service": "switch.turn_on",
                    "entity_id": f"switch.{normalized_area_name}_{appliance_type}_fan",
                },
                "turn_off": {
                    "service": "switch.turn_off",
                    "entity_id": f"switch.{normalized_area_name}_{appliance_type}_fan",
                },
                "set_speed": {
                    "service": "input_number.set_value",
                    "entity_id": (f"input_number.{normalized_area_name}_{appliance_type}_fan_speed"),
                    "data_template": {"value": "{{ speed }}"},
                },
                "speeds": ["low", "medium", "high"],
            }
        },
    }

    # Create the complete device configuration
    config: DeviceConfig = {
        "template": [
            {
                "binary_sensor": [appliance_active],
                "sensor": [state_sensor],
                "fan": [fan_config],
            }
        ]
    }

    # Validate the configuration before returning
    ensure_valid_config(config, f"{appliance_type} device config")

    return config
