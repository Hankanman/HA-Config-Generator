# area_config_generator/devices/appliance.py
"""Configuration generator for major appliances."""

from typing import Dict, List


def generate_appliance_config(area_name: str, appliance_type: str) -> Dict:
    """Generate configuration for major appliances."""
    templates = {
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

    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{template['name']} Active",
                        "unique_id": f"{area_name}_{appliance_type}_active",
                        "device_class": "running",
                        "state": f"{{{{ states('sensor.{area_name}_{appliance_type}_power')|float(0) > {template['power_threshold']} }}}}",
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
                "attributes": {
                    attr: f"{{{{ state_attr('sensor.{area_name}_{appliance_type}_state', '{attr}') }}}}"
                    for attr in template["attributes"]
                },
            }
        ],
    }
