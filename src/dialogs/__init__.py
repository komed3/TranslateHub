"""
TranslateHub - Dialogs Module
"""

from .about_dialog import AboutDialog
from .config_dialog import ConfigDialog
from .export_dialog import ExportDialog
from .missing_translations_dialog import MissingTranslationsDialog
from .move_keys_dialog import MoveKeysDialog
from .options_dialog import OptionsDialog
from .rename_key_dialog import RenameKeyDialog
from .search_dialog import SearchDialog
from .statistics_dialog import StatisticsDialog
from .translation_key_dialog import TranslationKeyDialog
from .update_dialog import UpdateDialog

__all__ = [
    "AboutDialog",
    "ConfigDialog",
    "ExportDialog",
    "MissingTranslationsDialog",
    "MoveKeysDialog",
    "OptionsDialog",
    "RenameKeyDialog",
    "SearchDialog",
    "StatisticsDialog",
    "TranslationKeyDialog",
    "UpdateDialog"
]
