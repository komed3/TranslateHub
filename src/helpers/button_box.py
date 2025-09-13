"""
TranslateHub - Button Box
Standard button boxes for dialogs
"""

from typing import Any, Callable, List, Tuple

from PyQt6.QtWidgets import QDialogButtonBox, QPushButton


def close ( reject: Callable ) -> QDialogButtonBox :
    """Create a standard Close button box"""

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Close
    )
    button_box.rejected.connect( reject )

    return button_box


def ok_close ( accept: Callable, reject: Callable ) -> QDialogButtonBox :
    """Create a standard OK/Close button box"""

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )

    button_box.accepted.connect( accept )
    button_box.rejected.connect( reject )

    return button_box


def custom_button_box (
    reject: Callable,
    buttons: List[ Tuple[ str, Callable, Any ] ]
) -> QDialogButtonBox :
    """
    Create a button box with Close and custom buttons
    Args:
        reject: Function to call when rejected
        buttons: List of tuples (button_text, callback, role)
    """

    button_box = close( reject )

    for button_text, callback, role in buttons :
        btn = QPushButton( button_text )
        btn.clicked.connect( callback )
        button_box.addButton( btn, role )

    return button_box


def refresh_close ( refresh: Callable, reject: Callable ) -> QDialogButtonBox :
    """
    Create a Refresh/Close button box
    Args:
        refresh: Function to call when refresh button is clicked
        reject: Function to call when rejected
    """

    return custom_button_box( reject, [
        ( "Refresh", refresh, QDialogButtonBox.ButtonRole.ActionRole )
    ] )


def export_button_box (
    export_callback: Callable, export_all_callback: Callable,
    reject: Callable
) -> QDialogButtonBox :
    """Create a button box for export dialog
    Args:
        export_callback: Function to call when Export button is clicked
        export_all_callback: Function to call when Export All button is clicked
        reject: Function to call when rejected
    """

    return custom_button_box( reject, [
        ( "Export", export_callback, QDialogButtonBox.ButtonRole.AcceptRole ),
        ( "Export All", export_all_callback, QDialogButtonBox.ButtonRole.ActionRole )
    ] )
