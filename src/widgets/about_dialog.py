"""
TranslateHub - About Dialog
About dialog showing application information
"""


import sys
from typing import Union

from PyQt6.QtCore import QUrl, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout, QWidget
)


class AboutDialog ( QDialog ) :
    """About dialog showing application information"""

    def __init__ (
        self, version: str, year: str, gh: str,
        parent: Union[ QWidget, None ] = None
    ) :
        """Initialize about dialog"""

        super().__init__( parent )
        self.setWindowTitle( "About TranslateHub" )
        self.resize( 400, 300 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # App title
        title_label = QLabel( "TranslateHub" )
        title_label.setFont( QFont( "", 16, QFont.Weight.Bold ) )
        self.layout.addWidget( title_label )

        # Description
        desc_label = QLabel( "\n".join( [
            "A cross-platform translation management tool for i18n projects.",
            "Designed to make translation work quick and efficient."
        ] ) )

        desc_label.setWordWrap( True )
        self.layout.addWidget( desc_label )

        # Version and Copyright
        copyright_label = QLabel( "\n".join( [
            f"Version {version}",
            f"© {year} komed3 (Paul Köhler)"
        ] ) )

        self.layout.addWidget( copyright_label )

        # GitHub link
        github_button = QPushButton( "Visit GitHub Repository" )
        github_button.clicked.connect( lambda: QDesktopServices.openUrl( QUrl( gh ) ) )
        self.layout.addWidget( github_button )

        self.layout.addSpacing( 20 )

        # System info
        sys_info = QLabel( "\n".join( [
            "Environment:",
            f"Python: {sys.version.split()[ 0 ]}",
            f"PyQt: {QT_VERSION_STR} / {PYQT_VERSION_STR}",
            f"OS: {sys.platform}"
        ] ) )

        self.layout.addWidget( sys_info )

        # Close button
        self.button_box = QDialogButtonBox( QDialogButtonBox.StandardButton.Close )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )
