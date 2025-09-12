# TranslateHub

A cross-platform translation management tool for i18n projects, designed to make translation work quick and efficient. It supports multiple languages and namespaces, allowing you to easily manage and edit your translation files. Features include automatic sorting of keys, synchronization of translation keys across languages, progress tracking, and a comprehensive statistics view.

## Features

**Language Management**: Create, delete, and rename language folders  
**Namespace Management**: Create, delete, and rename namespace files  
**Translation Editing**: Edit translations with a user-friendly interface  
**Key Management**: Add, delete, and rename translation keys  
**Automatic Sorting**: Keys are automatically sorted alphabetically when saving  
**Synchronization**: Ensure all languages have the same translation keys  
**Progress Tracking**: Visual progress bars for languages and namespaces  
**Statistics View**: Comprehensive statistics showing translation progress across all languages and namespaces  
**Filtering**: Search and filter languages and namespaces for quick access  
**Hide Translated**: Option to hide already translated values to focus on untranslated content  
**Auto-save**: Changes are automatically saved periodically  
**Cross-platform**: Works on Windows and Linux

## Installation

### Prerequisites

Python 3.8 or higher  
pip (Python package installer)

### Windows

Clone the repository:

```bash
git clone https://github.com/komed3/TranslateHub.git
cd TranslateHub
```

Install the application:

```bash
pip install -e .
```

Run the application:

```bash
python translatehub.py
```

### Linux

Clone the repository:

```bash
git clone https://github.com/komed3/TranslateHub.git
cd TranslateHub
```

Install the application:

```bash
pip install -e .
```

Make the launcher script executable:

```bash
chmod +x translatehub.py
```

Run the application:

```bash
./translatehub.py
```

## Building Standalone Executables

You can create a standalone executable using PyInstaller for both Windows and Linux. Just run the provided script. The executable will be in the `dist/TranslateHub` directory.

### Windows

```bash
pip install pyinstaller
./build_windows.bat
```

### Linux

```bash
pip install pyinstaller
chmod +x build_linux.sh
./build_linux.sh
```
