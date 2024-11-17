# area_config_generator/devices/tv.py
"""Configuration generator for TV/entertainment systems."""

from typing import Dict, List


def generate_tv_config(area_name: str) -> Dict:
    """Generate configuration for a TV/entertainment setup."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{area_name.title()} TV Active",
                        "unique_id": f"{area_name}_tv_active",
                        "device_class": "running",
                        "state": "\n".join(
                            [
                                "{% set tv_state = states('media_player.tv') %}",
                                "{% set power = states('sensor.tv_power')|float(0) %}",
                                "{{ tv_state in ['playing', 'paused'] or power > 20 }}",
                            ]
                        ),
                        "attributes": {
                            "source": "{{ state_attr('media_player.tv', 'source') }}",
                            "media_title": "{{ state_attr('media_player.tv', 'media_title') }}",
                            "power_state": "{{ 'standby' if states('sensor.tv_power')|float(0) < 20 else 'on' }}",
                        },
                    }
                ]
            }
        ],
        "media_player": [
            {
                "platform": "universal",
                "name": f"{area_name.title()} TV",
                "unique_id": f"{area_name}_tv",
                "children": [
                    f"media_player.{area_name}_tv_native",
                    f"media_player.{area_name}_tv_cast",
                    f"media_player.{area_name}_tv_shield",
                ],
                "state_template": "\n".join(
                    [
                        "{% if is_state('binary_sensor."
                        + f"{area_name}_tv_active"
                        + "', 'on') %}",
                        "  {% if is_state_attr('media_player."
                        + f"{area_name}_tv_shield"
                        + "', 'source', 'playing') %}",
                        "    playing",
                        "  {% else %}",
                        "    on",
                        "  {% endif %}",
                        "{% else %}",
                        "  off",
                        "{% endif %}",
                    ]
                ),
            }
        ],
    }
