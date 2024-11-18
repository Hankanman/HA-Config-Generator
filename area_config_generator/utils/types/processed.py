# area_config_generator/utils/types/processed.py
"""Processed value type definitions."""

from typing import Any, Dict, List, Union

# Processed value types
ProcessedScalarValue = Union[str, int, float, bool]
ProcessedDictValue = Dict[str, Any]
ProcessedListValue = List[Any]
ProcessedConfigValue = Union[ProcessedScalarValue, ProcessedDictValue, ProcessedListValue]

__all__ = [
    "ProcessedScalarValue",
    "ProcessedDictValue",
    "ProcessedListValue",
    "ProcessedConfigValue",
]
