# area_config_generator/generators/power.py
"""Power monitoring configuration generator."""

from typing import Any, Dict, List

from ..utils.types import PowerComponent


def generate_power_config(devices: List[str]) -> List[Dict[str, List[Dict[str, Any]]]]:
    """Generate power monitoring configuration."""
    components: List[Dict[str, List[Dict[str, Any]]]] = []

    # Map device types to their power components
    device_components: Dict[str, PowerComponent] = get_device_power_components(devices)

    # Generate total power sensor
    total_power: Dict[str, List[Dict[str, Any]]] = generate_total_power_sensor(device_components)
    components.append(total_power)

    # Generate daily energy sensor
    daily_energy: Dict[str, List[Dict[str, Any]]] = generate_daily_energy_sensor(device_components)
    components.append(daily_energy)

    return components


def get_device_power_components(devices: List[str]) -> Dict[str, PowerComponent]:
    """Map devices to their power monitoring components."""
    components: Dict[str, PowerComponent] = {}

    for device in devices:
        if device == "computer":
            components.update(
                {
                    "pc": {
                        "power_entity": "sensor.pc_power",
                        "energy_entity": "sensor.pc_daily_energy",
                        "description": "PC/Computer",
                    },
                    "monitors": {
                        "power_entity": "sensor.monitors_power",
                        "energy_entity": "sensor.monitors_daily_energy",
                        "description": "Monitors",
                    },
                    "desk": {
                        "power_entity": "sensor.desk_power",
                        "energy_entity": "sensor.desk_daily_energy",
                        "description": "Desk Equipment",
                    },
                }
            )

        elif device == "tv":
            components.update(
                {
                    "tv": {
                        "power_entity": "sensor.tv_power",
                        "energy_entity": "sensor.tv_daily_energy",
                        "description": "Television",
                    },
                    "entertainment": {
                        "power_entity": "sensor.entertainment_power",
                        "energy_entity": "sensor.entertainment_daily_energy",
                        "description": "Entertainment System",
                    },
                }
            )

        elif device == "appliance":
            components.update(
                {
                    "appliance": {
                        "power_entity": "sensor.appliance_power",
                        "energy_entity": "sensor.appliance_daily_energy",
                        "description": "Major Appliance",
                    }
                }
            )

        elif device == "bathroom":
            components.update(
                {
                    "bathroom": {
                        "power_entity": "sensor.bathroom_power",
                        "energy_entity": "sensor.bathroom_daily_energy",
                        "description": "Bathroom Equipment",
                    }
                }
            )

        elif device == "kitchen":
            components.update(
                {
                    "kitchen_major": {
                        "power_entity": "sensor.kitchen_major_power",
                        "energy_entity": "sensor.kitchen_major_daily_energy",
                        "description": "Major Kitchen Appliances",
                    },
                    "kitchen_small": {
                        "power_entity": "sensor.kitchen_small_power",
                        "energy_entity": "sensor.kitchen_small_daily_energy",
                        "description": "Small Kitchen Appliances",
                    },
                }
            )

    # Add extras/misc power for any area with powered devices
    if components:
        components["extras"] = {
            "power_entity": "sensor.extras_power",
            "energy_entity": "sensor.extras_daily_energy",
            "description": "Other Devices",
        }

    return components


def generate_total_power_sensor(components: dict[str, PowerComponent]) -> Dict[str, List[Dict[str, Any]]]:
    """Generate the total power sensor configuration."""
    # Build the power calculation template
    power_template: List[str] = ["{% set components = ["]

    # Add each component's power entity
    power_entities: List[str] = [f"'{comp['power_entity']}'" for comp in components.values()]
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


def generate_daily_energy_sensor(components: dict[str, PowerComponent]) -> Dict[str, List[Dict[str, Any]]]:
    """Generate the daily energy sensor configuration."""
    # Build the energy calculation template
    energy_template: List[str] = ["{% set components = ["]

    # Add each component's energy entity
    energy_entities: List[str] = [f"'{comp['energy_entity']}'" for comp in components.values()]
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
                "attributes": {"last_reset": "{{ now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() }}"},
            }
        ]
    }
