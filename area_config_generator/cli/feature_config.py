# area_config_generator/cli/feature_config.py

from typing import Dict, List

import click

from ..devices.manager import DeviceManager
from ..utils.types import Features, LightingDefaults


def get_area_features(area_name: str, device_manager: DeviceManager) -> Features:
    """Interactive CLI to determine area features.

    Args:
        area_name: The name of the area
        device_manager: The device manager instance

    Returns:
        Dictionary of features for the area
    """
    features: Features = {"area_name": area_name, "devices": []}

    features["motion_sensor"] = click.confirm("Does this area have motion sensors?", default=True)

    features["door_sensor"] = click.confirm("Does this area have door sensors?", default=True)

    features["window_sensor"] = click.confirm("Does this area have window sensors?", default=False)

    features["temperature_sensor"] = click.confirm("Does this area have temperature sensors?", default=True)

    features["humidity_sensor"] = click.confirm("Does this area have humidity sensors?", default=False)

    # Add smart lighting as a feature
    features["smart_lighting"] = click.confirm("Does this area have smart lighting?", default=True)
    if features["smart_lighting"]:
        features["lighting_defaults"] = get_lighting_defaults()

    if click.confirm("Does this area have powered devices?", default=True):
        features["power_monitoring"] = True
        features["devices"] = get_device_types(device_manager)
    else:
        features["power_monitoring"] = False
        features["devices"] = []

    features["climate_control"] = click.confirm("Does this area have climate control?", default=True)

    return features


def get_lighting_defaults() -> LightingDefaults:
    """Get default lighting configuration.

    Returns:
        Dictionary of lighting defaults
    """
    click.echo("\nConfigure default lighting settings:")

    defaults: LightingDefaults = {
        "brightness": click.prompt("Default brightness (0-100%)", type=int, default=50, show_default=True),
        "color_temp": click.prompt(
            "Default color temperature (warm/cool/neutral)",
            type=click.Choice(["warm", "cool", "neutral"]),
            default="neutral",
        ),
        "transition": click.prompt("Default transition time (seconds)", type=int, default=1, show_default=True),
    }

    return defaults


def get_device_types(device_manager: DeviceManager) -> List[str]:
    """Get specific devices in the area.

    Args:
        device_manager: The device manager instance

    Returns:
        List of device types present in the area
    """
    devices: List[str] = []
    device_options: Dict[str, str] = device_manager.get_device_options()

    click.echo("\nSelect devices present in this area:")
    for key, desc in device_options.items():
        if click.confirm(f"Is there a {desc}?", default=False):
            devices.append(key)

    return devices
