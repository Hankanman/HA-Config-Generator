# area_config_generator/utils/types/configs.py
"""Configuration type definitions."""

from typing import Dict, Mapping

from typing_extensions import TypedDict

from .input import InputBooleanConfig, InputNumberConfig
from .templates import TemplateList


class AreaConfig(TypedDict):
    """Area configuration."""

    template: TemplateList
    input_number: Dict[str, InputNumberConfig]
    input_boolean: Dict[str, InputBooleanConfig]


AreaConfigType = Mapping[str, AreaConfig]
"""Type for area configurations using Mapping for covariance."""

__all__ = [
    "AreaConfig",
    "AreaConfigType",
]
