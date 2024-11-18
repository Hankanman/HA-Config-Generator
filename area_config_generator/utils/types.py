# area_config_generator/utils/types.py
"""Type definitions for Home Assistant Area Configuration Generator.

This module serves as the main entry point for all type definitions.
It re-exports all types from the specialized type modules for backward
compatibility and ease of use.
"""

from .types.configs import AreaConfig, AreaConfigType
from .types.devices import DeviceConfig, DeviceConfigReturn, DeviceGeneratorFunc, PowerComponent
from .types.entities import EntityConfig, EntityIds, OccupancyTrigger
from .types.features import Features, FeatureType, FeatureValue, LightingDefaults
from .types.input import InputBooleanConfig, InputConfig, InputNumberConfig
from .types.processed import ProcessedConfigValue, ProcessedDictValue, ProcessedListValue, ProcessedScalarValue
from .types.templates import (
    BaseTemplate,
    BinarySensorTemplate,
    FanTemplate,
    SensorTemplate,
    TemplateComponent,
    TemplateItem,
    TemplateList,
)

__all__ = [
    # Configs
    "AreaConfig",
    "AreaConfigType",
    # Devices
    "DeviceConfig",
    "DeviceConfigReturn",
    "DeviceGeneratorFunc",
    "PowerComponent",
    # Entities
    "EntityConfig",
    "EntityIds",
    "OccupancyTrigger",
    # Features
    "Features",
    "FeatureType",
    "FeatureValue",
    "LightingDefaults",
    # Input
    "InputConfig",
    "InputNumberConfig",
    "InputBooleanConfig",
    # Processed
    "ProcessedConfigValue",
    "ProcessedDictValue",
    "ProcessedListValue",
    "ProcessedScalarValue",
    # Templates
    "BaseTemplate",
    "BinarySensorTemplate",
    "SensorTemplate",
    "FanTemplate",
    "TemplateComponent",
    "TemplateItem",
    "TemplateList",
]
