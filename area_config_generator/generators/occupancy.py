# area_config_generator/generators/occupancy.py
"""Occupancy detection configuration generator."""

from typing import Any, Dict, List, Union

from ..utils.types import AreaName, OccupancyTrigger


def generate_occupancy_config(features: Dict[str, Union[bool, str, List[str]]]) -> List[Dict[str, List[Dict[str, Any]]]]:
    """Generate occupancy detection configuration."""
    area_name = str(features.get("area_name", ""))

    # Build list of occupancy triggers and their weights
    triggers: Dict[str, OccupancyTrigger] = {}

    if features.get("motion_sensor"):
        triggers[f"binary_sensor.{area_name}_motion"] = {
            "weight": 2,
            "description": "Motion Detected",
        }

    if features.get("door_sensor"):
        triggers[f"binary_sensor.{area_name}_door_contact"] = {
            "weight": 1,
            "description": "Door Closed",
            "condition": "off",  # Door closed state
        }

    devices = features.get("devices", [])
    devices = devices if isinstance(devices, list) else []

    if "computer" in devices:
        triggers[f"binary_sensor.{area_name}_pc_active"] = {
            "weight": 3,
            "description": "PC Active",
        }

    if "tv" in devices:
        triggers[f"binary_sensor.{area_name}_tv_state"] = {
            "weight": 2,
            "description": "TV Active",
        }

    # Special device handling
    if any(device in devices for device in ["appliance", "bathroom"]):
        triggers[f"binary_sensor.{area_name}_device_active"] = {
            "weight": 2,
            "description": "Device Active",
        }

    # Generate template configuration
    return [
        {
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Occupancy" if area_name else "Occupancy",
                    "unique_id": f"{area_name}_occupancy",
                    "device_class": "occupancy",
                    "state": generate_occupancy_state_template(triggers, area_name),
                    "attributes": {
                        "confidence_score": generate_confidence_score_template(triggers, area_name),
                        "active_triggers": generate_active_triggers_template(triggers, area_name),
                    },
                }
            ]
        }
    ]


def generate_occupancy_state_template(triggers: Dict[str, OccupancyTrigger], area_name: AreaName) -> str:
    """Generate the template for occupancy state calculation."""
    # Construct template lines
    template_lines = ["{% set scores = namespace(total=0) %}"]

    # Add scoring logic for each trigger
    for entity_id, config in triggers.items():
        condition = str(config.get("condition", "on"))
        weight_value = int(config.get("weight", 0))

        # Construct template line with explicit string formatting
        template_line = (
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set scores.total = scores.total + {weight_value} %}}"
            "{% endif %}"
        )
        template_lines.append(template_line)

    # Add manual override check
    template_lines.append(
        f"{{% if is_state('input_boolean.{area_name}_occupied_override', 'on') %}}"
        "  {% set scores.total = scores.total + 5 %}"
        "{% endif %}"
    )

    # Final condition check
    template_lines.append("{{ scores.total >= 3 }}")

    return "\n".join(template_lines)


def generate_confidence_score_template(triggers: Dict[str, OccupancyTrigger], area_name: AreaName) -> str:
    """Generate the template for confidence score calculation."""
    # Construct template lines
    template_lines = ["{% set scores = namespace(total=0) %}"]

    # Add scoring logic for each trigger
    for entity_id, config in triggers.items():
        condition = str(config.get("condition", "on"))
        weight_value = int(config.get("weight", 0))

        # Construct template line with explicit string formatting
        template_line = (
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set scores.total = scores.total + {weight_value} %}}"
            "{% endif %}"
        )
        template_lines.append(template_line)

    # Add manual override score
    template_lines.append(
        f"{{% if is_state('input_boolean.{area_name}_occupied_override', 'on') %}}"
        "  {% set scores.total = scores.total + 5 %}"
        "{% endif %}"
    )

    # Return total score
    template_lines.append("{{ scores.total }}")

    return "\n".join(template_lines)


def generate_active_triggers_template(triggers: Dict[str, OccupancyTrigger], area_name: AreaName) -> str:
    """Generate the template for active triggers list."""
    # Construct template lines
    template_lines = ["{% set triggers = [] %}"]

    # Add check for each trigger
    for entity_id, config in triggers.items():
        condition = str(config.get("condition", "on"))
        description_value = str(config.get("description", ""))

        # Construct template line with explicit string formatting
        template_line = (
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set triggers = triggers + ['{description_value}'] %}}"
            "{% endif %}"
        )
        template_lines.append(template_line)

    # Add manual override check
    template_lines.append(
        f"{{% if is_state('input_boolean.{area_name}_occupied_override', 'on') %}}"
        "  {% set triggers = triggers + ['Manual Override'] %}"
        "{% endif %}"
    )

    # Join triggers
    template_lines.append("{{ triggers|join(', ') }}")

    return "\n".join(template_lines)
