# area_config_generator/utils/types/__init__.py
"""Base type definitions module."""

from typing import Any, Hashable, Mapping, TypeVar

from .configs import *  # noqa: F401, F403
from .devices import *  # noqa: F401, F403
from .entities import *  # noqa: F401, F403
from .features import *  # noqa: F401, F403
from .input import *  # noqa: F401, F403
from .processed import *  # noqa: F401, F403
from .templates import *  # noqa: F401, F403

# Type variables
KT = TypeVar("KT", bound=Hashable)
VT = TypeVar("VT")
T = TypeVar("T")

# Basic type definitions
ConfigType = Mapping[str, Mapping[str, Any]]
"""Base configuration type using Mapping for covariance."""

__all__ = ["ConfigType", "KT", "VT", "T"]
