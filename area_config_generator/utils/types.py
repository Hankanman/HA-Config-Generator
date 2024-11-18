"""
Type definitions and utility functions for the Area Config Generator.

This module provides comprehensive type definitions and utility functions
to support type-safe configuration generation for Home Assistant areas.
"""

from __future__ import annotations  # Added for forward references

from typing import Any, Callable, Dict, Hashable, List, Literal, TypeAlias, TypeVar, Union, cast

from typing_extensions import NotRequired, TypedDict

# Basic Type Definitions
# These define fundamental types used throughout the configuration generation process
ConfigType = Dict[str, Dict[str, Any]]
"""A dictionary representing the overall configuration structure."""

AreaName = str
"""Type alias for area names."""

TemplateConfig = Dict[str, Union[str, int, List[str]]]
"""Configuration template with mixed value types."""

FeatureValue = Union[bool, List[str], str]
"""Possible values for feature configurations."""

FeatureType = Dict[str, FeatureValue]
"""Dictionary of features with their corresponding values."""

ConfigGeneratorFunc = Callable[[AreaName], ConfigType]
"""Type for functions that generate configurations for a specific area."""

# Type Variables and Generic Types
KT = TypeVar("KT", bound=Hashable)
"""Generic type variable for dictionary keys that are hashable."""

VT = TypeVar("VT")
"""Generic type variable for dictionary values."""


class PreciseDict(Dict[KT, VT]):
    """A dictionary with more precise key and value types."""

    pass


# Entity and Domain Types
EntityType = Literal[
    "climate", "binary_sensor", "sensor", "input_boolean", "input_number", "switch", "fan", "light", "scene"
]
"""Literal type representing possible Home Assistant entity domains."""

DeviceOptionsType = Dict[str, str]
"""Dictionary of device-specific options."""

# Processed Configuration Value Types
ProcessedScalarValue = Union[str, int, float, bool]
"""Scalar values that can be processed in configurations."""

ProcessedDictValue = Dict[str, "ProcessedConfigValue"]
"""Nested dictionary of processed configuration values."""

ProcessedListValue = List["ProcessedConfigValue"]
"""List of processed configuration values."""

ProcessedConfigValue = Union[ProcessedScalarValue, ProcessedDictValue, ProcessedListValue]
"""Union type representing all possible processed configuration value types."""

ProcessedDict: TypeAlias = Dict[str, ProcessedConfigValue]
"""Type alias for processed configuration dictionaries."""

# Template-Specific Types
TemplateItem = Dict[str, List[Dict[str, Any]]]
"""A dictionary representing a template configuration item."""

TemplateList = List[TemplateItem]
"""A list of template configuration items."""

DeviceConfigType = Dict[str, List[Dict[str, Any]]]
"""Type for device configuration dictionaries."""


# Entity Configuration Types
class EntityConfig(TypedDict):
    """Configuration details for a specific entity."""

    domain: EntityType
    suggested_id: str
    description: str


class EntityIds(TypedDict, total=False):
    """Comprehensive type for tracking entity IDs across different domains."""

    climate: str
    temperature: str
    humidity: str
    window: str
    motion: str
    door: str
    pc_power: str
    pc_active: str
    monitors_power: str
    desk_power: str
    tv_power: str
    tv_active: str
    entertainment_power: str
    appliance_power: str
    appliance_active: str
    bathroom_power: str
    bathroom_active: str
    kitchen_power: str
    kitchen_active: str
    extras_power: str
    occupied_override: str
    light_group: str
    light_scene: str


# Feature and Lighting Configuration Types
class LightingDefaults(TypedDict, total=False):
    """Default configuration options for lighting."""

    brightness: int
    color_temp: str
    transition: int


class Features(TypedDict, total=False):
    """Comprehensive feature configuration for an area."""

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


# Device and Sensor Base Templates
class DeviceTemplate(TypedDict):
    """Base template for device configurations with optional attributes."""

    name: str
    unique_id: str
    attributes: NotRequired[Dict[str, str]]
    state: NotRequired[str]
    device_class: NotRequired[str]
    unit_of_measurement: NotRequired[str]
    icon: NotRequired[str]


class SensorConfigBase(TypedDict, total=False):
    """Base configuration for sensors with comprehensive options."""

    name: str
    unique_id: str
    state: str
    device_class: str
    state_class: str
    unit_of_measurement: str
    icon: str
    attributes: Dict[str, str]


class SensorBase(TypedDict, total=False):
    """Simplified sensor base configuration."""

    name: str
    unique_id: str
    state: str
    device_class: str
    state_class: str
    unit_of_measurement: str
    icon: str


class BinarySensorConfig(SensorConfigBase):
    """Specific configuration for binary sensors."""

    pass


class SensorConfig(SensorConfigBase):
    """Specific configuration for regular sensors."""

    pass


# State and Template Configurations
class StateTemplateConfig(TypedDict):
    """Configuration for state templates."""

    sensor: List[Dict[str, Any]]


class TemplateConfigItem(TypedDict, total=False):
    """Flexible template configuration with optional components."""

    binary_sensor: NotRequired[List[BinarySensorConfig]]
    sensor: NotRequired[List[SensorConfig]]
    fan: NotRequired[List[FanConfig]]
    state_template: NotRequired[List[Dict[str, Any]]]


