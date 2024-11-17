# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ha-area-config-generator",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Home Assistant Area Configuration Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ha-area-config-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "PyYAML>=6.0",
        "rich>=10.0.0",  # For pretty CLI output
    ],
    entry_points={
        "console_scripts": [
            "generate-ha-config=area_config_generator.cli.interface:main",
        ],
    },
)
