# area_config_generator/devices/bathroom.py
"""Configuration generator for bathroom devices."""

from ..utils.types import AreaName, ConfigType


def generate_bathroom_config(area_name: AreaName) -> ConfigType:
    """Generate configuration for bathroom devices."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{area_name.title()} Bathroom Humidity Alert",
                        "unique_id": f"{area_name}_bathroom_humidity_alert",
                        "device_class": "moisture",
                        "state": "\n".join(
                            [
                                "{% set humidity = states('sensor.bathroom_humidity')|float(0) %}",
                                "{{ humidity > 70 }}",
                            ]
                        ),
                        "attributes": {
                            "humidity": "{{ states('sensor.bathroom_humidity')|float(0) }}",
                            "temperature": "{{ states('sensor.bathroom_temperature')|float(0) }}",
                        },
                    }
                ]
            }
        ],
        "fan": [
            {
                "platform": "template",
                "fans": {
                    "bathroom_fan": {
                        "friendly_name": "Bathroom Fan",
                        "value_template": "{{ states('switch.bathroom_fan') }}",
                        "speed_template": "{{ states('sensor.bathroom_fan_speed') }}",
                        "turn_on": {
                            "service": "switch.turn_on",
                            "entity_id": "switch.bathroom_fan",
                        },
                        "turn_off": {
                            "service": "switch.turn_off",
                            "entity_id": "switch.bathroom_fan",
                        },
                        "set_speed": {
                            "service": "input_number.set_value",
                            "entity_id": "input_number.bathroom_fan_speed",
                            "data_template": {"value": "{{ speed }}"},
                        },
                        "speeds": ["low", "medium", "high"],
                    }
                },
            }
        ],
        "sensor": [
            {
                "name": "Bathroom Humidity Change",
                "unique_id": f"{area_name}_humidity_change",
                "state": "\n".join(
                    [
                        "{% set current = states('sensor.bathroom_humidity')|float(50) %}",
                        "{% set average = states('sensor.bathroom_average_humidity')|float(50) %}",
                        "{{ ((current - average) / average * 100)|round(1) }}",
                    ]
                ),
                "device_class": "humidity",
                "unit_of_measurement": "%",
                "attributes": {
                    "fan_speed": "{{ states('sensor.bathroom_fan_speed')|int(0) }}",
                    "is_running": "{{ is_state('fan.bathroom_ventilation', 'on') }}",
                },
            }
        ],
        "state_template": [
            {
                "sensor": [
                    {
                        "name": f"{area_name.title()} Bathroom Comfort Level",
                        "unique_id": f"{area_name}_bathroom_comfort_level",
                        "state": "\n".join(
                            [
                                "{% set humidity = states('sensor.bathroom_humidity')|float(0) %}",
                                "{% set temperature = states('sensor.bathroom_temperature')|float(0) %}",
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
                ]
            }
        ],
    }
