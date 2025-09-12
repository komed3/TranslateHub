@echo off

echo Building TranslateHub standalone executable for Windows ...
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing now ...
    pip install pyinstaller
)

REM Create resources directory if it doesn't exist
if not exist resources mkdir resources

echo Building executable ...

REM Build the executable
pyinstaller --name TranslateHub ^
    --clean ^
    --noupx ^
    --windowed ^
    --icon=resources/icon.ico ^
    --add-data "resources;resources" ^
    --exclude-module unittest ^
    --exclude-module pdb ^
    --exclude-module difflib ^
    --exclude-module doctest ^
    translatehub.py

echo.
echo Build complete! The executable is in the dist/TranslateHub directory.
echo.

pause
