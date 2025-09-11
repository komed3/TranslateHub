"""
TranslateHub - Main Application
Cross-platform translation management tool for i18n projects
"""


import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Union

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QListWidget, QListWidgetItem, QSplitter, QDialog,
    QDialogButtonBox, QFileDialog, QMessageBox, QProgressBar,
    QMenu, QToolBar, QStatusBar, QInputDialog, QGridLayout,
    QScrollArea, QCheckBox, QTableWidget, QTableWidgetItem,
    QAbstractItemView
)

from PyQt6.QtCore import (
    Qt, QSize, QSettings, pyqtSignal, QTimer, QUrl,
    QT_VERSION_STR, PYQT_VERSION_STR
)

from PyQt6.QtGui import QAction, QFont, QColor, QDesktopServices

from translation_manager import TranslationManager


# Application version
APP_VERSION = "0.1.0"
GITHUB_REPO = "https://github.com/komed3/TranslateHub"


class ConfigDialog ( QDialog ) :
    """Dialog for configuring the application"""

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        current_dir: Union[ str, None ] = None
    ) :
        """Initialize configuration dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Configuration" )
        self.resize( 500, 200 )

        self.layout = QVBoxLayout() # type: ignore

        # Root directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel( "Translation Root Directory:" )
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton( "Browse..." )
        self.dir_button.clicked.connect( self.browse_directory )

        if current_dir:
            self.dir_input.setText( current_dir )

        dir_layout.addWidget( self.dir_label )
        dir_layout.addWidget( self.dir_input, 1 )
        dir_layout.addWidget( self.dir_button )
        self.layout.addLayout( dir_layout ) # type: ignore

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box ) # type: ignore
        self.setLayout( self.layout() )


    def browse_directory ( self ) -> None :
        """Open file dialog to select root directory"""

        directory = QFileDialog.getExistingDirectory(
            self, "Select Translation Root Directory",
            self.dir_input.text() or str( Path.home() )
        )

        if directory:
            self.dir_input.setText( directory )


    def get_root_directory( self ) -> str :
        """Get the selected root directory"""
        return self.dir_input.text()


class TranslationKeyDialog ( QDialog ) :
    """Dialog for adding or editing translation keys"""

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        key: str = "", value: str = "", edit_mode: bool = False
    ) :
        """Initialize translation key dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Add Translation Key" if not edit_mode else "Edit Translation Key" )
        self.resize( 400, 200 )

        self.layout = QVBoxLayout() # type: ignore

        # Key input
        key_layout = QHBoxLayout()
        self.key_label = QLabel( "Key:" )
        self.key_input = QLineEdit( key )

        if edit_mode:
            self.key_input.setReadOnly( True )

        key_layout.addWidget( self.key_label )
        key_layout.addWidget( self.key_input, 1 )
        self.layout.addLayout( key_layout ) # type: ignore

        # Value input
        value_layout = QVBoxLayout()
        self.value_label = QLabel( "Default Value:" )
        self.value_input = QTextEdit()
        self.value_input.setPlainText( value )

        value_layout.addWidget( self.value_label )
        value_layout.addWidget( self.value_input )
        self.layout.addLayout( value_layout ) # type: ignore

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box ) # type: ignore
        self.setLayout( self.layout ) # type: ignore


    def get_key_value ( self ) -> Tuple[ str, str ] :
        """Get the entered key and value"""
        return self.key_input.text(), self.value_input.toPlainText()


class RenameKeyDialog ( QDialog ) :
    """Dialog for renaming translation keys"""

    def __init__ ( self, parent: Union[ QWidget, None ] = None, old_key: str = "" ) :
        """Initialize rename translation key dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Rename Translation Key" )
        self.resize( 400, 120 )

        self.layout = QVBoxLayout() # type: ignore

        # Old key display
        old_key_layout = QHBoxLayout()
        self.old_key_label = QLabel( "Current Key:" )
        self.old_key_display = QLineEdit( old_key )
        self.old_key_display.setReadOnly( True )

        old_key_layout.addWidget( self.old_key_label )
        old_key_layout.addWidget( self.old_key_display, 1 )
        self.layout.addLayout( old_key_layout ) # type: ignore

        # New key input
        new_key_layout = QHBoxLayout()
        self.new_key_label = QLabel( "New Key:" )
        self.new_key_input = QLineEdit()

        new_key_layout.addWidget( self.new_key_label )
        new_key_layout.addWidget( self.new_key_input, 1 )
        self.layout.addLayout( new_key_layout ) # type: ignore

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box ) # type: ignore
        self.setLayout( self.layout ) # type: ignore


    def get_new_key ( self ) -> str :
        """Get the entered new key"""
        return self.new_key_input.text()
