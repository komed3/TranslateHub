"""
TranslateHub - Config Dialog
Dialog for configuring the application
"""


from PyQt6.QtWidgets import QDialogButtonBox


def ok_close ( accept, reject ) -> QDialogButtonBox :
    """Create a standard OK/Close button box"""

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )

    button_box.accepted.connect( accept )
    button_box.rejected.connect( reject )

    return button_box
