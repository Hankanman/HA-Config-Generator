# Home Assistant Area Configuration Generator

A Python tool to generate Home Assistant YAML configurations for different types of areas in your smart home setup.

## Features

- Interactive CLI for area configuration
- Support for various device types (computers, TVs, appliances, etc.)
- Intelligent template generation
- Power monitoring integration
- Climate control configuration
- Occupancy detection

## Installation

```bash
pip install ha-area-config-generator
```

## Usage

```bash
# Generate a new area configuration
generate-ha-config study

# The tool will interactively ask about the area features and devices
```

## Example Output

```yaml
study:
  template:
    - binary_sensor:
        - name: "Study Occupancy"
          unique_id: study_occupancy
          device_class: occupancy
          # ... (configuration continues)
```

## Supported Area Types

- Study/Office
- Living Room
- Bedroom
- Kitchen
- Bathroom
- Utility Room
- And more...

## Device Support

- Computers/PCs
- TVs/Entertainment Systems
- Major Appliances
- Bathroom Fixtures
- Kitchen Appliances
- Climate Control Systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
