# area_config_generator/utils/validation.py

from typing import Any, Dict, List, cast

from .types import BinarySensorTemplate, DeviceConfig, FanTemplate, SensorTemplate, TemplateItem


def ensure_template_items(items: List[Dict[str, Any]]) -> List[TemplateItem]:
    """Ensure a list of dictionaries are valid TemplateItems.

    Args:
        items: List of dictionaries to validate

    Returns:
        List of validated TemplateItems
    """
    result: List[TemplateItem] = []

    for item in items:
        template_item: TemplateItem = {}

        if "binary_sensor" in item:
            template_item["binary_sensor"] = [cast(BinarySensorTemplate, sensor) for sensor in item["binary_sensor"]]

        if "sensor" in item:
            template_item["sensor"] = [cast(SensorTemplate, sensor) for sensor in item["sensor"]]

        if "fan" in item:
            template_item["fan"] = [cast(FanTemplate, fan) for fan in item["fan"]]

        if template_item:
            result.append(template_item)

    return result


def ensure_valid_config(config: Any, context: str = "") -> None:
    """Ensure configuration is valid.

    Args:
        config: Configuration to validate
        context: Optional context for error messages

    Raises:
        ValidationError: If configuration is invalid
    """
    if isinstance(config, dict):
        if "template" in config:
            device_config = cast(DeviceConfig, config)
            ensure_template_items(device_config["template"])
    else:
        raise ValueError(f"Invalid configuration type: {type(config)}")
