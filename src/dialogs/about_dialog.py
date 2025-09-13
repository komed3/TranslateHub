"""
TranslateHub - About Dialog
About dialog showing application information
"""


import sys
from typing import Union

from PyQt6.QtCore import QUrl, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from ..lib._button_box import close


class AboutDialog ( QDialog ) :
    """About dialog showing application information"""

    def __init__ (
        self, version: str, year: str, gh_owner: str, gh_repo: str,
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
        desc_label = QLabel( "<br />".join( [
            "A cross-platform translation management tool for i18n projects.",
            "Designed to make translation work quick and efficient."
        ] ) )

        desc_label.setWordWrap( True )
        self.layout.addWidget( desc_label )

        # Version and Copyright
        copyright_label = QLabel( "<br />".join( [
            f"Version {version}",
            f"© {year} komed3 (Paul Köhler)"
        ] ) )

        self.layout.addWidget( copyright_label )

        # GitHub link
        github_button = QPushButton( "Visit GitHub Repository" )
        github_button.clicked.connect( lambda: QDesktopServices.openUrl( QUrl(
            f"https://github.com/{gh_owner}/{gh_repo}"
        ) ) )
        self.layout.addWidget( github_button )

        self.layout.addSpacing( 20 )

        # System info
        sys_info = QLabel( "<br />".join( [
            "<u>Environment:</u>",
            f"Python: {sys.version.split()[ 0 ]}",
            f"PyQt: {QT_VERSION_STR} / {PYQT_VERSION_STR}",
            f"OS: {sys.platform}"
        ] ) )

        self.layout.addWidget( sys_info )

        # Close button
        self.button_box = close( self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )
