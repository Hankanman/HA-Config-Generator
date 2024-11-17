# area_config_generator/devices/bathroom.py
"""Configuration generator for bathroom fixtures."""

from typing import Dict, List


def generate_bathroom_config(area_name: str) -> Dict:
    """Generate configuration for bathroom fixtures."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": "Shower Active",
                        "unique_id": f"{area_name}_shower_active",
                        "device_class": "moisture",
                        "state": "\n".join(
                            [
                                "{% set humidity_change = states('sensor.bathroom_humidity_change')|float(0) %}",
                                "{% set water_flow = states('sensor.bathroom_water_flow')|float(0) %}",
                                "{{ humidity_change > 20 or water_flow > 0 }}",
                            ]
                        ),
                        "attributes": {
                            "humidity_change": "{{ states('sensor.bathroom_humidity_change')|float(0) }}",
                            "water_flow": "{{ states('sensor.bathroom_water_flow')|float(0) }}",
                            "steam_detected": "{{ states('sensor.bathroom_humidity_change')|float(0) > 20 }}",
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
                    "current_humidity": "{{ states('sensor.bathroom_humidity')|float(50) }}",
                    "average_humidity": "{{ states('sensor.bathroom_average_humidity')|float(50) }}",
                },
            }
        ],
    }
