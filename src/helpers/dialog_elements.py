"""
TranslateHub - Dialog Elements
Helper functions for dialog elements
"""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


def dialog_title ( title: str ) -> QLabel :
    """Create a styled title label for dialogs"""

    title_label = QLabel( title )
    title_label.setFont( QFont( "", 16, QFont.Weight.Bold ) )

    return title_label