# Input Configurations
class InputNumberConfig(TypedDict):
    """Configuration for numeric input entities."""

    name: str
    min: float
    max: float
    step: float
    unit_of_measurement: str
    icon: str
    initial: float


class InputBooleanConfig(TypedDict):
    """Configuration for boolean input entities."""

    name: str
    icon: str


# Area and Configuration Types
class AreaConfig(TypedDict):
    """Complete configuration for a specific area."""

    template: TemplateList
    input_number: Dict[str, InputNumberConfig]
    input_boolean: Dict[str, InputBooleanConfig]


AreaConfigType = Dict[str, AreaConfig]
"""Type alias for area configurations."""


# Power and Occupancy Types
class PowerComponent(TypedDict):
    """Configuration for power-related entities."""

    power_entity: str
    energy_entity: str
    description: str


class OccupancyTrigger(TypedDict, total=False):
    """Configuration for occupancy triggers with optional fields."""

    weight: int
    description: str
    condition: str


# Device Template Types
class BaseDeviceTemplate(TypedDict, total=False):
    """Base template with optional device configuration fields."""

    attributes: Dict[str, str]
    state: str
    icon: str


class RequiredDeviceFields(TypedDict):
    """Required fields for all device templates."""

    name: str
    unique_id: str


class BinarySensorTemplate(RequiredDeviceFields, BaseDeviceTemplate):
    """Specific template for binary sensor configurations."""

    device_class: str


class SensorTemplate(RequiredDeviceFields, BaseDeviceTemplate):
    """Specific template for sensor configurations."""

    unit_of_measurement: str
    state_class: NotRequired[str]


# Fan-specific Types
class FanSpeedAction(TypedDict):
    """Configuration for fan speed control actions."""

    service: str
    entity_id: str
    data_template: Dict[str, str]


class FanConfig(TypedDict):
    """Comprehensive configuration for individual fan entities."""

    friendly_name: str
    value_template: str
    speed_template: str
    turn_on: Dict[str, str]
    turn_off: Dict[str, str]
    set_speed: FanSpeedAction
    speeds: List[str]


class FanTemplate(TypedDict):
    """Template configuration for fan platforms."""

    platform: Literal["template"]
    fans: Dict[str, FanConfig]


# Component and Configuration Type Unions
TemplateComponent = Union[BinarySensorTemplate, SensorTemplate, FanTemplate]
"""Union type for components that can appear in a template."""


class DeviceConfig(TypedDict):
    """Configuration structure for device types."""

    template: List[Dict[str, List[TemplateComponent]]]


DeviceConfigReturn = Dict[str, List[Dict[str, List[TemplateComponent]]]]
"""Return type for device generation functions."""


# Utility Functions
def convert_template_config_to_item(config: TemplateConfigItem) -> TemplateItem:
    """
    Convert a TemplateConfigItem to a TemplateItem safely.

    Args:
        config (TemplateConfigItem): The input configuration to convert.

    Returns:
        TemplateItem: A safely converted template item.
    """
    result: TemplateItem = {}

    if "binary_sensor" in config:
        result["binary_sensor"] = [cast(Dict[str, Any], sensor) for sensor in config["binary_sensor"]]

    if "sensor" in config:
        result["sensor"] = [cast(Dict[str, Any], sensor) for sensor in config["sensor"]]

    if "fan" in config:
        result["fan"] = [cast(Dict[str, Any], fan) for fan in config["fan"]]

    if "state_template" in config:
        result["state_template"] = [template for template in config["state_template"]]

    return result


def convert_to_processed_config_value(value: Any) -> ProcessedConfigValue:
    """
    Recursively convert a value to a ProcessedConfigValue.

    This function handles nested structures like lists and dictionaries,
    converting them to a type-safe representation.

    Args:
        value (Any): The value to convert.

    Returns:
        ProcessedConfigValue: A type-safe, processed configuration value.
    """
    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, list):
        value_list = cast(List[Any], value)
        return [convert_to_processed_config_value(item) for item in value_list]

    if isinstance(value, dict):
        value_dict = cast(Dict[Any, Any], value)
        return {str(key): convert_to_processed_config_value(val) for key, val in value_dict.items()}

    return str(value)


def convert_area_config_to_config(area_config: AreaConfigType) -> ConfigType:
    """
    Convert an AreaConfigType to a ConfigType with type safety.

    Args:
        area_config (AreaConfigType): The input area configuration.

    Returns:
        ConfigType: A type-safe configuration dictionary.
    """
    config: ConfigType = {}

    for area_name, area_details in area_config.items():
        config[area_name] = {}

        # Process template items
        if "template" in area_details:
            template_items: TemplateList = []
            for template_item in area_details["template"]:
                converted_item: TemplateItem = {}
                valid_keys = {"binary_sensor", "sensor", "fan", "state_template"}

                for key in valid_keys:
                    if key in template_item and template_item[key]:
                        converted_item[key] = template_item[key]

                if converted_item:
                    template_items.append(converted_item)

            if template_items:
                config[area_name]["template"] = template_items

        # Process input_number configurations
        if "input_number" in area_details:
            config[area_name]["input_number"] = area_details["input_number"]

        # Process input_boolean configurations
        if "input_boolean" in area_details:
            config[area_name]["input_boolean"] = area_details["input_boolean"]

    return config
