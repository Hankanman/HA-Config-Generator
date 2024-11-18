# area_config_generator/cli/__init__.py

"""CLI module for Home Assistant Area Configuration Generator."""

from .entity_config import get_entity_config
from .feature_config import get_area_features, get_device_types, get_lighting_defaults
from .input_config import generate_input_controls
from .interface import main

__all__ = [
    "main",
    "get_entity_config",
    "get_area_features",
    "get_lighting_defaults",
    "get_device_types",
    "generate_input_controls",
]
