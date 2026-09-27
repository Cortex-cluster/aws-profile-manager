#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="aws-profile-manager",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "aws-profile-manager = aws_profile_manager.main:main",
        ],
    },
)
