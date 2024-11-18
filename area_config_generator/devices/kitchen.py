# area_config_generator/devices/kitchen.py

from typing import cast

from ..utils.types import BinarySensorTemplate, DeviceConfig, DeviceConfigReturn, FanTemplate, SensorTemplate
from ..utils.validation import ensure_valid_config


def generate_kitchen_config(area_name: str, normalized_area_name: str) -> DeviceConfigReturn:
    """Generate configuration for kitchen devices.

    Args:
        area_name: The display name of the area
        normalized_area_name: The normalized (lowercase, underscored) area name

    Returns:
        Dictionary containing template configurations for kitchen devices

    Raises:
        ValidationError: If the generated configuration is invalid
    """
    # Create appliance active sensor
    appliance_active: BinarySensorTemplate = {
        "name": f"{area_name.title()} Kitchen Appliance Active",
        "unique_id": f"{normalized_area_name}_kitchen_appliance_active",
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

    # Create energy consumption sensor
    energy_consumption: SensorTemplate = {
        "name": "Kitchen Appliance Energy Consumption",
        "unique_id": f"{normalized_area_name}_kitchen_energy_consumption",
        "unit_of_measurement": "W",
        "state": "\n".join(
            [
                "{% set oven_power = states('sensor.oven_power')|float(0) %}",
                "{% set dishwasher_power = states('sensor.dishwasher_power')|float(0) %}",
                "{% set refrigerator_power = states('sensor.refrigerator_power')|float(0) %}",
                "{{ (oven_power + dishwasher_power + refrigerator_power)|round(2) }}",
            ]
        ),
        "attributes": {
            "refrigerator_temp": "{{ states('sensor.refrigerator_temperature')|float(0) }}",
            "oven_state": "{{ states('sensor.oven_state') }}",
            "dishwasher_state": "{{ states('sensor.dishwasher_state') }}",
        },
    }

    # Create kitchen ventilation fan
    kitchen_fan: FanTemplate = {
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

    # Create appliance status sensor
    appliance_status: SensorTemplate = {
        "name": f"{area_name.title()} Kitchen Appliance Status",
        "unique_id": f"{normalized_area_name}_kitchen_appliance_status",
        "unit_of_measurement": "state",
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

    # Create the complete device configuration
    config: DeviceConfig = {
        "template": [
            {"binary_sensor": [appliance_active], "sensor": [energy_consumption, appliance_status], "fan": [kitchen_fan]}
        ]
    }

    # Validate the configuration before returning
    ensure_valid_config(config, "kitchen device config")

    return cast(DeviceConfigReturn, config)
