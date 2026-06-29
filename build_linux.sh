#!/bin/bash

echo "Building TranslateHub standalone executable for Linux ..."
echo ""

# Check if PyInstaller is installed
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "PyInstaller is not installed. Installing now ..."
    pip install pyinstaller
fi

# Create resources directory if it doesn't exist
if [ ! -d "resources" ]; then
    mkdir resources
fi

echo "Building executable ..."

# Build the executable
pyinstaller --name TranslateHub \
    --clean \
    --noupx \
    --windowed \
    --icon=resources/icon.png \
    --add-data "resources:resources" \
    --exclude-module unittest \
    --exclude-module pdb \
    --exclude-module difflib \
    --exclude-module doctest \
    --onefile translatehub.py

echo ""
echo "Build complete! The executable is in the dist/TranslateHub directory."
echo ""
