# Changelog

All notable changes to TranslateHub will be documented in this file.

## [0.2.1] - 2026-03-09

### Updated
- **PyQt6** updated to 6.10.2
- **PyQt6-Qt6** updated to 6.10.2
- **altgraph** updated to 0.17.5
- **certifi** updated to 2026.2.25
- **charset-normalizer** updated to 3.4.5
- **idna** updated to 3.11
- **packaging** updated to 26.0
- **pyinstaller** updated to 6.19.0
- **pyinstaller-hooks-contrib** updated to 2026.2
- **setuptools** updated to 82.0.0
- **urllib3** updated to 2.6.3

## [0.2.0] - 2025-09-14

### Added
- Schema directory (`_schema`) for maintaining consistent translation structure.
- Export dialog for exporting translations to ZIP files.
- Options dialog for configuring application settings.
- Translation API integration for automatic translations [ALPHA].
- Modified translations highlighting in the editor.
- Jump-to-translation functionality from search and missing translations dialogs.

### Changed
- Status bar timeout for automatic message reset.
- Improved code organization with better abstraction and modularity.
- Non-editable tables in search and missing translations dialogs.

### Fixed
- Various UI issues and inconsistencies.
- Better handling of file operations.

## [0.1.1] - 2025-09-13

### Added
- Dialog showing missing translations for all languages and namespaces.
- Dialog to search translations in the loaded translation files.
- Dialog to check for application updates via GitHub API.
- New menu items to reach new dialogs.
- Options to close out the current project and reset all filter.
- Filter option for translation editor.

### Changed
- Rework project structure, move files.
- Abstracted dialog buttons to prevent duplicate code.
- Move statistic dialog "Refresh" button to box.
- Improved about box layout.

### Fixed
- Reset list widget filters when selecting lang/namespace pair.

## [0.1.0] - 2025-09-12

Initial release.