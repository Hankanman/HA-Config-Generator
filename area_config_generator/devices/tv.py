# area_config_generator/devices/tv.py

from typing import cast

from ..utils.types import BinarySensorTemplate, DeviceConfig, DeviceConfigReturn, SensorTemplate
from ..utils.validation import ensure_valid_config


def generate_tv_config(area_name: str, normalized_area_name: str) -> DeviceConfigReturn:
    """Generate configuration for a TV setup.

    Args:
        area_name: The display name of the area
        normalized_area_name: The normalized (lowercase, underscored) area name

    Returns:
        Dictionary containing template configurations for TV devices

    Raises:
        ValidationError: If the generated configuration is invalid
    """
    # Create TV active sensor
    tv_active: BinarySensorTemplate = {
        "name": f"{area_name.title()} TV Active",
        "unique_id": f"{normalized_area_name}_tv_active",
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

    # Create TV status sensor
    tv_status: SensorTemplate = {
        "name": f"{area_name.title()} TV Status",
        "unique_id": f"{normalized_area_name}_tv_status",
        "unit_of_measurement": "state",
        "state": "{{ states('sensor.tv_state') }}",
        "attributes": {
            "input_source": "{{ states('sensor.tv_input_source') }}",
            "hdmi_connected": "{{ state_attr('sensor.tv_hdmi', 'connected_devices')|default([]) }}",
        },
    }

    # Create TV power state sensor
    power_state: SensorTemplate = {
        "name": f"{area_name.title()} TV Power State",
        "unique_id": f"{normalized_area_name}_tv_power_state",
        "unit_of_measurement": "state",
        "state": "\n".join(
            [
                "{% set power = states('sensor.tv_power')|float(0) %}",
                "{% if power > 50 %}on{% elif power > 10 %}standby{% else %}off{% endif %}",
            ]
        ),
    }

    # Create the complete device configuration
    config: DeviceConfig = {"template": [{"binary_sensor": [tv_active], "sensor": [tv_status, power_state]}]}

    # Validate the configuration before returning
    ensure_valid_config(config, "tv device config")

    return cast(DeviceConfigReturn, config)
