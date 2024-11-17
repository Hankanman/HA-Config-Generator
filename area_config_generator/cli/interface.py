from collections.abc import Iterable
from typing import Any, Dict, List, Literal, Optional, TypedDict, TypeGuard, TypeVar, Union, cast, overload

import click

from ..generators import climate, occupancy, power
from ..utils.types import (
    AreaConfigType,
    FeatureType,
    FeatureValue,
    InputBooleanConfig,
    InputNumberConfig,
    TemplateConfigItem,
    convert_area_config_to_config,
)
from ..utils.yaml_writer import write_yaml_config

# Type definitions
DeviceOptionsType = Dict[str, str]
T = TypeVar("T", bound=Dict[str, Any])

# Template-specific types
TemplateKeyType = Literal["binary_sensor", "sensor", "fan", "state_template"]


class BaseTemplateItem(TypedDict, total=False):
    """Base type for template items."""

    name: str
    unique_id: str
    state: str
    attributes: Dict[str, Any]


class SensorTemplateItem(BaseTemplateItem):
    """Sensor template item type."""

    device_class: Optional[str]
    state_class: Optional[str]
    unit_of_measurement: Optional[str]


class BinarySensorTemplateItem(BaseTemplateItem):
    """Binary sensor template item type."""

    device_class: Optional[str]


class FanTemplateItem(BaseTemplateItem):
    """Fan template item type."""

    platform: str
    fans: Dict[str, Dict[str, Any]]


class StateTemplateItem(BaseTemplateItem):
    """State template item type."""

    sensor: List[Dict[str, Any]]


TemplateItemValueType = Union[
    List[SensorTemplateItem], List[BinarySensorTemplateItem], List[FanTemplateItem], List[StateTemplateItem]
]


class TemplateItemDict(TypedDict, total=False):
    """Type definition for template items."""

    binary_sensor: List[BinarySensorTemplateItem]
    sensor: List[SensorTemplateItem]
    fan: List[FanTemplateItem]
    state_template: List[StateTemplateItem]


def is_dict(value: Any) -> TypeGuard[Dict[str, Any]]:
    """Check if a value is a dictionary."""
    return isinstance(value, dict)


def is_list(value: Any) -> TypeGuard[List[Any]]:
    """Check if a value is a list."""
    return isinstance(value, list)


def is_template_key(key: Any) -> TypeGuard[TemplateKeyType]:
    """Check if a value is a valid template key."""
    return isinstance(key, str) and key in {"binary_sensor", "sensor", "fan", "state_template"}


def validate_template_key(item: Dict[str, Any], key: TemplateKeyType) -> bool:
    """Validate that a template item has the correct structure for a key."""
    if not is_dict(item) or key not in item:
        return False

    value = item[key]
    if not is_list(value):
        return False

    return all(is_dict(subitem) for subitem in value)


def is_valid_template_item(item: Any) -> TypeGuard[TemplateConfigItem]:
    """Check if an item is a valid template configuration item."""
    if not is_dict(item):
        return False

    # Check that at least one valid key exists with correct structure
    return any(is_template_key(key) and validate_template_key(item, key) for key in item.keys())


@overload
def safe_get_template(config: Dict[str, Any], key: str = "template") -> List[TemplateItemDict]: ...


@overload
def safe_get_template(config: List[Any], key: str = "template") -> List[TemplateItemDict]: ...


def safe_get_template(config: Union[Dict[str, Any], List[Any]], key: str = "template") -> List[TemplateItemDict]:
    """Safely get template list from config dictionary or list."""
    if is_dict(config):
        template = config.get(key, [])
    else:
        template = config

    if not is_list(template):
        return []

    return [cast(TemplateItemDict, item) for item in template if is_dict(item)]


def extract_template_list(items: Iterable[Any]) -> List[TemplateConfigItem]:
    """Extract valid template items from an iterable."""
    return [item for item in items if is_valid_template_item(item)]


def extract_template(config: Union[Dict[str, Any], List[Any]]) -> List[TemplateConfigItem]:
    """Extract template configuration from config."""
    if is_dict(config):
        return extract_template_list(safe_get_template(config))
    if is_list(config):
        return extract_template_list(config)
    return []


@click.command()
@click.argument("area_name")
def main(area_name: str) -> None:
    """Generate a Home Assistant area configuration."""
    click.echo(f"Generating configuration for {area_name}")

    features: FeatureType = get_area_features()
    features["area_name"] = area_name

    config: AreaConfigType = generate_area_config(area_name, features)
    write_yaml_config(area_name, convert_area_config_to_config(config))

    click.echo(f"Configuration generated for {area_name}")


