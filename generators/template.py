# area_config_generator/generators/template.py
"""Template generation utilities for Home Assistant configurations."""

from typing import Dict, List, Union, Any


class TemplateGenerator:
    """Utility class for generating Home Assistant templates."""

    @staticmethod
    def state_template(entity_id: str, transform: str = None) -> str:
        """Generate a template to get an entity's state with optional transform."""
        template = f"states('{entity_id}')"
        if transform:
            template += f"|{transform}"
        return "{{{{ {} }}}}".format(template)

    @staticmethod
    def attribute_template(
        entity_id: str, attribute: str, transform: str = None
    ) -> str:
        """Generate a template to get an entity's attribute with optional transform."""
        template = f"state_attr('{entity_id}', '{attribute}')"
        if transform:
            template += f"|{transform}"
        return "{{{{ {} }}}}".format(template)

    @staticmethod
    def condition_template(conditions: List[Dict[str, Any]]) -> str:
        """Generate a template for condition checking."""
        template_lines = []

        for condition in conditions:
            if condition.get("type") == "state":
                template_lines.append(
                    f"{{% if is_state('{condition['entity']}', '{condition['state']}') %}}"
                )
            elif condition.get("type") == "numeric_state":
                operator = condition.get("operator", ">")
                template_lines.append(
                    f"{{% if states('{condition['entity']}')|float(0) {operator} {condition['value']} %}}"
                )
            elif condition.get("type") == "template":
                template_lines.append(f"{{% if {condition['value']} %}}")

        return "\n".join(template_lines)

    @staticmethod
    def value_comparison(
        value1: str, operator: str, value2: str, default: str = None
    ) -> str:
        """Generate a template for comparing values."""
        if default:
            value1 += f"|default({default})"
            value2 += f"|default({default})"
        return "{{{{ {} {} {} }}}}".format(value1, operator, value2)

    @staticmethod
    def calculation_template(calculation: str, round_digits: int = None) -> str:
        """Generate a template for calculations."""
        template = "{{{{ {} }}}}".format(calculation)
        if round_digits is not None:
            template = "{{{{ {} | round({}) }}}}".format(calculation, round_digits)
        return template

    @staticmethod
    def generate_complex_template(template_parts: List[Dict[str, Any]]) -> str:
        """Generate a complex template from multiple parts."""
        template_lines = []

        for part in template_parts:
            if part.get("type") == "set":
                template_lines.append(
                    "{{% set {} = {} %}}".format(part["variable"], part["value"])
                )
            elif part.get("type") == "if":
                template_lines.append("{{% if {} %}}".format(part["condition"]))
                template_lines.append("  " + part["then"])
                if "else" in part:
                    template_lines.append("{% else %}")
                    template_lines.append("  " + part["else"])
                template_lines.append("{% endif %}")
            elif part.get("type") == "for":
                template_lines.append(
                    "{{% for {} in {} %}}".format(part["var"], part["list"])
                )
                template_lines.append("  " + part["do"])
                template_lines.append("{% endfor %}")
            elif part.get("type") == "raw":
                template_lines.append(part["value"])

        return "\n".join(template_lines)


class AttributeGenerator:
    """Utility class for generating entity attributes."""

    @staticmethod
    def generate_attributes(attributes: Dict[str, Union[str, Dict]]) -> Dict[str, str]:
        """Generate attribute templates from configuration."""
        generated = {}

        for key, value in attributes.items():
            if isinstance(value, str):
                generated[key] = value
            elif isinstance(value, dict):
                if value.get("type") == "template":
                    generated[key] = value["template"]
                elif value.get("type") == "state":
                    generated[key] = TemplateGenerator.state_template(
                        value["entity"], value.get("transform")
                    )
                elif value.get("type") == "attribute":
                    generated[key] = TemplateGenerator.attribute_template(
                        value["entity"], value["attribute"], value.get("transform")
                    )

        return generated


class DeviceClassHelper:
    """Helper class for managing device classes and units."""

    DEVICE_CLASSES = {
        "temperature": {
            "device_class": "temperature",
            "state_class": "measurement",
            "unit_of_measurement": "°C",
        },
        "humidity": {
            "device_class": "humidity",
            "state_class": "measurement",
            "unit_of_measurement": "%",
        },
        "power": {
            "device_class": "power",
            "state_class": "measurement",
            "unit_of_measurement": "W",
        },
        "energy": {
            "device_class": "energy",
            "state_class": "total_increasing",
            "unit_of_measurement": "kWh",
        },
        "current": {
            "device_class": "current",
            "state_class": "measurement",
            "unit_of_measurement": "A",
        },
        "voltage": {
            "device_class": "voltage",
            "state_class": "measurement",
            "unit_of_measurement": "V",
        },
        "illuminance": {
            "device_class": "illuminance",
            "state_class": "measurement",
            "unit_of_measurement": "lx",
        },
    }

    @classmethod
    def get_class_config(cls, device_class: str) -> Dict[str, str]:
        """Get the configuration for a device class."""
        return cls.DEVICE_CLASSES.get(device_class, {})

    @classmethod
    def apply_device_class(cls, config: Dict, device_class: str) -> Dict:
        """Apply device class configuration to an entity config."""
        class_config = cls.get_class_config(device_class)
        config.update(class_config)
        return config
