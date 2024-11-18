# area_config_generator/utils/validation.py

from typing import Any, Optional, TypeVar, cast

from .types import BinarySensorTemplate, DeviceConfig, FanTemplate, Features, LightingDefaults, SensorTemplate

T = TypeVar("T")


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, context: Optional[str] = None):
        """Initialize validation error.

        Args:
            message: The error message
            context: Optional context about where the error occurred
        """
        self.context = context
        super().__init__(f"{context + ': ' if context else ''}{message}")


def validate_features(features: Features) -> None:
    """Validate the features configuration.

    Args:
        features: The features configuration to validate

    Raises:
        ValidationError: If the features configuration is invalid
    """
    required_fields = ["area_name", "normalized_area_name"]
    for field in required_fields:
        if field not in features:
            raise ValidationError(f"Missing required field: {field}", "features")

    if features.get("smart_lighting"):
        if "lighting_defaults" not in features:
            raise ValidationError("Smart lighting enabled but no defaults provided", "features")
        if lighting_defaults := features.get("lighting_defaults"):
            validate_lighting_defaults(lighting_defaults)

    if features.get("power_monitoring"):
        if not features.get("devices"):
            raise ValidationError("Power monitoring enabled but no devices specified", "features")


def validate_lighting_defaults(defaults: LightingDefaults) -> None:
    """Validate lighting default settings.

    Args:
        defaults: The lighting defaults to validate

    Raises:
        ValidationError: If the lighting defaults are invalid
    """
    required_fields = ["brightness", "color_temp", "transition"]
    for field in required_fields:
        if field not in defaults:
            raise ValidationError(f"Missing required field: {field}", "lighting_defaults")

    brightness = defaults.get("brightness")
    if not isinstance(brightness, int) or brightness < 0 or brightness > 100:
        raise ValidationError("Brightness must be between 0 and 100", "lighting_defaults")

    color_temp = defaults.get("color_temp")
    if not isinstance(color_temp, str) or color_temp not in ["warm", "cool", "neutral"]:
        raise ValidationError("Color temperature must be warm, cool, or neutral", "lighting_defaults")

    transition = defaults.get("transition")
    if not isinstance(transition, int) or transition < 0:
        raise ValidationError("Transition time must be non-negative", "lighting_defaults")


def validate_binary_sensor(config: BinarySensorTemplate) -> None:
    """Validate a binary sensor configuration.

    Args:
        config: The binary sensor configuration to validate

    Raises:
        ValidationError: If the configuration is invalid
    """
    if not config.get("device_class"):
        raise ValidationError("Binary sensor must have device_class", "binary_sensor config")

    if "state" in config:
        validate_template(config["state"], "binary_sensor state template")

    if "attributes" in config:
        for name, template in config["attributes"].items():
            validate_template(template, f"binary_sensor attribute {name}")


def validate_sensor(config: SensorTemplate) -> None:
    """Validate a sensor configuration.

    Args:
        config: The sensor configuration to validate

    Raises:
        ValidationError: If the configuration is invalid
    """
    if not config.get("unit_of_measurement"):
        raise ValidationError("Sensor must have unit_of_measurement", "sensor config")

    if "state" in config:
        validate_template(config["state"], "sensor state template")

    if "attributes" in config:
        for name, template in config["attributes"].items():
            validate_template(template, f"sensor attribute {name}")


def validate_template(template: str, context: str) -> None:
    """Validate a template string.

    Args:
        template: The template string to validate
        context: Context information for error messages

    Raises:
        ValidationError: If the template is invalid
    """
    if not template:
        raise ValidationError("Template must be a string", context)

    # Check for matching Jinja2 braces
    if template.count("{{") != template.count("}}"):
        raise ValidationError("Mismatched template braces", context)
    if template.count("{%") != template.count("%}"):
        raise ValidationError("Mismatched template tags", context)

    # Check for common template syntax errors
    if "}}" in template and not ("{{" in template):
        raise ValidationError("Found closing brace without opening brace", context)
    if "%}" in template and not ("{%" in template):
        raise ValidationError("Found closing tag without opening tag", context)


def validate_fan_config(config: FanTemplate) -> None:
    """Validate a fan configuration.

    Args:
        config: The fan configuration to validate

    Raises:
        ValidationError: If the fan configuration is invalid
    """
    if config["platform"] != "template":
        raise ValidationError("Fan config must have platform: template", "fan config")

    for fan_id, fan_config in config["fans"].items():
        # Validate required fields
        required_fields = ["friendly_name", "value_template", "speed_template", "turn_on", "turn_off", "set_speed", "speeds"]
        for field in required_fields:
            if field not in fan_config:
                raise ValidationError(f"Fan {fan_id} missing required field: {field}", "fan config")

        # Validate templates
        validate_template(fan_config["value_template"], f"fan {fan_id} value_template")
        validate_template(fan_config["speed_template"], f"fan {fan_id} speed_template")


def validate_device_config(config: DeviceConfig) -> None:
    """Validate a device configuration.

    Args:
        config: The device configuration to validate

    Raises:
        ValidationError: If the device configuration is invalid
    """
    if "template" not in config:
        raise ValidationError("Device config must have template section", "device config")

    for template_item in config["template"]:
        for component_type, components in template_item.items():
            if not components:
                raise ValidationError(f"Components for {component_type} must be a list", "device config")

            for component in components:
                if component_type == "binary_sensor":
                    validate_binary_sensor(cast(BinarySensorTemplate, component))
                elif component_type == "sensor":
                    validate_sensor(cast(SensorTemplate, component))
                elif component_type == "fan":
                    validate_fan_config(cast(FanTemplate, component))


def ensure_valid_config(config: Any, context: str = "") -> None:
    """Ensure configuration is valid, raising an error if not.

    This function serves as the main entry point for configuration validation.

    Args:
        config: The configuration to validate
        context: Optional context for error messages

    Raises:
        ValidationError: If the configuration is invalid
    """
    if isinstance(config, dict):
        if "features" in config:
            validate_features(cast(Features, config["features"]))
        if "template" in config:
            validate_device_config(cast(DeviceConfig, config))
    else:
        raise ValidationError(f"Invalid configuration type: {type(config)}", context)
