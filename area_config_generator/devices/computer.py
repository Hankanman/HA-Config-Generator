# area_config_generator/devices/computer.py
"""Configuration generator for computer/PC setups."""

from typing import Any, Dict, List


def generate_computer_config(area_name: str, normalized_area_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """Generate configuration for a computer setup."""
    return {
        "template": [
            {
                "binary_sensor": [
                    {
                        "name": f"{area_name.title()} PC Active",
                        "unique_id": f"{normalized_area_name}_pc_active",
                        "device_class": "power",
                        "state": "\n".join(
                            [
                                "{% set idle_time = states('sensor.pc_idle_time')|int(0) %}",
                                "{% set power = states('sensor.pc_power')|float(0) %}",
                                "{{ idle_time < 300 or power > 50 }}",
                            ]
                        ),
                        "attributes": {
                            "idle_time": "{{ states('sensor.pc_idle_time')|int(0) }}",
                            "power_draw": "{{ states('sensor.pc_power')|float(0) }}",
                            "apps_running": "{{ state_attr('sensor.pc_status', 'running_apps')|default([]) }}",
                        },
                    }
                ]
            }
        ],
        "sensor": [
            {
                "name": f"{area_name.title()} PC Status",
                "unique_id": f"{normalized_area_name}_pc_status",
                "state": "{{ states('sensor.pc_state') }}",
                "attributes": {
                    "uptime": "{{ states('sensor.pc_uptime') }}",
                    "cpu_usage": "{{ states('sensor.pc_cpu_usage') }}",
                    "memory_usage": "{{ states('sensor.pc_memory_usage') }}",
                    "gpu_temp": "{{ states('sensor.pc_gpu_temp') }}",
                },
            }
        ],
    }
