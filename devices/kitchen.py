# area_config_generator/devices/kitchen.py
"""Configuration generator for kitchen appliances."""

from typing import Dict, List


def generate_kitchen_config(area_name: str) -> Dict:
    """Generate configuration for kitchen appliances."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": "Cooking Active",
                        "unique_id": f"{area_name}_cooking_active",
                        "device_class": "heat",
                        "state": "\n".join(
                            [
                                "{% set hob_power = states('sensor.kitchen_hob_power')|float(0) %}",
                                "{% set oven_power = states('sensor.kitchen_oven_power')|float(0) %}",
                                "{% set temp_rise = states('sensor.kitchen_temperature_rise')|float(0) %}",
                                "{{ hob_power > 100 or oven_power > 100 or temp_rise > 2 }}",
                            ]
                        ),
                        "attributes": {
                            "hob_power": "{{ states('sensor.kitchen_hob_power')|float(0) }}",
                            "oven_power": "{{ states('sensor.kitchen_oven_power')|float(0) }}",
                            "temperature_rise": "{{ states('sensor.kitchen_temperature_rise')|float(0) }}",
                        },
                    },
                    {
                        "name": "Kettle Active",
                        "unique_id": f"{area_name}_kettle_active",
                        "device_class": "power",
                        "state": "{{ states('sensor.kitchen_kettle_power')|float(0) > 50 }}",
                    },
                    {
                        "name": "Fridge State",
                        "unique_id": f"{area_name}_fridge_state",
                        "device_class": "cold",
                        "state": "\n".join(
                            [
                                "{% set power = states('sensor.kitchen_fridge_power')|float(0) %}",
                                "{% set temp = states('sensor.kitchen_fridge_temp')|float(4) %}",
                                "{{ power > 0 and temp < 8 }}",
                            ]
                        ),
                        "attributes": {
                            "power_draw": "{{ states('sensor.kitchen_fridge_power')|float(0) }}",
                            "temperature": "{{ states('sensor.kitchen_fridge_temp')|float(4) }}",
                            "door_open": "{{ is_state('binary_sensor.kitchen_fridge_door', 'on') }}",
                        },
                    },
                ]
            }
        ],
        "sensor": [
            {
                "name": "Kitchen Temperature Rise",
                "unique_id": f"{area_name}_temperature_rise",
                "state": "\n".join(
                    [
                        "{% set current = states('sensor.kitchen_temperature')|float(20) %}",
                        "{% set average = states('sensor.kitchen_average_temperature')|float(20) %}",
                        "{{ (current - average)|round(1) }}",
                    ]
                ),
                "device_class": "temperature",
                "unit_of_measurement": "°C",
            }
        ],
    }
