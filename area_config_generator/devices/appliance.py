# area_config_generator/devices/appliance.py
"""Configuration generator for major appliances."""

from typing import Any, Dict, List, Union, cast


def generate_appliance_config(area_name: str, appliance_type: str) -> Dict[str, List[Dict[str, Any]]]:
    """Generate configuration for major appliances."""
    templates: Dict[str, Dict[str, Union[str, int, List[str]]]] = {
        "washing_machine": {
            "name": "Washing Machine",
            "power_threshold": 10,
            "states": ["idle", "washing", "spinning", "finished"],
            "attributes": ["cycle", "time_remaining", "total_power"],
        },
        "dishwasher": {
            "name": "Dishwasher",
            "power_threshold": 10,
            "states": ["idle", "washing", "drying", "finished"],
            "attributes": ["cycle", "time_remaining", "total_power"],
        },
        "dryer": {
            "name": "Dryer",
            "power_threshold": 10,
            "states": ["idle", "drying", "cooling", "finished"],
            "attributes": ["cycle", "time_remaining", "total_power"],
        },
    }

    template = templates.get(
        appliance_type,
        {
            "name": "Generic Appliance",
            "power_threshold": 10,
            "states": ["idle", "running", "finished"],
            "attributes": ["time_active", "total_power"],
        },
    )

    # Safely get attributes with a default empty list
    attributes_list: List[str] = cast(List[str], template.get("attributes", []))

    # Create attributes dictionary
    attributes_dict: Dict[str, str] = {}
    for attr in attributes_list:
        attributes_dict[attr] = f"{{{{ state_attr('sensor.{area_name}_{appliance_type}_state', '{attr}') }}}}"

    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{template['name']} Active",
                        "unique_id": f"{area_name}_{appliance_type}_active",
                        "device_class": "running",
                        "state": (
                            f"{{{{ states('sensor.{area_name}_{appliance_type}_power')|"
                            f"float(0) > {template['power_threshold']} }}}}"
                        ),
                        "attributes": {
                            "state": f"{{{{ states('sensor.{area_name}_{appliance_type}_state') }}}}",
                            "run_time": f"{{{{ states('sensor.{area_name}_{appliance_type}_run_time') }}}}",
                        },
                    }
                ]
            }
        ],
        "sensor": [
            {
                "name": f"{template['name']} State",
                "unique_id": f"{area_name}_{appliance_type}_state",
                "state": "\n".join(
                    [
                        f"{{% set power = states('sensor.{area_name}_{appliance_type}_power')|float(0) %}}",
                        # type: ignore[list-item]
                        "{% set states = " + str(template["states"]) + " %}",
                        "{% if power == 0 %}",
                        "  {{ states[0] }}",  # idle
                        "{% elif power > " + str(template["power_threshold"]) + " %}",
                        "  {{ states[1] }}",  # running/washing/drying
                        "{% else %}",
                        "  {{ states[-1] }}",  # finished
                        "{% endif %}",
                    ]
                ),
                "attributes": attributes_dict,
            }
        ],
        "fan": [
            {
                "platform": "template",
                "fans": {
                    f"{area_name}_{appliance_type}_ventilation": {
                        "friendly_name": f"{template['name']} Ventilation",
                        "value_template": f"{{{{ states('switch.{area_name}_{appliance_type}_fan') }}}}",
                        "speed_template": f"{{{{ states('sensor.{area_name}_{appliance_type}_fan_speed') }}}}",
                        "turn_on": {
                            "service": "switch.turn_on",
                            "entity_id": f"switch.{area_name}_{appliance_type}_fan",
                        },
                        "turn_off": {
                            "service": "switch.turn_off",
                            "entity_id": f"switch.{area_name}_{appliance_type}_fan",
                        },
                        "set_speed": {
                            "service": "input_number.set_value",
                            "entity_id": f"input_number.{area_name}_{appliance_type}_fan_speed",
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
                        "name": f"{template['name']} Energy Efficiency",
                        "unique_id": f"{area_name}_{appliance_type}_energy_efficiency",
                        "state": "\n".join(
                            [
                                f"{{% set power = states('sensor.{area_name}_{appliance_type}_power')|float(0) %}}",
                                f"{{% set run_time = states('sensor.{area_name}_{appliance_type}_run_time')|float(0) %}}",
                                "{% if run_time > 0 %}",
                                "  {{ (power / run_time)|round(2) }}",
                                "{% else %}",
                                "  0",
                                "{% endif %}",
                            ]
                        ),
                        "unit_of_measurement": "W/min",
                    }
                ]
            }
        ],
    }
