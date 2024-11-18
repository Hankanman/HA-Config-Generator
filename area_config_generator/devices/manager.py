# area_config_generator/devices/manager.py
"""Device management module for Home Assistant Area Configuration Generator."""

from typing import Dict, List, Optional

from ..utils.types import DeviceConfig, DeviceConfigReturn, DeviceGeneratorFunc, Features
from . import appliance, bathroom, computer, kitchen, tv


class DeviceManager:
    """Manages device configuration generation."""

    def __init__(self) -> None:
        """Initialize the device manager."""
        # Map device types to their configuration generators
        self.device_generators: Dict[str, DeviceGeneratorFunc] = {
            "computer": computer.generate_computer_config,
            "tv": tv.generate_tv_config,
            "appliance": appliance.generate_appliance_config,
            "bathroom": bathroom.generate_bathroom_config,
            "kitchen": kitchen.generate_kitchen_config,
        }

        # Device descriptions for CLI
        self.device_options: Dict[str, str] = {
            "computer": "Computer/PC setup",
            "tv": "Television/Entertainment system",
            "appliance": "Major appliances (washing machine, dishwasher, etc)",
            "bathroom": "Bathroom fixtures (shower, toilet, etc)",
            "kitchen": "Kitchen appliances (fridge, oven, etc)",
        }

    def get_device_options(self) -> Dict[str, str]:
        """Get available device options with descriptions."""
        return self.device_options

    def generate_device_config(
        self, device_type: str, area_name: str, normalized_area_name: str
    ) -> Optional[DeviceConfigReturn]:
        """Generate configuration for a specific device type.

        Args:
            device_type: The type of device to configure
            area_name: The display name of the area
            normalized_area_name: The normalized (lowercase, underscored) area name

        Returns:
            Device configuration if generator exists, None otherwise
        """
        generator = self.device_generators.get(device_type)
        if generator:
            return generator(area_name, normalized_area_name)
        return None

    def generate_all_device_configs(self, features: Features) -> List[DeviceConfig]:
        """Generate configurations for all devices in features.

        Args:
            features: Feature configuration containing device list and area details

        Returns:
            List of device configurations
        """
        configs: List[DeviceConfig] = []
        area_name = str(features.get("area_name", ""))
        normalized_area_name = str(features.get("normalized_area_name", area_name.lower()))

        for device in features.get("devices", []):
            config = self.generate_device_config(device, area_name, normalized_area_name)
            if config:
                configs.append(DeviceConfig, config)

        return configs
