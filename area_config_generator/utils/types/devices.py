# area_config_generator/utils/types/devices.py
"""Device type definitions."""

from typing import Protocol

from typing_extensions import TypedDict

from .templates import TemplateItem


class DeviceConfig(TypedDict):
    """Device configuration structure."""

    template: list[TemplateItem]


class DeviceGeneratorProtocol(Protocol):
    """Protocol for device generator functions."""

    def __call__(self, area_name: str, normalized_area_name: str, *args: str) -> DeviceConfig: ...


# Type aliases
DeviceConfigReturn = DeviceConfig
"""Return type for device generators."""

DeviceGeneratorFunc = DeviceGeneratorProtocol
"""Type for device generator functions."""


# Power component types
class PowerComponent(TypedDict):
    """Power component configuration."""

    power_entity: str
    energy_entity: str
    description: str


__all__ = [
    "DeviceConfig",
    "DeviceConfigReturn",
    "DeviceGeneratorFunc",
    "PowerComponent",
]
