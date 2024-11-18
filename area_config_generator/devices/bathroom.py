# area_config_generator/devices/bathroom.py

from typing import cast

from ..utils.types import BinarySensorTemplate, DeviceConfig, DeviceConfigReturn, FanTemplate, SensorTemplate
from ..utils.validation import ensure_valid_config


def generate_bathroom_config(area_name: str, normalized_area_name: str) -> DeviceConfigReturn:
    """Generate configuration for bathroom devices.

    Args:
        area_name: The display name of the area
        normalized_area_name: The normalized (lowercase, underscored) area name

    Returns:
        Dictionary containing template configurations for bathroom devices

    Raises:
        ValidationError: If the generated configuration is invalid
    """
    # Create humidity alert sensor
    humidity_alert: BinarySensorTemplate = {
        "name": f"{area_name.title()} Humidity Alert",
        "unique_id": f"{normalized_area_name}_humidity_alert",
        "device_class": "moisture",
        "state": "\n".join(
            [
                f"{{% set humidity = states('sensor.{normalized_area_name}_humidity')|float(0) %}}",
                "{{ humidity > 70 }}",
            ]
        ),
        "attributes": {
            "humidity": f"{{{{ states('sensor.{normalized_area_name}_humidity')|float(0) }}}}",
            "temperature": f"{{{{ states('sensor.{normalized_area_name}_temperature')|float(0) }}}}",
        },
    }

    # Create fan configuration
    bathroom_fan: FanTemplate = {
        "platform": "template",
        "fans": {
            "bathroom_fan": {
                "friendly_name": f"{area_name.title()} Fan",
                "value_template": f"{{{{ states('switch.{normalized_area_name}_fan') }}}}",
                "speed_template": f"{{{{ states('sensor.{normalized_area_name}_fan_speed') }}}}",
                "turn_on": {
                    "service": "switch.turn_on",
                    "entity_id": f"switch.{normalized_area_name}_fan",
                },
                "turn_off": {
                    "service": "switch.turn_off",
                    "entity_id": f"switch.{normalized_area_name}_fan",
                },
                "set_speed": {
                    "service": "input_number.set_value",
                    "entity_id": f"input_number.{normalized_area_name}_fan_speed",
                    "data_template": {"value": "{{ speed }}"},
                },
                "speeds": ["low", "medium", "high"],
            }
        },
    }

    # Create humidity change sensor
    humidity_change: SensorTemplate = {
        "name": f"{area_name.title()} Humidity Change",
        "unique_id": f"{normalized_area_name}_humidity_change",
        "unit_of_measurement": "%",
        "state": "\n".join(
            [
                f"{{% set current = states('sensor.{normalized_area_name}_humidity')|float(50) %}}",
                f"{{% set average = states('sensor.{normalized_area_name}_average_humidity')|float(50) %}}",
                "{{ ((current - average) / average * 100)|round(1) }}",
            ]
        ),
        "attributes": {
            "fan_speed": f"{{{{ states('sensor.{normalized_area_name}_fan_speed')|int(0) }}}}",
            "is_running": f"{{{{ is_state('fan.{normalized_area_name}_ventilation', 'on') }}}}",
        },
    }

    # Create comfort level sensor
    comfort_level: SensorTemplate = {
        "name": f"{area_name.title()} Comfort Level",
        "unique_id": f"{normalized_area_name}_comfort_level",
        "unit_of_measurement": "state",
        "state": "\n".join(
            [
                f"{{% set humidity = states('sensor.{normalized_area_name}_humidity')|float(0) %}}",
                f"{{% set temperature = states('sensor.{normalized_area_name}_temperature')|float(0) %}}",
                "{% if humidity > 70 and temperature > 25 %}"
                "uncomfortable"
                "{% elif humidity > 60 %}"
                "moderate"
                "{% else %}"
                "comfortable"
                "{% endif %}",
            ]
        ),
    }

    # Create the complete device configuration
    config: DeviceConfig = {
        "template": [{"binary_sensor": [humidity_alert], "fan": [bathroom_fan], "sensor": [humidity_change, comfort_level]}]
    }

    # Validate the configuration before returning
    ensure_valid_config(config, "bathroom device config")

    return cast(DeviceConfigReturn, config)
