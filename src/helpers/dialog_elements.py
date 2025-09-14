"""
TranslateHub - Dialog Elements
Helper functions for dialog elements
"""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


def dialog_label ( title: str, size: int = 12 ) -> QLabel :
    """Create a styled label for dialogs"""

    label = QLabel( title )
    label.setFont( QFont( "Sans-serif", size, QFont.Weight.Bold ) )

    return label


def dialog_title ( title: str ) -> QLabel :
    """Create a styled title label for dialogs"""

    return dialog_label( title, 16 )
