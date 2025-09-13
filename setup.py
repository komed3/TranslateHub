"""
TranslateHub - Setup Script
Installs the application and its dependencies
"""

from setuptools import setup, find_packages

setup(
    name= "TranslateHub",
    version= "0.1.1",
    description= "Cross-platform Translation Management Tool for i18n projects",
    author= "komed3 (Paul Köhler)",
    packages= find_packages(),
    include_package_data= True,
    install_requires= [
        "PyQt6>=6.9.0",
    ],
    entry_points= {
        "console_scripts": [
            "translatehub=src.main:main",
        ],
    },
    classifiers= [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires= ">=3.9",
)
