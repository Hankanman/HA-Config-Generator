# area_config_generator/devices/computer.py

from typing import cast

from ..utils.types import BinarySensorTemplate, DeviceConfig, DeviceConfigReturn, SensorTemplate
from ..utils.validation import ensure_valid_config


def generate_computer_config(area_name: str, normalized_area_name: str) -> DeviceConfigReturn:
    """Generate configuration for a computer setup.

    Args:
        area_name: The display name of the area
        normalized_area_name: The normalized (lowercase, underscored) area name

    Returns:
        Dictionary containing template configurations for computer devices

    Raises:
        ValidationError: If the generated configuration is invalid
    """
    # Create the binary sensor configuration
    pc_active: BinarySensorTemplate = {
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

    # Create the sensor configuration
    pc_status: SensorTemplate = {
        "name": f"{area_name.title()} PC Status",
        "unique_id": f"{normalized_area_name}_pc_status",
        "unit_of_measurement": "state",  # Required for SensorTemplate
        "state": "{{ states('sensor.pc_state') }}",
        "attributes": {
            "uptime": "{{ states('sensor.pc_uptime') }}",
            "cpu_usage": "{{ states('sensor.pc_cpu_usage') }}",
            "memory_usage": "{{ states('sensor.pc_memory_usage') }}",
            "gpu_temp": "{{ states('sensor.pc_gpu_temp') }}",
        },
    }

    # Create the complete device configuration
    config: DeviceConfig = {"template": [{"binary_sensor": [pc_active], "sensor": [pc_status]}]}

    # Validate the configuration before returning
    ensure_valid_config(config, "computer device config")

    return cast(DeviceConfigReturn, config)
