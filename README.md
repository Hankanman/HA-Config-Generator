# Home Assistant Area Configuration Generator

A Python tool to generate Home Assistant YAML configurations for different types of areas in your smart home setup. This tool helps create standardized, feature-rich configurations for different room types while following Home Assistant best practices.

## Features

- Interactive CLI for area configuration
- Support for various device types:
  - Computers and workstations
  - TVs and entertainment systems
  - Major appliances (washing machines, dishwashers, etc.)
  - Bathroom fixtures
  - Kitchen appliances
- Smart template generation for:
  - Occupancy detection with confidence scoring
  - Power monitoring and energy tracking
  - Climate control and monitoring
  - Device-specific states and attributes
- Extensible architecture for adding new device types

## Installation

### For Users

```bash
pip install ha-area-config-generator
```

### For Developers

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ha-area-config-generator.git
cd ha-area-config-generator
```

2. Create and activate a virtual environment:

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate     # On Windows

# Or using conda
conda create -n ha-config python=3.9
conda activate ha-config
```

3. Install in development mode:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
# Generate a new area configuration
generate-ha-config study

# The tool will interactively ask about:
# - Area type and features
# - Present devices and sensors
# - Monitoring requirements
# - Control preferences
```

### Development Usage

#### Running Tests

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=area_config_generator
```

#### Code Style

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run formatters
black area_config_generator
isort area_config_generator

# Run linters
flake8 area_config_generator
mypy area_config_generator
```

#### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html
```

## Development

### Project Structure

```
area_config_generator/
├── __init__.py
├── cli/
│   ├── __init__.py
│   └── interface.py
├── generators/
│   ├── __init__.py
│   ├── occupancy.py
│   ├── power.py
│   ├── climate.py
│   └── template.py
├── devices/
│   ├── __init__.py
│   ├── computer.py
│   ├── tv.py
│   ├── bathroom.py
│   └── appliance.py
└── utils/
    ├── __init__.py
    └── yaml_writer.py
```

### Adding New Device Types

1. Create a new module in the `devices` directory:

```python
# area_config_generator/devices/new_device.py

def generate_device_config(area_name: str) -> Dict:
    """Generate configuration for the new device type."""
    return {
        'template': [{
            'binary_sensor': [{
                'name': f"{area_name.title()} Device State",
                'unique_id': f"{area_name}_device_state",
                # ... additional configuration
            }]
        }]
    }
```

2. Register the device type in `cli/interface.py`:

```python
device_options = {
    # ... existing options ...
    'new_device': "New Device Description"
}
```

3. Add device-specific templates in `generators/template.py` if needed.

### Running Type Checks

The project uses type hints throughout. Run type checks with:

```bash
mypy area_config_generator --strict
```

### Code Style Guide

This project follows:

- PEP 8 style guide
- Black code formatting
- Type hints throughout
- Google-style docstrings

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually (if needed)
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes:
   - Add tests for new functionality
   - Update documentation as needed
   - Follow the code style guide
4. Run tests and linters
5. Submit a pull request

### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the documentation with any new features
3. Ensure all tests pass and coverage remains high
4. Add your changes to CHANGELOG.md
5. The PR will be merged once you have at least one approval

## Example Output

```yaml
study:
  template:
    - binary_sensor:
        - name: "Study Occupancy"
          unique_id: study_occupancy
          device_class: occupancy
          state: >-
            {% set scores = namespace(total=0) %}

            {% if is_state('binary_sensor.study_pc_active', 'on') %}
              {% set scores.total = scores.total + 3 %}
            {% endif %}

            # ... additional configuration
```

## Supported Area Types

- Study/Office - Computer, desk setup, environment monitoring
- Living Room - Entertainment system, lighting, comfort monitoring
- Bedroom - Sleep monitoring, lighting control, climate
- Kitchen - Appliance monitoring, cooking detection
- Bathroom - Humidity monitoring, shower detection
- Utility Room - Appliance monitoring, power tracking

## Device Support

Each device type comes with specific features:

### Computer/PC

- Activity detection
- Power monitoring
- Temperature monitoring
- App state detection

### TV/Entertainment

- Media state tracking
- Power monitoring
- Source tracking
- Remote control integration

### Major Appliances

- State detection
- Power monitoring
- Cycle detection
- Runtime tracking

### Bathroom Fixtures

- Humidity monitoring
- Shower detection
- Fan control
- Water usage tracking

### Kitchen Appliances

- Cooking detection
- Temperature monitoring
- Power tracking
- State management

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Home Assistant community for inspiration and best practices
- Contributors to the project
- Users who provide feedback and suggestions
