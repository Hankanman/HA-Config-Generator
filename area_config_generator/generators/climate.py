from typing import Dict, List, Mapping, Optional, TypedDict, Union


class SensorDict(TypedDict, total=False):
    name: Optional[str]
    unique_id: Optional[str]
    state: Optional[str]
    device_class: Optional[str]
    state_class: Optional[str]
    unit_of_measurement: Optional[str]
    attributes: Optional[Dict[str, str]]


def generate_climate_config(features: Mapping[str, Union[str, bool]]) -> List[Dict[str, List[SensorDict]]]:
    """Generate climate control configuration."""
    area_name = str(features.get("area_name", ""))
    components: List[Dict[str, List[SensorDict]]] = []

    # Generate temperature differential sensor
    components.extend(generate_temperature_sensors(area_name))

    # Generate humidity sensors if applicable
    if features.get("humidity_sensor"):
        components.extend(generate_humidity_sensors(area_name))

    # Add window state monitoring if applicable
    if features.get("window_sensor"):
        components.extend(generate_window_monitoring(area_name))

    return components


def generate_temperature_sensors(area_name: str) -> List[Dict[str, List[SensorDict]]]:
    """Generate temperature monitoring sensors."""
    return [
        {
            "sensor": [
                {
                    "name": f"{area_name.title()} Temperature Differential",
                    "unique_id": f"{area_name}_temp_differential",
                    "state": generate_temp_differential_template(area_name),
                    "device_class": "temperature",
                    "state_class": "measurement",
                    "unit_of_measurement": "°C",
                    "attributes": {
                        "current_temp": f"{{{{ states('sensor.{area_name}_temperature')|float(20) }}}}",
                        "target_temp": f"{{{{ state_attr('climate.{area_name}', 'temperature')|float(20) }}}}",
                        "mode": f"{{{{ state_attr('climate.{area_name}', 'hvac_action')|default('off') }}}}",
                    },
                }
            ],
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Temperature Rising",
                    "unique_id": f"{area_name}_temp_rising",
                    "device_class": "heat",
                    "state": generate_temp_trend_template(area_name, rising=True),
                },
                {
                    "name": f"{area_name.title()} Temperature Falling",
                    "unique_id": f"{area_name}_temp_falling",
                    "device_class": "cold",
                    "state": generate_temp_trend_template(area_name, rising=False),
                },
            ],
        }
    ]


def generate_humidity_sensors(area_name: str) -> List[Dict[str, List[SensorDict]]]:
    """Generate humidity monitoring sensors."""
    return [
        {
            "sensor": [
                {
                    "name": f"{area_name.title()} Humidity Change",
                    "unique_id": f"{area_name}_humidity_change",
                    "state": generate_humidity_change_template(area_name),
                    "device_class": "humidity",
                    "state_class": "measurement",
                    "unit_of_measurement": "%",
                    "attributes": {
                        "current_humidity": f"{{{{ states('sensor.{area_name}_humidity')|float(50) }}}}",
                        "average_humidity": f"{{{{ states('sensor.{area_name}_average_humidity')|float(50) }}}}",
                    },
                }
            ],
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} High Humidity",
                    "unique_id": f"{area_name}_high_humidity",
                    "device_class": "moisture",
                    "state": generate_humidity_threshold_template(area_name, high=True),
                }
            ],
        }
    ]


def generate_window_monitoring(area_name: str) -> List[Dict[str, List[SensorDict]]]:
    """Generate window state monitoring configuration."""
    return [
        {
            "binary_sensor": [
                {
                    "name": f"{area_name.title()} Windows Open",
                    "unique_id": f"{area_name}_windows_open",
                    "device_class": "window",
                    "state": f"{{{{ is_state('binary_sensor.{area_name}_window_contact', 'on') }}}}",
                    "attributes": {"climate_impact": generate_window_climate_impact_template(area_name)},
                }
            ]
        }
    ]


def generate_temp_differential_template(area_name: str) -> str:
    """Generate template for temperature differential calculation."""
    return "\n".join(
        [
            f"{{% set current = states('sensor.{area_name}_temperature')|float(20) %}}",
            f"{{% set target = state_attr('climate.{area_name}', 'temperature')|float(20) %}}",
            "{{ (current - target)|round(1) }}",
        ]
    )


def generate_temp_trend_template(area_name: str, rising: bool = True) -> str:
    """Generate template for temperature trend detection."""
    operator = ">" if rising else "<"
    return "\n".join(
        [
            f"{{% set current = states('sensor.{area_name}_temperature')|float(20) %}}",
            f"{{% set previous = state_attr('sensor.{area_name}_temperature', 'previous_value')|float(20) %}}",
            "{% set threshold = 0.2 %}",
            f"{{{{ (current - previous) {operator} threshold }}}}",
        ]
    )


def generate_humidity_change_template(area_name: str) -> str:
    """Generate template for humidity change calculation."""
    return "\n".join(
        [
            f"{{% set current = states('sensor.{area_name}_humidity')|float(50) %}}",
            f"{{% set average = states('sensor.{area_name}_average_humidity')|float(50) %}}",
            "{{ ((current - average) / average * 100)|round(1) }}",
        ]
    )


def generate_humidity_threshold_template(area_name: str, high: bool = True) -> str:
    """Generate template for humidity threshold detection."""
    operator = ">" if high else "<"
    threshold = 75 if high else 30
    return "\n".join(
        [
            f"{{% set current = states('sensor.{area_name}_humidity')|float(50) %}}",
            f"{{{{ current {operator} {threshold} }}}}",
        ]
    )


def generate_window_climate_impact_template(area_name: str) -> str:
    """Generate template for assessing window state impact on climate."""
    return "\n".join(
        [
            f"{{% set temp_diff = states('sensor.{area_name}_temp_differential')|float(0) %}}",
            f"{{% set window_open = is_state('binary_sensor.{area_name}_window_contact', 'on') %}}",
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
