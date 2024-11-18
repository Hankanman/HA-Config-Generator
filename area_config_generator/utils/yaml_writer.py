import os
from typing import Any, Dict, Optional

import yaml
from yaml.dumper import Dumper
from yaml.nodes import ScalarNode

from .types import AreaName, ConfigType, ProcessedConfigValue, ProcessedDict, convert_to_processed_config_value


class CustomDumper(yaml.SafeDumper):
    """Custom YAML dumper with template handling."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        """Override to ensure proper template indentation."""
        return super().increase_indent(flow, False)


def safe_represent_scalar(dumper: Dumper, tag: str, value: str, style: Optional[str] = None) -> ScalarNode:
    return dumper.represent_scalar(tag, value, style=style)  # type: ignore


def template_presenter(dumper: CustomDumper, data: str) -> ScalarNode:
    """Custom presenter for Jinja2 templates.

    Args:
        dumper: The YAML dumper instance
        data: The template string to process

    Returns:
        ScalarNode: The YAML scalar node with processed template
    """
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
    """Write the configuration to a YAML file with proper template handling.

    Args:
        area_name: The name of the area being configured
        config: The configuration to write
    """
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


def process_config(config: ConfigType) -> ProcessedDict:
    """Process configuration to properly handle templates and special characters.

    Args:
        config: The configuration dictionary to process

    Returns:
        The processed configuration dictionary
    """
    processed: ProcessedDict = {}

    for key, value in config.items():
        processed[key] = [_process_config_item(item) for item in value]

    return processed


def _process_config_item(item: Dict[str, Any]) -> Dict[str, ProcessedConfigValue]:
    """Process a single configuration item.

    Args:
        item: A configuration item dictionary

    Returns:
        Processed configuration item
    """
    processed_item: Dict[str, ProcessedConfigValue] = {}
    for component_type, components in item.items():
        # Explicitly convert to ProcessedConfigValue
        processed_item[component_type] = convert_to_processed_config_value(components)
    return processed_item


def process_template(value: str) -> str:
    """Process a template string.

    Args:
        value: The template string to process

    Returns:
        The processed template string
    """
    if "{{" in value or "{%" in value:
        # Remove unnecessary outer quotes
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        # Replace doubled quotes
        value = value.replace("''", "'")
    return value


def validate_config(config: ConfigType) -> None:
    """Validate the configuration structure.

    Args:
        config: The configuration to validate

    Raises:
        ValueError: If the configuration is invalid
    """
    if not config:
        raise ValueError("Configuration cannot be empty")

    for area_name, area_config in config.items():
        if not area_name:
            raise ValueError("Area name cannot be empty")

        if not area_config:
            raise ValueError(f"Configuration for area {area_name} cannot be empty")

        for item in area_config:
            if not item:
                raise ValueError(f"Configuration item in {area_name} cannot be empty")

            for component_type, components in item.items():
                if not components:
                    raise ValueError(f"Component {component_type} in {area_name} cannot be empty")
