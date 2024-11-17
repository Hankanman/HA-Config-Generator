# area_config_generator/utils/types.py
from typing import Any, Callable, Dict, List, Literal, TypedDict, Union

# Basic types
ConfigType = Dict[str, List[Dict[str, Any]]]
AreaName = str
TemplateConfig = Dict[str, Union[str, int, List[str]]]
FeatureValue = Union[bool, List[str], str]
FeatureType = Dict[str, FeatureValue]
ConfigGeneratorFunc = Callable[[AreaName], ConfigType]


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
