# area_config_generator/utils/types/input.py
"""Input type definitions."""

from typing_extensions import TypedDict


class InputConfig(TypedDict):
    """Base input configuration."""

    name: str
    icon: str


class InputNumberConfig(InputConfig):
    """Numeric input configuration."""

    min: float
    max: float
    step: float
    unit_of_measurement: str
    initial: float


class InputBooleanConfig(InputConfig):
    """Boolean input configuration."""

    pass


__all__ = [
    "InputConfig",
    "InputNumberConfig",
    "InputBooleanConfig",
]