def get_area_features() -> FeatureType:
    """Interactive CLI to determine area features."""
    features: Dict[str, FeatureValue] = {}

    features["motion_sensor"] = click.confirm("Does this area have motion sensors?", default=True)
    features["door_sensor"] = click.confirm("Does this area have door sensors?", default=True)
    features["window_sensor"] = click.confirm("Does this area have window sensors?", default=False)
    features["temperature_sensor"] = click.confirm("Does this area have temperature sensors?", default=True)

    if click.confirm("Does this area have powered devices?", default=True):
        features["power_monitoring"] = True
        features["devices"] = get_device_types()
    else:
        features["power_monitoring"] = False
        features["devices"] = []

    features["climate_control"] = click.confirm("Does this area have climate control?", default=True)

    return features


def get_device_types() -> List[str]:
    """Get specific devices in the area."""
    devices: List[str] = []

    device_options: DeviceOptionsType = {
        "computer": "Computer/PC setup",
        "tv": "Television/Entertainment system",
        "appliance": "Major appliances (washing machine, dishwasher, etc)",
        "lighting": "Smart lighting",
        "bathroom": "Bathroom fixtures (shower, toilet, etc)",
        "kitchen": "Kitchen appliances (fridge, oven, etc)",
    }

    click.echo("\nSelect devices present in this area:")
    for key, desc in device_options.items():
        if click.confirm(f"Is there a {desc}?", default=False):
            devices.append(key)

    return devices


def generate_area_config(area_name: str, features: FeatureType) -> AreaConfigType:
    """Generate the complete area configuration."""
    config: AreaConfigType = {area_name: {"template": [], "input_number": {}, "input_boolean": {}}}

    def filter_features(features_dict: FeatureType) -> Dict[str, Union[bool, str, List[str]]]:
        return {k: v for k, v in features_dict.items() if k != "area_name"}

    def extract_devices(features_dict: FeatureType) -> List[str]:
        devices = features_dict.get("devices")
        if not is_list(devices):
            return []
        return devices

    if features.get("motion_sensor") or features.get("door_sensor"):
        occupancy_features = filter_features(features)
        occupancy_config = occupancy.generate_occupancy_config(occupancy_features)
        config[area_name]["template"].extend(extract_template(occupancy_config))

    if features.get("power_monitoring"):
        devices = extract_devices(features)
        power_config = power.generate_power_config(devices)
        config[area_name]["template"].extend(extract_template(power_config))

    if features.get("climate_control"):
        climate_features = {k: v for k, v in filter_features(features).items() if isinstance(v, (bool, str))}
        climate_config = climate.generate_climate_config(climate_features)
        config[area_name]["template"].extend(extract_template(climate_config))

    input_controls = generate_input_controls(features)

    if "input_number" in input_controls:
        config[area_name]["input_number"] = {
            k: cast(InputNumberConfig, v) for k, v in input_controls["input_number"].items()
        }

    if "input_boolean" in input_controls:
        config[area_name]["input_boolean"] = {
            k: cast(InputBooleanConfig, v) for k, v in input_controls["input_boolean"].items()
        }

    return config


def generate_input_controls(features: FeatureType) -> Dict[str, Dict[str, Union[InputNumberConfig, InputBooleanConfig]]]:
    """Generate input_number and input_boolean configurations."""
    controls: Dict[str, Dict[str, Union[InputNumberConfig, InputBooleanConfig]]] = {
        "input_number": {},
        "input_boolean": {},
    }

    area_name = str(features.get("area_name", "unknown_area"))

    if features.get("power_monitoring"):
        controls["input_number"][f"{area_name}_power_threshold"] = cast(
            InputNumberConfig,
            {
                "name": f"{area_name.title()} Power Alert Threshold",
                "min": 100.0,
                "max": 1000.0,
                "step": 50.0,
                "unit_of_measurement": "W",
                "icon": "mdi:flash-alert",
                "initial": 400.0,
            },
        )

    if features.get("climate_control"):
        controls["input_number"][f"{area_name}_temp_threshold"] = cast(
            InputNumberConfig,
            {
                "name": f"{area_name.title()} Temperature Threshold",
                "min": 19.0,
                "max": 25.0,
                "step": 0.5,
                "unit_of_measurement": "°C",
                "icon": "mdi:thermometer",
                "initial": 23.0,
            },
        )

    controls["input_boolean"] = {
        f"{area_name}_occupied_override": cast(
            InputBooleanConfig,
            {
                "name": f"{area_name.title()} Manual Occupancy Override",
                "icon": "mdi:account-check",
            },
        ),
        f"{area_name}_sleep_mode": cast(
            InputBooleanConfig,
            {
                "name": f"{area_name.title()} Sleep Mode",
                "icon": "mdi:power-sleep",
            },
        ),
    }

    return controls


if __name__ == "__main__":
    main()
