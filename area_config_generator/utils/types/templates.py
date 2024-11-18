# area_config_generator/utils/types/templates.py
"""Template type definitions."""

from typing import Any, Dict, List, Literal, Union

from typing_extensions import NotRequired, TypedDict


class BaseTemplate(TypedDict, total=False):
    """Base template for all components."""

    name: str
    unique_id: str
    state: str
    device_class: str
    unit_of_measurement: str
    icon: str
    attributes: Dict[str, str]


class BinarySensorTemplate(BaseTemplate):
    """Template for binary sensors."""

    state: NotRequired[str]
    attributes: NotRequired[Dict[str, str]]


class SensorTemplate(BaseTemplate):
    """Template for regular sensors."""

    state: NotRequired[str]
    attributes: NotRequired[Dict[str, str]]


class FanTemplate(BaseTemplate):
    """Template for fans."""

    platform: Literal["template"]
    fans: Dict[str, Dict[str, Any]]


# Template Component Types
TemplateComponent = Union[BinarySensorTemplate, SensorTemplate, FanTemplate]
"""Union type for all template components."""

TemplateItem = Dict[str, List[TemplateComponent]]
"""Single template item structure."""

TemplateList = List[TemplateItem]
"""List of template items."""

__all__ = [
    "BaseTemplate",
    "BinarySensorTemplate",
    "SensorTemplate",
    "FanTemplate",
    "TemplateComponent",
    "TemplateItem",
    "TemplateList",
]
