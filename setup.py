"""
TranslateHub - Setup Script
Installation script for TranslateHub
"""

from setuptools import setup, find_packages

from .translatehub import __version__

# Read README for long description
with open( "README.md", "r", encoding= "utf-8" ) as fh :
    long_description = fh.read()

setup(
    name= "translatehub",
    version= __version__,
    author= "komed3 (Paul Köhler)",
    author_email= "webmaster@komed3.de",
    description= "Cross-platform translation management tool for i18n projects",
    long_description= long_description,
    long_description_content_type= "text/markdown",
    url= "https://github.com/komed3/TranslateHub",
    packages= find_packages(),
    classifiers= [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Utilities",
        "Topic :: Text Processing :: Linguistic"
    ],
    python_requires= ">=3.8",
    install_requires= [
        "PyQt6>=6.0.0",
        "requests>=2.25.0"
    ],
    entry_points= {
        "console_scripts": [
            "translatehub=translatehub:main"
        ]
    },
    include_package_data= True,
    package_data= {
        "translatehub": [
            "resources/icon.ico",
            "resources/icon.png"
        ]
    }
)
