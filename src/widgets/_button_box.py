"""
TranslateHub - Config Dialog
Dialog for configuring the application
"""


from PyQt6.QtWidgets import QDialogButtonBox, QPushButton


def ok_close ( accept, reject ) -> QDialogButtonBox :
    """Create a standard OK/Close button box"""

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )

    button_box.accepted.connect( accept )
    button_box.rejected.connect( reject )

    return button_box


def refresh_close ( refresh, reject ) -> QDialogButtonBox :
    """Create a standard Refresh/Close button box"""

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Close
    )

    button_box.rejected.connect( reject )

    refresh_btn = QPushButton( "Refresh" )
    refresh_btn.clicked.connect( refresh )
    button_box.addButton( refresh_btn, QDialogButtonBox.ButtonRole.ActionRole )

    return button_box
