from typing import Any, Dict, List

from ..utils.types import Features, OccupancyTrigger


def generate_occupancy_config(features: Features) -> List[Dict[str, List[Dict[str, Any]]]]:
    """Generate occupancy detection configuration."""
    area_name = str(features.get("area_name", ""))
    normalized_area_name = str(features.get("normalized_area_name", area_name.lower()))
    entity_ids = features.get("entity_ids", {})

    # Build list of occupancy triggers and their weights
    triggers: Dict[str, OccupancyTrigger] = {}

    if features.get("motion_sensor"):
        motion_entity = entity_ids.get("motion", f"binary_sensor.{normalized_area_name}_motion")
        triggers[motion_entity] = {
            "weight": 2,
            "description": "Motion Detected",
        }

    if features.get("door_sensor"):
        door_entity = entity_ids.get("door", f"binary_sensor.{normalized_area_name}_door_contact")
        triggers[door_entity] = {
            "weight": 1,
            "description": "Door Closed",
            "condition": "off",  # Door closed state
        }

    devices = features.get("devices", [])
    for device in devices:
        if device == "computer":
            pc_entity = entity_ids.get("pc_active", f"binary_sensor.{normalized_area_name}_pc_active")
            triggers[pc_entity] = {
                "weight": 3,
                "description": "PC Active",
            }

        if device == "tv":
            tv_entity = entity_ids.get("tv_active", f"binary_sensor.{normalized_area_name}_tv_active")
            triggers[tv_entity] = {
                "weight": 2,
                "description": "TV Active",
            }

        # Special device handling
        if device in ("appliance", "bathroom"):
            device_entity = entity_ids.get(f"{device}_active", f"binary_sensor.{normalized_area_name}_{device}_active")
            triggers[device_entity] = {
                "weight": 2,
                "description": f"{device.title()} Active",
            }

    # Get override entity
    override_entity = entity_ids.get("occupied_override", f"input_boolean.{normalized_area_name}_occupied_override")

    return [
        {
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Occupancy",
                    "unique_id": f"{normalized_area_name}_occupancy",
                    "device_class": "occupancy",
                    "state": generate_occupancy_state_template(triggers, override_entity),
                    "attributes": {
                        "confidence_score": generate_confidence_score_template(triggers, override_entity),
                        "active_triggers": generate_active_triggers_template(triggers, override_entity),
                    },
                }
            ]
        }
    ]


def generate_occupancy_state_template(triggers: Dict[str, OccupancyTrigger], override_entity: str) -> str:
    """Generate the template for occupancy state calculation."""
    template_lines = ["{% set scores = namespace(total=0) %}"]

    # Add scoring logic for each trigger
    for entity_id, config in triggers.items():
        condition = str(config.get("condition", "on"))
        weight = int(config.get("weight", 0))
        template_lines.append(
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set scores.total = scores.total + {weight} %}}"
            "{% endif %}"
        )

    # Add manual override check
    template_lines.append(
        f"{{% if is_state('{override_entity}', 'on') %}}" "  {% set scores.total = scores.total + 5 %}" "{% endif %}"
    )

    # Final condition check
    template_lines.append("{{ scores.total >= 3 }}")

    return "\n".join(template_lines)


def generate_confidence_score_template(triggers: Dict[str, OccupancyTrigger], override_entity: str) -> str:
    """Generate the template for confidence score calculation."""
    template_lines = ["{% set scores = namespace(total=0) %}"]

    # Add scoring logic for each trigger
    for entity_id, config in triggers.items():
        condition = str(config.get("condition", "on"))
        weight = int(config.get("weight", 0))
        template_lines.append(
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set scores.total = scores.total + {weight} %}}"
            "{% endif %}"
        )

    # Add manual override score
    template_lines.append(
        f"{{% if is_state('{override_entity}', 'on') %}}" "  {% set scores.total = scores.total + 5 %}" "{% endif %}"
    )

    # Return total score
    template_lines.append("{{ scores.total }}")

    return "\n".join(template_lines)


def generate_active_triggers_template(triggers: Dict[str, OccupancyTrigger], override_entity: str) -> str:
    """Generate the template for active triggers list."""
    template_lines = ["{% set triggers = [] %}"]

    # Add check for each trigger
    for entity_id, config in triggers.items():
        condition = str(config.get("condition", "on"))
        description = str(config.get("description", ""))
        template_lines.append(
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set triggers = triggers + ['{description}'] %}}"
            "{% endif %}"
        )

    # Add manual override check
    template_lines.append(
        f"{{% if is_state('{override_entity}', 'on') %}}"
        "  {% set triggers = triggers + ['Manual Override'] %}"
        "{% endif %}"
    )

    # Join triggers
    template_lines.append("{{ triggers|join(', ') }}")

    return "\n".join(template_lines)
