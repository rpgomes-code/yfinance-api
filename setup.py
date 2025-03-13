#!/usr/bin/env python
import os
from setuptools import setup, find_packages

# Get package version
with open("app/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"

# Get long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Get requirements
def get_requirements():
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
    return [r for r in requirements if not r.startswith("#") and r.strip()]

setup(
    name="yfinance-api",
    version=version,
    description="RESTful API for Yahoo Finance data using yfinance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="YFinance API Team",
    author_email="info@yfinance-api.com",
    url="https://github.com/yourusername/yfinance-api",
    packages=find_packages(exclude=["tests*", "docs", "scripts"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "yfinance-api=app.main:run",
        ],
    },
    project_urls={
        "Documentation": "https://yfinance-api.readthedocs.io/",
        "Source": "https://github.com/yourusername/yfinance-api",
        "Issues": "https://github.com/yourusername/yfinance-api/issues",
    },
)