"""
Setup script for logos-cli package.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="logos-cli",
    version="0.1.0",
    description="CLI client for Logos with local LLM integration",
    long_description="Command-line interface for interacting with Logos using various local LLMs",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "logos-cli=cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)