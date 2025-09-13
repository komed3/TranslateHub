"""
TranslateHub - About Dialog
About dialog showing application information
"""

from typing import Optional

import sys
from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from ..helpers import close, dialog_title


class AboutDialog ( QDialog ) :
    """About dialog showing application information"""

    def __init__ (
        self, version: str, year: str, gh_owner: str, gh_repo: str,
        parent: Optional[ QWidget ] = None
    ) :
        """
        Initialize about dialog
        Args:
            version: Application version
            year: Copyright year
            gh_owner: GitHub owner
            gh_repo: GitHub repository name
            parent: Parent widget
        """

        super().__init__( parent )
        self.setWindowTitle( "About TranslateHub" )
        self.resize( 400, 300 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # App title
        self.layout.addWidget( dialog_title( "TranslateHub" ) )

        # Description
        desc_label = QLabel(
            "<br />".join( [
                "A cross-platform translation management tool for i18n projects.",
                "Designed to make translation work quick and efficient."
            ] )
        )

        desc_label.setWordWrap( True )
        self.layout.addWidget( desc_label )

        # Version and Copyright
        copyright_label = QLabel(
            "<br />".join( [
                f"Version {version}",
                f"© {year} komed3 (Paul Köhler)"
            ] )
        )

        self.layout.addWidget( copyright_label )

        # GitHub link
        github_button = QPushButton( "Visit GitHub Repository" )
        github_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl( f"https://github.com/{gh_owner}/{gh_repo}" )
            )
        )
        self.layout.addWidget( github_button )

        self.layout.addSpacing( 20 )

        # System info
        sys_info = QLabel(
            "<br />".join( [
                "<u>Environment:</u>",
                f"Python: {sys.version.split()[ 0 ]}",
                f"PyQt: {QT_VERSION_STR} / {PYQT_VERSION_STR}",
                f"OS: {sys.platform}"
            ] )
        )

        self.layout.addWidget( sys_info )

        # Close button
        self.layout.addWidget( close( self.reject ) )

        self.setLayout( self.layout )
