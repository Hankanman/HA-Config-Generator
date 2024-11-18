# area_config_generator/utils/types/features.py
"""Feature type definitions."""

from typing import List

from typing_extensions import TypedDict

from .entities import EntityIds


class LightingDefaults(TypedDict, total=False):
    """Lighting defaults configuration."""

    brightness: int
    color_temp: str
    transition: int


class Features(TypedDict, total=False):
    """Area features configuration."""

    area_name: str
    normalized_area_name: str
    motion_sensor: bool
    door_sensor: bool
    window_sensor: bool
    temperature_sensor: bool
    humidity_sensor: bool
    power_monitoring: bool
    climate_control: bool
    smart_lighting: bool
    lighting_defaults: LightingDefaults
    devices: List[str]
    entity_ids: EntityIds


# Type aliases
FeatureValue = bool | List[str] | str
"""Possible values for feature configurations."""

FeatureType = dict[str, FeatureValue]
"""Dictionary of features with their corresponding values."""

__all__ = [
    "LightingDefaults",
    "Features",
    "FeatureValue",
    "FeatureType",
]
