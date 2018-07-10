#!/usr/bin/env python3

"""Aca setup script"""

from setuptools import setup
from aca import __VERSION__

setup(
    name="acalang",
    version=__VERSION__,
    description="Aca, a functional programming language, and shitty toy",
    license="MIT",
    author="AnqurVanillapy",
    author_email="anqurvanillapy@gmail.com",
    url="https://github.com/anqurvanillapy/acalang",
    entry_points={"console_scripts": ["aca=aca:main"]},
)
