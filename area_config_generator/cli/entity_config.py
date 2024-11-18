# area_config_generator/cli/entity_config.py

from typing import List

import click

from ..utils.types import EntityConfig, EntityIds, Features


def confirm_entity_id(domain: str, suggested_id: str, description: str) -> str:
    """Confirm entity ID with user.

    Args:
        domain: The entity domain
        suggested_id: Suggested entity ID
        description: Description of the entity

    Returns:
        Confirmed entity ID
    """
    # Ensure entity ID is lowercase
    suggested_id = suggested_id.lower()
    default_id = f"{domain}.{suggested_id}"

    # First try with just a prompt that allows empty (default) value
    entity_id = click.prompt(
        f"Please confirm the {description} entity ID", default=default_id, show_default=True, type=str
    ).strip()

    # If they just hit enter or entered the default exactly, return it
    if not entity_id or entity_id == default_id:
        return default_id

    # Otherwise validate their custom entry
    while True:
        # Strip any quotes they may have added
        entity_id = entity_id.strip('"').strip("'")
        # Ensure entity ID is lowercase
        entity_id = entity_id.lower()

        # Validate format
        if "." not in entity_id:
            click.echo(f"Invalid format. Must be in format: {domain}.entity_id")
            entity_id = click.prompt("Please try again", default=default_id, type=str)
            continue

        prefix = entity_id.split(".", 1)[0]
        if prefix != domain:
            click.echo(f"Invalid domain. Must start with: {domain}")
            entity_id = click.prompt("Please try again", default=default_id, type=str)
            continue

        return entity_id


def get_entity_config(area_name: str, features: Features) -> EntityIds:
    """Get and confirm all entity IDs for the area.

    Args:
        area_name: The name of the area
        features: The features configuration

    Returns:
        Dictionary of confirmed entity IDs
    """
    # Explicitly type the list of entities
    entities: List[EntityConfig] = []
    confirmed_entities: EntityIds = {}

    # Normalize area_name for entity IDs while preserving original for display
    normalized_area_name = area_name.lower()

    # Basic entities
    if features.get("climate_control"):
        entities.append({"domain": "climate", "suggested_id": normalized_area_name, "description": "climate control"})

    if features.get("motion_sensor"):
        entities.append(
            {"domain": "binary_sensor", "suggested_id": f"{normalized_area_name}_motion", "description": "motion sensor"}
        )

    if features.get("door_sensor"):
        entities.append(
            {
                "domain": "binary_sensor",
                "suggested_id": f"{normalized_area_name}_door_contact",
                "description": "door contact sensor",
            }
        )

    if features.get("temperature_sensor"):
        entities.append(
            {"domain": "sensor", "suggested_id": f"{normalized_area_name}_temperature", "description": "temperature sensor"}
        )

    # Lighting entities
    if features.get("smart_lighting"):
        entities.extend(
            [
                {"domain": "light", "suggested_id": f"{normalized_area_name}_lights", "description": "area light group"},
                {
                    "domain": "scene",
                    "suggested_id": f"{normalized_area_name}_light_scene",
                    "description": "default light scene",
                },
            ]
        )

    # Add device-specific entities
    devices = features.get("devices", [])
    for device in devices:
        if device == "computer":
            entities.extend(
                [
                    {
                        "domain": "sensor",
                        "suggested_id": f"{normalized_area_name}_pc_power",
                        "description": "PC power sensor",
                    },
                    {
                        "domain": "binary_sensor",
                        "suggested_id": f"{normalized_area_name}_pc_active",
                        "description": "PC state sensor",
                    },
                ]
            )
        elif device == "tv":
            entities.extend(
                [
                    {
                        "domain": "sensor",
                        "suggested_id": f"{normalized_area_name}_tv_power",
                        "description": "TV power sensor",
                    },
                    {
                        "domain": "binary_sensor",
                        "suggested_id": f"{normalized_area_name}_tv_active",
                        "description": "TV state sensor",
                    },
                ]
            )
        elif device in ["appliance", "bathroom", "kitchen"]:
            entities.extend(
                [
                    {
                        "domain": "sensor",
                        "suggested_id": f"{normalized_area_name}_{device}_power",
                        "description": f"{device.title()} power sensor",
                    },
                    {
                        "domain": "binary_sensor",
                        "suggested_id": f"{normalized_area_name}_{device}_active",
                        "description": f"{device.title()} state sensor",
                    },
                ]
            )

    # Add input_boolean entities
    entities.append(
        {
            "domain": "input_boolean",
            "suggested_id": f"{normalized_area_name}_occupied_override",
            "description": "occupancy override switch",
        }
    )

    # Get confirmation for each entity
    click.echo("\nPlease confirm the entity IDs for your configuration:")
    for entity_config in entities:
        # Use a more robust key extraction method
        key = entity_config["suggested_id"].split("_")[-1]

        # Ensure the key is unique
        base_key = key
        counter = 1
        while key in confirmed_entities:
            key = f"{base_key}_{counter}"
            counter += 1

        confirmed_entities[key] = confirm_entity_id(
            entity_config["domain"], entity_config["suggested_id"], entity_config["description"]
        )

    return confirmed_entities
