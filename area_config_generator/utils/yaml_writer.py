# area_config_generator/utils/yaml_writer.py
import os
from typing import Optional, cast

import yaml
from yaml.dumper import Dumper
from yaml.nodes import ScalarNode

from .types import AreaName, ConfigType, ProcessedDictValue, TemplateItem, TemplateList, convert_to_processed_config_value


class CustomDumper(yaml.SafeDumper):
    """Custom YAML dumper with template handling."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        """Override to ensure proper template indentation."""
        return super().increase_indent(flow, False)


def safe_represent_scalar(dumper: Dumper, tag: str, value: str, style: Optional[str] = None) -> ScalarNode:
    """Safely represent a scalar value in YAML."""
    return dumper.represent_scalar(tag, value, style=style)  # type: ignore


def template_presenter(dumper: CustomDumper, data: str) -> ScalarNode:
    """Custom presenter for Jinja2 templates."""
    if data.startswith("'") and data.endswith("'"):
        data = data[1:-1]

    # Replace doubled single quotes with single quotes
    data = data.replace("''", "'")

    # Handle special characters
    data = data.replace("°C", "°C")

    # Use block style for multiline strings
    style: Optional[str] = "|" if "\n" in data else None

    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)  # type: ignore


def write_yaml_config(area_name: AreaName, config: ConfigType) -> None:
    """Write the configuration to a YAML file with proper template handling."""
    # Set up custom YAML handling
    CustomDumper.add_representer(str, template_presenter)

    # Create output directory if it doesn't exist
    os.makedirs("generated_configs", exist_ok=True)

    # Process the config to handle templates
    processed_config = process_config(config)

    # Write configuration with custom dumper
    output_path = f"generated_configs/{area_name}.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            processed_config,
            f,
            Dumper=CustomDumper,
            sort_keys=False,
            allow_unicode=True,
            width=120,
            default_flow_style=False,
        )


def process_config(config: ConfigType) -> ProcessedDictValue:
    """Process configuration to properly handle templates and special characters."""
    processed: ProcessedDictValue = {}

    for area_name, area_config in config.items():
        area_processed: ProcessedDictValue = {}

        # Process template items
        if "template" in area_config:
            templates = cast(TemplateList, area_config["template"])
            area_processed["template"] = convert_to_processed_config_value(
                [_process_config_item(item) for item in templates]
            )

        # Process input_number configurations
        if "input_number" in area_config:
            area_processed["input_number"] = convert_to_processed_config_value(area_config["input_number"])

        # Process input_boolean configurations
        if "input_boolean" in area_config:
            area_processed["input_boolean"] = convert_to_processed_config_value(area_config["input_boolean"])

        processed[area_name] = area_processed

    return processed


def _process_config_item(item: TemplateItem) -> ProcessedDictValue:
    """Process a single configuration item."""
    processed_item: ProcessedDictValue = {}
    for component_type, components in item.items():
        processed_item[component_type] = convert_to_processed_config_value(components)
    return processed_item


def process_template(value: str) -> str:
    """Process a template string."""
    if "{{" in value or "{%" in value:
        # Remove unnecessary outer quotes
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        # Replace doubled quotes
        value = value.replace("''", "'")
    return value


def validate_config(config: ConfigType) -> None:
    """Validate the configuration structure."""
    if not config:
        raise ValueError("Configuration cannot be empty")

    for area_name, area_config in config.items():
        if not area_name:
            raise ValueError("Area name cannot be empty")

        if not area_config:
            raise ValueError(f"Configuration for area {area_name} cannot be empty")

        if "template" in area_config:
            templates = cast(TemplateList, area_config["template"])
            for item in templates:
                if not item:
                    raise ValueError(f"Template item in {area_name} cannot be empty")

                for component_type, components in item.items():
                    if not components:
                        raise ValueError(f"Component {component_type} in {area_name} cannot be empty")

        if "input_number" in area_config and not area_config["input_number"]:
            raise ValueError(f"input_number configuration in {area_name} cannot be empty")

        if "input_boolean" in area_config and not area_config["input_boolean"]:
            raise ValueError(f"input_boolean configuration in {area_name} cannot be empty")
