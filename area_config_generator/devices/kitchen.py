# area_config_generator/devices/kitchen.py
"""Configuration generator for kitchen devices."""

from ..utils.types import AreaName, ConfigType


def generate_kitchen_config(area_name: AreaName) -> ConfigType:
    """Generate configuration for kitchen devices."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{area_name.title()} Kitchen Appliance Active",
                        "unique_id": f"{area_name}_kitchen_appliance_active",
                        "device_class": "power",
                        "state": "\n".join(
                            [
                                "{% set oven_power = states('sensor.oven_power')|float(0) %}",
                                "{% set dishwasher_power = states('sensor.dishwasher_power')|float(0) %}",
                                "{{ oven_power > 50 or dishwasher_power > 50 }}",
                            ]
                        ),
                        "attributes": {
                            "oven_power": "{{ states('sensor.oven_power')|float(0) }}",
                            "dishwasher_power": "{{ states('sensor.dishwasher_power')|float(0) }}",
                        },
                    }
                ]
            }
        ],
        "sensor": [
            {
                "name": "Kitchen Appliance Energy Consumption",
                "unique_id": f"{area_name}_kitchen_energy_consumption",
                "state": "\n".join(
                    [
                        "{% set oven_power = states('sensor.oven_power')|float(0) %}",
                        "{% set dishwasher_power = states('sensor.dishwasher_power')|float(0) %}",
                        "{% set refrigerator_power = states('sensor.refrigerator_power')|float(0) %}",
                        "{{ (oven_power + dishwasher_power + refrigerator_power)|round(2) }}",
                    ]
                ),
                "unit_of_measurement": "W",
                "device_class": "power",
                "attributes": {
                    "refrigerator_temp": "{{ states('sensor.refrigerator_temperature')|float(0) }}",
                    "oven_state": "{{ states('sensor.oven_state') }}",
                    "dishwasher_state": "{{ states('sensor.dishwasher_state') }}",
                },
            }
        ],
        "fan": [
            {
                "platform": "template",
                "fans": {
                    "kitchen_ventilation": {
                        "friendly_name": "Kitchen Ventilation",
                        "value_template": "{{ states('switch.kitchen_fan') }}",
                        "speed_template": "{{ states('sensor.kitchen_fan_speed') }}",
                        "turn_on": {
                            "service": "switch.turn_on",
                            "entity_id": "switch.kitchen_fan",
                        },
                        "turn_off": {
                            "service": "switch.turn_off",
                            "entity_id": "switch.kitchen_fan",
                        },
                        "set_speed": {
                            "service": "input_number.set_value",
                            "entity_id": "input_number.kitchen_fan_speed",
                            "data_template": {"value": "{{ speed }}"},
                        },
                        "speeds": ["low", "medium", "high"],
                    }
                },
            }
        ],
        "state_template": [
            {
                "sensor": [
                    {
                        "name": f"{area_name.title()} Kitchen Appliance Status",
                        "unique_id": f"{area_name}_kitchen_appliance_status",
                        "state": "\n".join(
                            [
                                "{% set oven_state = states('sensor.oven_state') %}",
                                "{% set dishwasher_state = states('sensor.dishwasher_state') %}",
                                "{% if oven_state == 'on' and dishwasher_state == 'on' %}"
                                "high_activity"
                                "{% elif oven_state == 'on' or dishwasher_state == 'on' %}"
                                "moderate_activity"
                                "{% else %}"
                                "idle"
                                "{% endif %}",
                            ]
                        ),
                    }
                ]
            }
        ],
    }
