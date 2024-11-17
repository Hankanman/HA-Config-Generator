# area_config_generator/generators/occupancy.py
from typing import Dict, List


def generate_occupancy_config(features: Dict[str, bool]) -> List[Dict]:
    """Generate occupancy detection configuration."""
    area_name = features["area_name"]

    # Build list of occupancy triggers and their weights
    triggers = {}

    if features["motion_sensor"]:
        triggers[f"binary_sensor.{area_name}_motion"] = {
            "weight": 2,
            "description": "Motion Detected",
        }

    if features["door_sensor"]:
        triggers[f"binary_sensor.{area_name}_door_contact"] = {
            "weight": 1,
            "description": "Door Closed",
            "condition": "off",  # Door closed state
        }

    if "computer" in features.get("devices", []):
        triggers[f"binary_sensor.{area_name}_pc_active"] = {
            "weight": 3,
            "description": "PC Active",
        }

    if "tv" in features.get("devices", []):
        triggers[f"binary_sensor.{area_name}_tv_state"] = {
            "weight": 2,
            "description": "TV Active",
        }

    # Special device handling
    if any(
        device in features.get("devices", []) for device in ["appliance", "bathroom"]
    ):
        triggers[f"binary_sensor.{area_name}_device_active"] = {
            "weight": 2,
            "description": "Device Active",
        }

    # Generate template configuration
    return [
        {
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Occupancy",
                    "unique_id": f"{area_name}_occupancy",
                    "device_class": "occupancy",
                    "state": generate_occupancy_state_template(triggers),
                    "attributes": {
                        "confidence_score": generate_confidence_score_template(
                            triggers
                        ),
                        "active_triggers": generate_active_triggers_template(triggers),
                    },
                }
            ]
        }
    ]


def generate_occupancy_state_template(triggers: Dict) -> str:
    """Generate the template for occupancy state calculation."""
    template_lines = ["{% set scores = namespace(total=0) %}"]

    # Add scoring logic for each trigger
    for entity_id, config in triggers.items():
        condition = config.get("condition", "on")
        template_lines.append(
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set scores.total = scores.total + {config['weight']} %}}"
            "{% endif %}"
        )

    # Add manual override check
    template_lines.extend(
        [
            "{% if is_state('input_boolean.${area_name}_occupied_override', 'on') %}",
            "  {% set scores.total = scores.total + 5 %}",
            "{% endif %}",
            "",
            "{{ scores.total >= 3 }}",
        ]
    )

    return "\n".join(template_lines)


def generate_confidence_score_template(triggers: Dict) -> str:
    """Generate the template for confidence score calculation."""
    template_lines = ["{% set scores = namespace(total=0) %}"]

    # Add scoring logic for each trigger
    for entity_id, config in triggers.items():
        condition = config.get("condition", "on")
        template_lines.append(
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set scores.total = scores.total + {config['weight']} %}}"
            "{% endif %}"
        )

    # Add manual override score
    template_lines.extend(
        [
            "{% if is_state('input_boolean.${area_name}_occupied_override', 'on') %}",
            "  {% set scores.total = scores.total + 5 %}",
            "{% endif %}",
            "",
            "{{ scores.total }}",
        ]
    )

    return "\n".join(template_lines)


def generate_active_triggers_template(triggers: Dict) -> str:
    """Generate the template for active triggers list."""
    template_lines = ["{% set triggers = [] %}"]

    # Add check for each trigger
    for entity_id, config in triggers.items():
        condition = config.get("condition", "on")
        template_lines.append(
            f"{{% if is_state('{entity_id}', '{condition}') %}}"
            f"  {{% set triggers = triggers + ['{config['description']}'] %}}"
            "{% endif %}"
        )

    # Add manual override check
    template_lines.extend(
        [
            "{% if is_state('input_boolean.${area_name}_occupied_override', 'on') %}",
            "  {% set triggers = triggers + ['Manual Override'] %}",
            "{% endif %}",
            "",
            "{{ triggers|join(', ') }}",
        ]
    )

    return "\n".join(template_lines)
