# area_config_generator/devices/appliance.py

from typing import Dict, List, cast

from ..utils.types import BinarySensorTemplate, DeviceConfig, DeviceConfigReturn, FanTemplate, SensorTemplate
from ..utils.validation import ensure_valid_config


def generate_appliance_config(area_name: str, normalized_area_name: str, appliance_type: str) -> DeviceConfigReturn:
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
    # Define appliance templates
    templates: Dict[str, Dict[str, List[str]]] = {
        "washing_machine": {
            "states": ["idle", "washing", "spinning", "finished"],
            "attributes": ["cycle", "time_remaining", "total_power"],
        },
        "dishwasher": {
            "states": ["idle", "washing", "drying", "finished"],
            "attributes": ["cycle", "time_remaining", "total_power"],
        },
        "dryer": {
            "states": ["idle", "drying", "cooling", "finished"],
            "attributes": ["cycle", "time_remaining", "total_power"],
        },
    }

    # Get template or use default
    template = templates.get(
        appliance_type,
        {
            "states": ["idle", "running", "finished"],
            "attributes": ["time_active", "total_power"],
        },
    )

    # Create binary sensor configuration
    appliance_active: BinarySensorTemplate = {
        "name": f"{area_name.title()} {appliance_type.title()} Active",
        "unique_id": f"{normalized_area_name}_{appliance_type}_active",
        "device_class": "running",
        "state": (f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_power')|" f"float(0) > 10 }}}}"),
        "attributes": {
            "state": f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_state') }}}}",
            "run_time": f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_run_time') }}}}",
        },
    }

    # Create state sensor configuration
    state_sensor: SensorTemplate = {
        "name": f"{area_name.title()} {appliance_type.title()} State",
        "unique_id": f"{normalized_area_name}_{appliance_type}_state",
        "unit_of_measurement": "state",
        "state": "\n".join(
            [
                f"{{% set power = states('sensor.{normalized_area_name}_{appliance_type}_power')|float(0) %}}",
                f"{{% set states = {template['states']} %}}",
                "{% if power == 0 %}",
                "  {{ states[0] }}",  # idle
                "{% elif power > 10 %}",
                "  {{ states[1] }}",  # running/washing/drying
                "{% else %}",
                "  {{ states[-1] }}",  # finished
                "{% endif %}",
            ]
        ),
    }

    # Create energy efficiency sensor configuration
    energy_sensor: SensorTemplate = {
        "name": f"{area_name.title()} {appliance_type.title()} Energy Efficiency",
        "unique_id": f"{normalized_area_name}_{appliance_type}_energy_efficiency",
        "unit_of_measurement": "W/min",
        "state": "\n".join(
            [
                f"{{% set power = states('sensor.{normalized_area_name}_{appliance_type}_power')|float(0) %}}",
                f"{{% set run_time = states('sensor.{normalized_area_name}_{appliance_type}_run_time')|float(0) %}}",
                "{% if run_time > 0 %}",
                "  {{ (power / run_time)|round(2) }}",
                "{% else %}",
                "  0",
                "{% endif %}",
            ]
        ),
    }

    # Create fan configuration
    fan_config: FanTemplate = {
        "platform": "template",
        "fans": {
            f"{normalized_area_name}_{appliance_type}_ventilation": {
                "friendly_name": f"{area_name.title()} {appliance_type.title()} Ventilation",
                "value_template": f"{{{{ states('switch.{normalized_area_name}_{appliance_type}_fan') }}}}",
                "speed_template": f"{{{{ states('sensor.{normalized_area_name}_{appliance_type}_fan_speed') }}}}",
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
                    "entity_id": f"input_number.{normalized_area_name}_{appliance_type}_fan_speed",
                    "data_template": {"value": "{{ speed }}"},
                },
                "speeds": ["low", "medium", "high"],
            }
        },
    }

    # Create the complete device configuration
    config: DeviceConfig = {
        "template": [{"binary_sensor": [appliance_active], "sensor": [state_sensor, energy_sensor], "fan": [fan_config]}]
    }

    # Validate the configuration before returning
    ensure_valid_config(config, f"{appliance_type} device config")

    return cast(DeviceConfigReturn, config)
