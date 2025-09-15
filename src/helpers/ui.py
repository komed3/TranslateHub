"""
TranslateHub - UI Elements
Helper functions for UI elements
"""

from typing import Callable, List, Optional

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QMenu, QWidget


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


def ui_menu ( window: QMainWindow, title: str, items: List[ Optional[ QAction ] ] ) -> QMenu :

    menu_bar = window.menuBar()
    assert menu_bar is not None

    menu = menu_bar.addMenu( title )
    assert menu is not None

    for item in items :
        if item :
            menu.addAction( item )
        else :
            menu.addSeparator()

    return menu
