"""
TranslateHub - Update Dialog
Dialog to check for application updates via GitHub API
"""


from typing import Union

import requests
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget
)


class UpdateDialog ( QDialog ) :
    """Dialog to check for application updates via GitHub API"""

    def __init__ (
        self, version: str, gh_owner: str, gh_repo: str,
        parent: Union[ QWidget, None ] = None
    ) :
        """Initialize update dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Check for Updates" )
        self.resize( 400, 160 )

        self.version = version
        self.gh_owner = gh_owner
        self.gh_repo = gh_repo

        self.layout: QVBoxLayout = QVBoxLayout()

        # App title
        title_label = QLabel( "Check for updates" )
        title_label.setFont( QFont( "", 16, QFont.Weight.Bold ) )
        self.layout.addWidget( title_label )

        # Info label
        self.info_label = QLabel( "Fetching version from GitHub API ...<br /><br />" )
        self.layout.addWidget( self.info_label )

        # Dialog buttons
        self.button_box = QDialogButtonBox( QDialogButtonBox.StandardButton.Close )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )

        self._check_update()


    def _check_update ( self ) -> None :
        """Check for updates using GitHub API"""

        # Try to get latest release from GitHub API
        try :
            resp = requests.get(
                f"https://api.github.com/repos/{self.gh_owner}/{self.gh_repo}/releases/latest",
                timeout= 5
            )

            resp.raise_for_status()
            data = resp.json()
            latest = data.get( "tag_name", "" ).lstrip( "v" )
            url = data.get( "html_url", "" )

            # Check if latest version is different from current version
            if latest and latest != self.version :
                self.info_label.setText( "\n".join( [
                    f"New version available: <b>{latest}</b><br />",
                    f"Your version: {self.version}<br />",
                    f'Download: <a href="{url}">Open Release Page</a>'
                ] ) )
                self.info_label.setOpenExternalLinks( True )
            else:
                self.info_label.setText(
                    f"You are running the latest version ({self.version}).<br /><br />"
                )

        except requests.ConnectionError as e :
            self.info_label.setText( f"Update check failed: {e}" )
