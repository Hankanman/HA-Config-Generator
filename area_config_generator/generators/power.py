from typing import Any, Dict, List

from ..utils.types import EntityIds, Features, PowerComponent


def generate_power_config(features: Features) -> List[Dict[str, List[Dict[str, Any]]]]:
    """Generate power monitoring configuration."""
    components: List[Dict[str, List[Dict[str, Any]]]] = []

    area_name = str(features.get("area_name", ""))
    normalized_area_name = str(features.get("normalized_area_name", area_name.lower()))
    entity_ids = features.get("entity_ids", {})
    devices = features.get("devices", [])

    # Map device types to their power components
    device_components: Dict[str, PowerComponent] = get_device_power_components(
        area_name=area_name, normalized_area_name=normalized_area_name, devices=devices, entity_ids=entity_ids
    )

    # Only generate power sensors if we have components
    if device_components:
        # Generate total power sensor
        total_power = generate_total_power_sensor(device_components)
        components.append(total_power)

        # Generate daily energy sensor
        daily_energy = generate_daily_energy_sensor(device_components)
        components.append(daily_energy)

    return components


def get_device_power_components(
    area_name: str, normalized_area_name: str, devices: List[str], entity_ids: EntityIds
) -> Dict[str, PowerComponent]:
    """Map devices to their power monitoring components."""
    components: Dict[str, PowerComponent] = {}

    for device in devices:
        if device == "computer":
            pc_power = entity_ids.get("pc_power", f"sensor.{normalized_area_name}_pc_power")
            monitors_power = entity_ids.get("monitors_power", f"sensor.{normalized_area_name}_monitors_power")
            desk_power = entity_ids.get("desk_power", f"sensor.{normalized_area_name}_desk_power")

            components.update(
                {
                    "pc": {
                        "power_entity": pc_power,
                        "energy_entity": pc_power.replace("_power", "_daily_energy"),
                        "description": "PC/Computer",
                    },
                    "monitors": {
                        "power_entity": monitors_power,
                        "energy_entity": monitors_power.replace("_power", "_daily_energy"),
                        "description": "Monitors",
                    },
                    "desk": {
                        "power_entity": desk_power,
                        "energy_entity": desk_power.replace("_power", "_daily_energy"),
                        "description": "Desk Equipment",
                    },
                }
            )

        elif device == "tv":
            tv_power = entity_ids.get("tv_power", f"sensor.{normalized_area_name}_tv_power")
            entertainment_power = entity_ids.get("entertainment_power", f"sensor.{normalized_area_name}_entertainment_power")

            components.update(
                {
                    "tv": {
                        "power_entity": tv_power,
                        "energy_entity": tv_power.replace("_power", "_daily_energy"),
                        "description": "Television",
                    },
                    "entertainment": {
                        "power_entity": entertainment_power,
                        "energy_entity": entertainment_power.replace("_power", "_daily_energy"),
                        "description": "Entertainment System",
                    },
                }
            )

        elif device == "appliance":
            appliance_power = entity_ids.get("appliance_power", f"sensor.{normalized_area_name}_appliance_power")
            components.update(
                {
                    "appliance": {
                        "power_entity": appliance_power,
                        "energy_entity": appliance_power.replace("_power", "_daily_energy"),
                        "description": "Major Appliance",
                    }
                }
            )

        elif device == "bathroom":
            bathroom_power = entity_ids.get("bathroom_power", f"sensor.{normalized_area_name}_bathroom_power")
            components.update(
                {
                    "bathroom": {
                        "power_entity": bathroom_power,
                        "energy_entity": bathroom_power.replace("_power", "_daily_energy"),
                        "description": "Bathroom Equipment",
                    }
                }
            )

        elif device == "kitchen":
            kitchen_power = entity_ids.get("kitchen_power", f"sensor.{normalized_area_name}_kitchen_power")

            if kitchen_power:
                components.update(
                    {
                        "kitchen_major": {
                            "power_entity": f"{kitchen_power}_major",
                            "energy_entity": f"{kitchen_power}_major_daily_energy",
                            "description": "Major Kitchen Appliances",
                        },
                        "kitchen_small": {
                            "power_entity": f"{kitchen_power}_small",
                            "energy_entity": f"{kitchen_power}_small_daily_energy",
                            "description": "Small Kitchen Appliances",
                        },
                    }
                )

    return components


def generate_total_power_sensor(components: Dict[str, PowerComponent]) -> Dict[str, List[Dict[str, Any]]]:
    """Generate the total power sensor configuration."""
    # Build the power calculation template
    power_template: List[str] = ["{% set components = ["]

    # Add each component's power entity
    power_entities: List[str] = [f"'{comp['power_entity']}'" for comp in components.values()]
    if power_entities:
        power_template.append("    " + ",\n    ".join(power_entities))

    power_template.extend(
        [
            "] %}",
            "",
            "{% set total = namespace(power=0) %}",
            "{% for component in components %}",
            "  {% set total.power = total.power + states(component)|float(0) %}",
            "{% endfor %}",
            "{{ total.power|round(2) }}",
        ]
    )

    # Build attributes template with individual component values
    attributes: Dict[str, str] = {}
    for key, comp in components.items():
        attributes[key] = f"{{{{ states('{comp['power_entity']}')|float(0)|round(2) }}}}"

    return {
        "sensor": [
            {
                "name": "Total Power",
                "unique_id": "total_power",
                "state": "\n".join(power_template),
                "device_class": "power",
                "state_class": "measurement",
                "unit_of_measurement": "W",
                "attributes": attributes,
            }
        ]
    }


def generate_daily_energy_sensor(components: Dict[str, PowerComponent]) -> Dict[str, List[Dict[str, Any]]]:
    """Generate the daily energy sensor configuration."""
    # Build the energy calculation template
    energy_template: List[str] = ["{% set components = ["]

    # Add each component's energy entity
    energy_entities: List[str] = [f"'{comp['energy_entity']}'" for comp in components.values()]
    if energy_entities:
        energy_template.append("    " + ",\n    ".join(energy_entities))

    energy_template.extend(
        [
            "] %}",
            "",
            "{% set total = namespace(energy=0) %}",
            "{% for component in components %}",
            "  {% set total.energy = total.energy + states(component)|float(0) %}",
            "{% endfor %}",
            "{{ total.energy|round(3) }}",
        ]
    )

    return {
        "sensor": [
            {
                "name": "Daily Energy",
                "unique_id": "daily_energy",
                "state": "\n".join(energy_template),
                "device_class": "energy",
                "state_class": "total_increasing",
                "unit_of_measurement": "kWh",
                "attributes": {"last_reset": ("{{ now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() }}")},
            }
        ]
    }
