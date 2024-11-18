# area_config_generator/utils/types/entities.py
"""Entity type definitions."""

from typing_extensions import TypedDict


class EntityConfig(TypedDict):
    """Entity configuration."""

    domain: str
    suggested_id: str
    description: str


class EntityIds(TypedDict, total=False):
    """Entity ID mapping."""

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
    light_group: str
    light_scene: str


class OccupancyTrigger(TypedDict, total=False):
    """Occupancy trigger configuration."""

    weight: int
    description: str
    condition: str


__all__ = [
    "EntityConfig",
    "EntityIds",
    "OccupancyTrigger",
]
