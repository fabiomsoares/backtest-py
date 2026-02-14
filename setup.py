"""Setup script for backtest-py package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="backtest-py",
    version="0.1.0",
    author="Fabio Soares",
    author_email="",
    description="A simple but sophisticated backtesting framework in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fabiomsoares/backtest-py",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "notebooks", "docs", "scripts"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "black>=21.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "pytest-cov>=2.12.0",
        ],
        "api": [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "pydantic>=1.8.0",
        ],
        "cli": [
            "click>=8.0.0",
            "rich>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "backtest=cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
