"""
Setup script for Ice Experiment Data Analyzer
"""

from setuptools import setup, find_packages
import os

# Read README for long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ice-experiment-analyzer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@institution.edu",
    description="A Python tool for processing and analyzing ice mechanical testing data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ice-experiment-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
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
            "pytest-cov>=2.12.0",
            "black>=21.6.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ice-analyzer=ice_analyzer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ice_analyzer": ["config/*.yaml"],
    },
    keywords="ice mechanics data analysis CTD oceanography",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ice-experiment-analyzer/issues",
        "Source": "https://github.com/yourusername/ice-experiment-analyzer",
        "Documentation": "https://ice-experiment-analyzer.readthedocs.io/",
    },
)