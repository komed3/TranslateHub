# TranslateHub

**TranslateHub** is a cross-platform translation management tool for i18n projects, designed to make translation work quick and efficient. It supports multiple languages and namespaces, allowing you to easily manage and edit your translation files. Features include automatic sorting of keys, synchronization of translation keys across languages, progress tracking, and a comprehensive statistics view.

This app was originally created to manage translations for the [@Airportmap](https://github.com/airportmap) projects, but should support other Node.js apps using i18next as well.

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

Clone the repository:

```bash
git clone https://github.com/komed3/TranslateHub.git
cd TranslateHub
```

### Prerequisites

Python 3.8 or higher  
pip (Python package installer)

### Windows

```bash
pip install -e .
python translatehub.py
```

### Linux

```bash
pip install -e .
chmod +x translatehub.py
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

## Usage

### Getting Started

When you first run **TranslateHub**, you'll be prompted to select your translation root directory. This should be the directory containing your language folders (e.g., `en-US`, `de-DE`). Once selected, the app will load all languages and namespaces.

### Working with Languages and Namespaces

Languages and namespaces are displayed in the left panel. You can manage them by adding, renaming, or deleting. To add a new language or namespace, use the `Add` button next to the respective header. Rename or delete by right-clicking on the item.

Additionally, you can filter the list of languages and namespaces using the filter boxes above each list.

### Editing Translations

To edit translations, use the editor in the right panel. If the editor is empty, ensure you have selected a language and namespace from the left panel.

Now, you can edit translations directly in the text fields. Changes are automatically saved periodically. Use the "Hide Translated Values" checkbox to focus on untranslated content.

### Managing Translation Keys

Translation keys will be synced across all languages and sorted alphabetically when saving. You can manage keys by adding, renaming, or deleting them.

To add a new key, select a language and namespace, then click the `Add Key` button. To rename or delete a key, use the buttons next to each key in the editor.

Syncing will happen automatically. You can also manually synchronize keys using the `Synchronize Keys` option in the `Edit` menu.

### Statistics

The **TranslateHub** app provides a comprehensive statistics view to help you track the translation progress. Progress bars at the bottom of the left panel shows the progress for the currently selected language and namespace.

If you want to see overall statistics, use the `Show Statistics` option in the `Edit` menu. This dialog shows translation progress for all languages and namespaces as a matrix. Double-click on a cell to navigate directly to that language and namespace.

## Project Structure

**TranslateHub** expects your translation files to be organized as follows:

```
root_directory/
├── en-US/
│   ├── app.generic.json
│   ├── app.home.json
│   └── ...
├── de-DE/
│   ├── app.generic.json
│   ├── app.home.json
│   └── ...
└── ...
```

Each JSON file should contain key-value pairs for translations:

```json
{
  "search": "Search",
  "title": "Welcome to our application",
  ...
}
```

## License

This project is licensed under the [MIT License](LICENSE).  
© 2025 [@komed3](https://github.com/komed3) (Paul Köhler)
