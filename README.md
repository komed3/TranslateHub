# TranslateHub

![GitHub Release](https://img.shields.io/github/v/release/komed3/TranslateHub?include_prereleases&display_name=release&style=for-the-badge)
![GitHub License](https://img.shields.io/github/license/komed3/TranslateHub?style=for-the-badge)

**TranslateHub** is a cross-platform translation management tool for i18n projects, designed to make translation work quick and efficient. It supports multiple languages and namespaces, allowing for easily manage and edit translation files. Features include automatic sorting and synchronization of translation keys across languages using a schema that stores the structure of all namespaces. The app provides a user-friendly interface for editing translations, tracking progress, searching and filtering, exporting, and comprehensive statistics.

This app was originally created to manage translations for the [@Airportmap](https://github.com/airportmap) projects, but should support other Node.js apps using [i18next](https://npmjs.com/package/i18next) or similar structures as well.

## Installation

Clone the repository:

```bash
git clone https://github.com/komed3/TranslateHub.git
cd TranslateHub
```

### Prerequisites

Python 3.9 or higher  
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

**Just a reminder:** Windows defender might flag the executable as suspicious. This is a common false positive for PyInstaller builds. You can safely ignore this warning. If you want to take further investigation, submit the executable to Microsoft Security following [these instructions](https://www.microsoft.com/en-us/wdsi/filesubmission).

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

When you first run **TranslateHub**, you'll be prompted to select the translation root directory. This should be the directory containing your language folders (e.g., `en-US`, `de-DE`). Once selected, the app will load all languages and namespaces. If the project does not contain a valid schema directory, one will be created automatically.

In the options dialog (`File` -> `Options`), you can configure settings such as the auto-save interval, JSON file compressing, and much more.

Closing out of the project via menu (`File` -> `Close Project`) will close the app and remove the current project folder. Normal closing will keep the current folder loaded for the next start.

If you want to export translations, use the `Export` option in the `File` menu. This will create a zip file containing languages and namespaces of your choice.

### Working with Languages and Namespaces

Languages and namespaces are displayed in the left panel. You can manage them by adding, renaming, or deleting. To add a new language or namespace, use the `Add` button next to the respective header. Rename or delete by right-clicking on the item.

Additionally, you can filter the list of languages and namespaces using the filter boxes above each list.

### Editing Translations

To edit translations, use the editor in the right panel. If the editor is empty, ensure you have selected a language and namespace from the left panel.

Now, you can edit translations directly in the text fields. Changes are highlighted and automatically saved periodically (if activated). Use the "Hide Translated Values" checkbox to focus on untranslated content. To search for specific keys or values, use the filter box at the top of the editor.

### Managing Translation Keys

Translation keys will be synced across all languages and sorted alphabetically when saving. You can manage keys by adding, renaming, or deleting them.

To add a new key, select a language and namespace, then click the `Add Key` button. To rename or delete a key, use the buttons next to each key in the editor.

Syncing will happen automatically. You can also manually synchronize keys using the `Synchronize Keys` option in the `Edit` menu.

### Statistics

The **TranslateHub** app provides a comprehensive statistics view to help you track the translation progress. Progress bars at the bottom of the left panel shows the progress for the currently selected language and namespace.

If you want to see overall statistics, use the `Statistics` option in the `Edit` menu. This dialog shows translation progress for all languages and namespaces as a matrix. Double-click on a cell to navigate directly to that language and namespace.

Via `Missing Translations` in the `Edit` menu, you can see all missing translations across all languages and namespaces in a list view. Alternatively, you can search within all translations using the `Search` option.

### API Translations

Translating using external APIs is supported but in early `ALPHA` and not jet tested. You can configure API settings in the options dialog (`File` -> `Options`). After that, click the `Translate` button in the editor to translate a missing key for the currently selected language and namespace.

## Project Structure

**TranslateHub** expects your translation files to be organized as follows:

```
root_directory/
├── _schema/
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
