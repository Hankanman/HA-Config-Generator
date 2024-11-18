import os
from typing import Any, Dict, List, Optional, TypeGuard, TypeVar, Union, cast

import yaml
from typing_extensions import NotRequired, TypedDict
from yaml.nodes import ScalarNode

from .types import (
    ConfigType,
    ProcessedConfigValue,
    ProcessedDictValue,
    TemplateItem,
    TemplateList,
    convert_to_processed_config_value,
)

T = TypeVar("T")


class ComponentAttributes(TypedDict):
    attributes: NotRequired[Dict[str, str]]
    state: NotRequired[str]


class ComponentDict(TypedDict):
    name: str
    unique_id: str
    attributes: NotRequired[Dict[str, str]]
    state: NotRequired[str]


ComponentList = List[Union[ComponentDict, Dict[str, Any]]]


def is_valid_component(component: Any) -> TypeGuard[ComponentDict]:
    if not isinstance(component, dict):
        return False
    component = cast(Dict[str, Any], component)
    name = component.get("name")
    unique_id = component.get("unique_id")
    return isinstance(name, str) and isinstance(unique_id, str)


class CustomDumper(yaml.SafeDumper):
    """Custom YAML dumper with improved template handling."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        """Override to ensure proper template indentation."""
        return super().increase_indent(flow, False)


def clean_template_string(value: Optional[Union[str, Any]]) -> str:
    """Clean template string by fixing quote issues and special characters."""
    if value is None:
        return ""

    str_value = str(value)

    # Handle special cases for attributes
    if str_value.startswith("'{") and str_value.endswith("}'"):
        # Remove outer single quotes for dictionary-like strings
        str_value = str_value[1:-1]

    # Fix double apostrophes
    str_value = str_value.replace("''", "'")

    # Handle special characters
    str_value = str_value.replace("°C", "°C")

    # Clean up any remaining unnecessary escaping
    str_value = str_value.replace("\\'", "'")

    return str_value


def template_presenter(dumper: CustomDumper, data: Union[str, Any]) -> ScalarNode:
    """Present template strings in YAML with proper formatting."""
    data = clean_template_string(data)

    # Determine if we need block style
    style: Optional[str] = None
    if "\n" in data:
        style = "|"
    elif "{{" in data or "{%" in data:
        # Use literal style for template expressions
        style = ">"

    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)  # type: ignore


def process_template_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Process template strings in attributes with improved quote handling."""
    processed_attributes: Dict[str, Any] = {}

    for key, value in attributes.items():
        if isinstance(value, str):
            # Clean the template string
            cleaned_value = clean_template_string(value)
            # For template expressions, ensure proper formatting
            if "{{" in cleaned_value or "{%" in cleaned_value:
                processed_attributes[key] = cleaned_value
            else:
                processed_attributes[key] = value
        else:
            processed_attributes[key] = value

    return processed_attributes


def _process_config_item(item: Union[TemplateItem, TemplateConfigItem]) -> TemplateItem:
    """Process a single configuration item with improved template handling."""
    processed_item: TemplateItem = {}

    if not item:
        return processed_item

    for component_type, components in item.items():
        if not isinstance(components, list):
            continue

        processed_components: List[Dict[str, Any]] = []
        typed_components = cast(ComponentList, components)

        for raw_component in typed_components:
            if not is_valid_component(raw_component):
                continue

            processed_component: Dict[str, Any] = {
                "name": raw_component["name"],
                "unique_id": raw_component["unique_id"],
            }

            # Process attributes with improved template handling
            if "attributes" in raw_component:
                attributes = raw_component["attributes"]
                if attributes:
                    processed_component["attributes"] = process_template_attributes(attributes)

            # Process state templates
            if "state" in raw_component:
                state = raw_component["state"]
                if state:
                    processed_component["state"] = clean_template_string(state)

            # Copy remaining fields
            for key, value in raw_component.items():
                if key not in ("attributes", "state", "name", "unique_id"):
                    processed_component[key] = value

            processed_components.append(processed_component)

        if processed_components:
            processed_item[component_type] = processed_components

    return processed_item


def write_yaml_config(area_name: str, config: ConfigType) -> None:
    """Write the configuration to a YAML file with improved template handling."""
    # Register the template presenter
    CustomDumper.add_representer(str, template_presenter)

    # Ensure output directory exists
    os.makedirs("generated_configs", exist_ok=True)

    # Process the configuration
    processed_config = process_config(config)

    # Write the YAML file
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
    """Process configuration with improved template handling."""
    processed: ProcessedDictValue = {}

    for area_name, area_config in config.items():
        area_processed: ProcessedDictValue = {}

        # Process templates
        if "template" in area_config:
            templates = cast(TemplateList, area_config["template"])
            processed_templates: List[ProcessedConfigValue] = []

            for template_item in templates:
                processed_item = _process_config_item(template_item)
                processed_templates.append(convert_to_processed_config_value(processed_item))

            area_processed["template"] = convert_to_processed_config_value(processed_templates)

        # Process input configurations
        if "input_number" in area_config:
            area_processed["input_number"] = convert_to_processed_config_value(area_config["input_number"])

        if "input_boolean" in area_config:
            area_processed["input_boolean"] = convert_to_processed_config_value(area_config["input_boolean"])

        processed[area_name] = area_processed

    return processed


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
                    for comp in components:
                        if not is_valid_component(comp):
                            raise ValueError(f"Invalid component in {component_type}: {comp}")

        if "input_number" in area_config and not area_config["input_number"]:
            raise ValueError(f"input_number configuration in {area_name} cannot be empty")

        if "input_boolean" in area_config and not area_config["input_boolean"]:
            raise ValueError(f"input_boolean configuration in {area_name} cannot be empty")
