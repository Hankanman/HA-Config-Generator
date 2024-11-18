# area_config_generator/utils/types.py
from __future__ import annotations  # Added for forward references

from typing import Any, Callable, Dict, Hashable, List, Literal, TypeAlias, TypeVar, Union, cast

from typing_extensions import NotRequired, TypedDict

# Basic types
ConfigType = Dict[str, Dict[str, Any]]
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


# Processed configuration value types
ProcessedScalarValue = Union[str, int, float, bool]
ProcessedDictValue = Dict[str, "ProcessedConfigValue"]
ProcessedListValue = List["ProcessedConfigValue"]
ProcessedConfigValue = Union[ProcessedScalarValue, ProcessedDictValue, ProcessedListValue]

# Template specific types
TemplateItem = Dict[str, List[Dict[str, Any]]]
TemplateList = List[TemplateItem]

# Recursive dictionary type for processed configuration
ProcessedDict: TypeAlias = Dict[str, ProcessedConfigValue]


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
class SensorConfigBase(TypedDict, total=False):
    """Base configuration for sensors."""

    name: str
    unique_id: str
    state: str
    device_class: str
    state_class: str
    unit_of_measurement: str
    icon: str
    attributes: Dict[str, str]


class SensorBase(TypedDict, total=False):
    """Base sensor configuration."""

    name: str
    unique_id: str
    state: str
    device_class: str
    state_class: str
    unit_of_measurement: str
    icon: str


class BinarySensorConfig(SensorConfigBase):
    """Binary sensor specific configuration."""

    pass


class SensorConfig(SensorConfigBase):
    """Regular sensor specific configuration."""

    pass


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
    """Template configuration item with optional fields."""

    binary_sensor: NotRequired[List[BinarySensorConfig]]
    sensor: NotRequired[List[SensorConfig]]
    fan: NotRequired[List[FanConfig]]
    state_template: NotRequired[List[Dict[str, Any]]]


# Input configurations
class InputNumberConfig(TypedDict):
    name: str
    min: float
    max: float
    step: float
    unit_of_measurement: str
    icon: str
    initial: float


class InputBooleanConfig(TypedDict):
    name: str
    icon: str


# Area configuration
class AreaConfig(TypedDict):
    template: TemplateList
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


def convert_template_config_to_item(config: TemplateConfigItem) -> TemplateItem:
    """Convert TemplateConfigItem to TemplateItem safely."""
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


def convert_area_config_to_config(area_config: AreaConfigType) -> ConfigType:
    """Convert AreaConfigType to ConfigType with type safety."""
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
