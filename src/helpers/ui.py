"""
TranslateHub - UI Elements
Helper functions for UI elements
"""

from typing import Callable, Optional

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget


def ui_action (
    name: str, parent: Optional[ QWidget ] = None, callable: Optional[ Callable ] = None,
    shortcut: Optional[ str ] = None
) -> QAction :
    """Create a QAction with optional callback and shortcut"""

    action = QAction( name, parent )

    if callable :
        action.triggered.connect( callable )
    if shortcut :
        action.setShortcut( shortcut )

    return action
