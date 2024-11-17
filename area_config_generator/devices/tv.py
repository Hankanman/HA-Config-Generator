# area_config_generator/devices/tv.py
"""Configuration generator for TV setups."""

from utils.types import AreaName, ConfigType


def generate_tv_config(area_name: AreaName) -> ConfigType:
    """Generate configuration for a TV setup."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{area_name.title()} TV Active",
                        "unique_id": f"{area_name}_tv_active",
                        "device_class": "power",
                        "state": "\n".join(
                            [
                                "{% set power = states('sensor.tv_power')|float(0) %}",
                                "{{ power > 10 }}",
                            ]
                        ),
                        "attributes": {
                            "power_draw": "{{ states('sensor.tv_power')|float(0) }}",
                            "current_channel": "{{ states('sensor.tv_channel') }}",
                            "volume": "{{ states('sensor.tv_volume')|int(0) }}",
                        },
                    }
                ]
            }
        ],
        "sensor": [
            {
                "name": f"{area_name.title()} TV Status",
                "unique_id": f"{area_name}_tv_status",
                "state": "{{ states('sensor.tv_state') }}",
                "attributes": {
                    "input_source": "{{ states('sensor.tv_input_source') }}",
                    "hdmi_connected": "{{ state_attr('sensor.tv_hdmi', 'connected_devices')|default([]) }}",
                },
            }
        ],
        "state_template": [
            {
                "sensor": [
                    {
                        "name": f"{area_name.title()} TV Power State",
                        "unique_id": f"{area_name}_tv_power_state",
                        "state": "\n".join(
                            [
                                "{% set power = states('sensor.tv_power')|float(0) %}",
                                "{% if power > 50 %}on{% elif power > 10 %}standby{% else %}off{% endif %}",
                            ]
                        ),
                    }
                ]
            }
        ],
    }
