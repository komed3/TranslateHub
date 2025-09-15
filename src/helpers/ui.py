"""
TranslateHub - UI Elements
Helper functions for UI elements
"""

from typing import Callable, List, Optional

from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QLabel, QMainWindow, QMenu, QToolBar, QWidget


def ui_action (
    name: str, parent: Optional[ QWidget ] = None, cb: Optional[ Callable ] = None,
    shortcut: Optional[ str ] = None
) -> QAction :
    """Create a QAction with optional callback and shortcut"""

    action = QAction( name, parent )

    if cb :
        action.triggered.connect( cb )
    if shortcut :
        action.setShortcut( shortcut )

    return action


def ui_menu ( window: QMainWindow, title: str, items: List[ Optional[ QAction ] ] ) -> QMenu :
    """Create a QMenu with given title and items"""

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


def ui_toolbar (
    title: str, items: List[ QAction ], parent: Optional[ QWidget ],
    movable: bool = False
) -> QToolBar :
    """Create a QToolBar with given title and items"""

    toolbar = QToolBar( title, parent )
    toolbar.setMovable( movable )
    toolbar.addActions( items )

    return toolbar


def ui_label ( title: str, size: int = 12 ) -> QLabel :
    """Create a styled label for dialogs"""

    label = QLabel( title )
    label.setFont( QFont( "Sans-serif", size, QFont.Weight.Bold ) )

    return label


def ui_title ( title: str ) -> QLabel :
    """Create a styled title label for dialogs"""

    return ui_label( title, 16 )
