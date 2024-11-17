# area_config_generator/utils/yaml_writer.py
import yaml
import os
from typing import Dict


def write_yaml_config(area_name: str, config: Dict) -> None:
    """Write the configuration to a YAML file."""
    # Create output directory if it doesn't exist
    os.makedirs("generated_configs", exist_ok=True)

    # Write configuration
    output_path = f"generated_configs/{area_name}.yaml"
    with open(output_path, "w") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)
