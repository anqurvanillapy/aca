#!/usr/bin/env python3

"""Aca setup script"""

from setuptools import setup, find_packages
from aca import __VERSION__

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="acalang",
    version=__VERSION__,
    description="Aca, a functional programming language, and shitty toy",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    author="AnqurVanillapy",
    author_email="anqurvanillapy@gmail.com",
    url="https://github.com/anqurvanillapy/acalang",
    entry_points={"console_scripts": ["aca=aca:main"]},
    packages=find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
