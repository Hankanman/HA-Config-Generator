# area_config_generator/utils/yaml_writer.py
import os

import yaml

from .types import AreaName, ConfigType


def write_yaml_config(area_name: AreaName, config: ConfigType) -> None:
    """Write the configuration to a YAML file."""
    # Create output directory if it doesn't exist
    os.makedirs("generated_configs", exist_ok=True)

    # Write configuration
    output_path = f"generated_configs/{area_name}.yaml"
    with open(output_path, "w") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)
