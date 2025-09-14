# Changelog

All notable changes to TranslateHub will be documented in this file.

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