"""
TranslateHub - Dialogs Module
"""

from .about_dialog import AboutDialog
from .export_dialog import ExportDialog
from .missing_translations_dialog import MissingTranslationsDialog
from .options_dialog import OptionsDialog
from .rename_key_dialog import RenameKeyDialog
from .search_dialog import SearchDialog
from .statistics_dialog import StatisticsDialog
from .translation_key_dialog import TranslationKeyDialog
from .update_dialog import UpdateDialog

__all__ = [
    "AboutDialog",
    "ExportDialog",
    "MissingTranslationsDialog",
    "OptionsDialog",
    "RenameKeyDialog",
    "SearchDialog",
    "StatisticsDialog",
    "TranslationKeyDialog",
    "UpdateDialog"
]
