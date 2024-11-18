from typing import Dict, List

from ..utils.types import Features


def generate_climate_config(features: Features) -> List[Dict[str, List[SensorConfig]]]:
    """Generate climate control configuration."""
    area_name = str(features.get("area_name", ""))
    normalized_area_name = str(features.get("normalized_area_name", area_name.lower()))
    entity_ids = features.get("entity_ids", {})
    components: List[Dict[str, List[SensorConfig]]] = []

    # Get confirmed entity IDs with fallbacks
    climate_entity = entity_ids.get("climate", f"climate.{normalized_area_name}")
    temp_entity = entity_ids.get("temperature", f"sensor.{normalized_area_name}_temperature")

    # Generate temperature differential sensor
    components.extend(
        generate_temperature_sensors(
            area_name=area_name,
            normalized_area_name=normalized_area_name,
            climate_entity=climate_entity,
            temp_entity=temp_entity,
        )
    )

    # Generate humidity sensors if applicable
    if features.get("humidity_sensor"):
        humidity_entity = entity_ids.get("humidity", f"sensor.{normalized_area_name}_humidity")
        components.extend(
            generate_humidity_sensors(
                area_name=area_name, normalized_area_name=normalized_area_name, humidity_entity=humidity_entity
            )
        )

    # Add window state monitoring if applicable
    if features.get("window_sensor"):
        window_entity = entity_ids.get("window", f"binary_sensor.{normalized_area_name}_window")
        components.extend(
            generate_window_monitoring(
                area_name=area_name,
                normalized_area_name=normalized_area_name,
                window_entity=window_entity,
                temp_entity=temp_entity,
            )
        )

    return components


def generate_temperature_sensors(
    area_name: str, normalized_area_name: str, climate_entity: str, temp_entity: str
) -> List[Dict[str, List[SensorConfig]]]:
    """Generate temperature monitoring sensors."""
    return [
        {
            "sensor": [
                {
                    "name": f"{area_name.title()} Temperature Differential",
                    "unique_id": f"{normalized_area_name}_temp_differential",
                    "state": generate_temp_differential_template(temp_entity, climate_entity),
                    "device_class": "temperature",
                    "state_class": "measurement",
                    "unit_of_measurement": "°C",
                    "attributes": {
                        "current_temp": f"{{{{ states('{temp_entity}')|float(20) }}}}",
                        "target_temp": f"{{{{ state_attr('{climate_entity}', 'temperature')|float(20) }}}}",
                        "mode": f"{{{{ state_attr('{climate_entity}', 'hvac_action')|default('off') }}}}",
                    },
                }
            ],
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Temperature Rising",
                    "unique_id": f"{normalized_area_name}_temp_rising",
                    "device_class": "heat",
                    "state": generate_temp_trend_template(temp_entity, rising=True),
                    "attributes": {},
                },
                {
                    "name": f"{area_name.title()} Temperature Falling",
                    "unique_id": f"{normalized_area_name}_temp_falling",
                    "device_class": "cold",
                    "state": generate_temp_trend_template(temp_entity, rising=False),
                    "attributes": {},
                },
            ],
        }
    ]


def generate_humidity_sensors(
    area_name: str, normalized_area_name: str, humidity_entity: str
) -> List[Dict[str, List[SensorConfig]]]:
    """Generate humidity monitoring sensors."""
    return [
        {
            "sensor": [
                {
                    "name": f"{area_name.title()} Humidity Change",
                    "unique_id": f"{normalized_area_name}_humidity_change",
                    "state": generate_humidity_change_template(humidity_entity),
                    "device_class": "humidity",
                    "state_class": "measurement",
                    "unit_of_measurement": "%",
                    "attributes": {
                        "current_humidity": f"{{{{ states('{humidity_entity}')|float(50) }}}}",
                        "average_humidity": (f"{{{{ states('sensor.{humidity_entity}_average')|float(50) }}}}"),
                    },
                }
            ],
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} High Humidity",
                    "unique_id": f"{normalized_area_name}_high_humidity",
                    "device_class": "moisture",
                    "state": generate_humidity_threshold_template(humidity_entity, high=True),
                    "attributes": {},  # Added empty attributes
                }
            ],
        }
    ]


def generate_window_monitoring(
    area_name: str, normalized_area_name: str, window_entity: str, temp_entity: str
) -> List[Dict[str, List[SensorConfig]]]:
    """Generate window state monitoring configuration."""
    return [
        {
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Windows Open",
                    "unique_id": f"{normalized_area_name}_windows_open",
                    "device_class": "window",
                    "state": f"{{{{ is_state('{window_entity}', 'on') }}}}",
                    "attributes": {
                        "climate_impact": generate_window_climate_impact_template(area_name, window_entity, temp_entity)
                    },
                }
            ]
        }
    ]


def generate_temp_differential_template(temp_entity: str, climate_entity: str) -> str:
    """Generate template for temperature differential calculation."""
    return "\n".join(
        [
            f"{{% set current = states('{temp_entity}')|float(20) %}}",
            f"{{% set target = state_attr('{climate_entity}', 'temperature')|float(20) %}}",
            "{{ (current - target)|round(1) }}",
        ]
    )


def generate_temp_trend_template(temp_entity: str, rising: bool = True) -> str:
    """Generate template for temperature trend detection."""
    operator = ">" if rising else "<"
    return "\n".join(
        [
            f"{{% set current = states('{temp_entity}')|float(20) %}}",
            f"{{% set previous = state_attr('{temp_entity}', 'previous_value')|float(20) %}}",
            "{% set threshold = 0.2 %}",
            f"{{{{ (current - previous) {operator} threshold }}}}",
        ]
    )


def generate_humidity_change_template(humidity_entity: str) -> str:
    """Generate template for humidity change calculation."""
    return "\n".join(
        [
            f"{{% set current = states('{humidity_entity}')|float(50) %}}",
            f"{{% set average = states('sensor.{humidity_entity}_average')|float(50) %}}",
            "{{ ((current - average) / average * 100)|round(1) }}",
        ]
    )


def generate_humidity_threshold_template(humidity_entity: str, high: bool = True) -> str:
    """Generate template for humidity threshold detection."""
    operator = ">" if high else "<"
    threshold = 75 if high else 30
    return "\n".join(
        [
            f"{{% set current = states('{humidity_entity}')|float(50) %}}",
            f"{{{{ current {operator} {threshold} }}}}",
        ]
    )


def generate_window_climate_impact_template(area_name: str, window_entity: str, temp_entity: str) -> str:
    """Generate template for assessing window state impact on climate."""
    return "\n".join(
        [
            f"{{% set temp_diff = states('sensor.{area_name}_temp_differential')|float(0) %}}",
            f"{{% set window_open = is_state('{window_entity}', 'on') %}}",
            "{% if window_open %}",
            "  {% if temp_diff > 2 %}",
            "    'heating_loss'",
            "  {% elif temp_diff < -2 %}",
            "    'cooling_loss'",
            "  {% else %}",
            "    'minimal'",
            "  {% endif %}",
            "{% else %}",
            "  'none'",
            "{% endif %}",
        ]
    )
