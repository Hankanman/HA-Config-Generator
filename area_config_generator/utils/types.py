# area_config_generator/utils/types.py
from __future__ import annotations  # Added for forward references

from typing import Any, Callable, Dict, Hashable, List, Literal, TypeAlias, TypedDict, TypeVar, Union, cast

# Basic types
ConfigType = Dict[str, List[Dict[str, Any]]]
AreaName = str
TemplateConfig = Dict[str, Union[str, int, List[str]]]
FeatureValue = Union[bool, List[str], str]
FeatureType = Dict[str, FeatureValue]
ConfigGeneratorFunc = Callable[[AreaName], ConfigType]

EntityType = Literal["climate", "binary_sensor", "sensor", "input_boolean", "input_number", "switch", "fan"]
DeviceOptionsType = Dict[str, str]

# Generic type variables
KT = TypeVar("KT", bound=Hashable)
VT = TypeVar("VT")


# Precise dictionary type
class PreciseDict(Dict[KT, VT]):
    """A dictionary with more precise key and value types."""

    pass


# Processed configuration value type
ProcessedConfigValue: TypeAlias = Union[
    str, int, float, bool, Dict[str, "ProcessedConfigValue"], List["ProcessedConfigValue"]
]

# Recursive dictionary type for processed configuration
ProcessedDict: TypeAlias = Dict[str, ProcessedConfigValue]


def convert_to_processed_config_value(value: object) -> ProcessedConfigValue:
    """Convert a value to ProcessedConfigValue.

    Args:
        value: The value to convert

    Returns:
        Processed configuration value
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


class EntityConfig(TypedDict):
    """Configuration for an entity."""

    domain: EntityType
    suggested_id: str
    description: str


class EntityIds(TypedDict, total=False):
    """Type for entity IDs."""

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


class Features(TypedDict, total=False):
    """Type for feature configuration."""

    area_name: str
    normalized_area_name: str
    motion_sensor: bool
    door_sensor: bool
    window_sensor: bool
    temperature_sensor: bool
    humidity_sensor: bool
    power_monitoring: bool
    climate_control: bool
    devices: List[str]
    entity_ids: EntityIds


# Sensor base configurations
class SensorBase(TypedDict, total=False):
    """Base sensor configuration."""

    name: str
    unique_id: str
    state: str
    device_class: str
    state_class: str
    unit_of_measurement: str
    icon: str


class BinarySensorConfig(SensorBase):
    """Binary sensor configuration."""

    attributes: Dict[str, str]


class SensorConfig(SensorBase):
    """Regular sensor configuration."""

    attributes: Dict[str, str]


# Fan configuration
class FanConfig(TypedDict):
    """Fan configuration."""

    platform: Literal["template"]
    fans: Dict[str, Dict[str, Any]]


# State template configuration
class StateTemplateConfig(TypedDict):
    """State template configuration."""

    sensor: List[Dict[str, Any]]


# Template configuration item
class TemplateConfigItem(TypedDict, total=False):
    """Template configuration item."""

    binary_sensor: List[BinarySensorConfig]
    sensor: List[SensorConfig]
    fan: List[FanConfig]
    state_template: List[StateTemplateConfig]


# Input configurations
class InputNumberConfig(TypedDict):
    """Input number configuration."""

    name: str
    min: float
    max: float
    step: float
    unit_of_measurement: str
    icon: str
    initial: float


class InputBooleanConfig(TypedDict):
    """Input boolean configuration."""

    name: str
    icon: str


# Area configuration
class AreaConfig(TypedDict):
    """Area configuration."""

    template: List[TemplateConfigItem]
    input_number: Dict[str, InputNumberConfig]
    input_boolean: Dict[str, InputBooleanConfig]


# Area configuration type
AreaConfigType = Dict[str, AreaConfig]


# Power component
class PowerComponent(TypedDict):
    """Power component configuration."""

    power_entity: str
    energy_entity: str
    description: str


# Occupancy trigger
class OccupancyTrigger(TypedDict, total=False):
    """Occupancy trigger configuration."""

    weight: int
    description: str
    condition: str


def convert_area_config_to_config(area_config: AreaConfigType) -> ConfigType:
    """Convert AreaConfigType to ConfigType with type safety."""
    config: ConfigType = {}

    for area_name, area_details in area_config.items():
        template_items: List[Dict[str, Any]] = []

        for template_item in area_details.get("template", []):
            converted_item: Dict[str, List[Dict[str, Any]]] = {}
            valid_keys = {"binary_sensor", "sensor", "fan", "state_template"}

            for key in valid_keys:
                if key in template_item and isinstance(template_item[key], list):
                    converted_item[key] = template_item[key]

            if converted_item:
                template_items.append(converted_item)

        if template_items:
            config[area_name] = template_items

    return config
