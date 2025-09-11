"""
TranslateHub - Main Application
Cross-platform translation management tool for i18n projects
"""


import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

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

    def __init__ ( self, parent = None, current_dir = None ) :
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


    def browse_directory ( self ) :
        """Open file dialog to select root directory"""

        directory = QFileDialog.getExistingDirectory(
            self, "Select Translation Root Directory",
            self.dir_input.text() or str( Path.home() )
        )

        if directory:
            self.dir_input.setText( directory )


    def get_root_directory( self ) :
        """Get the selected root directory"""
        return self.dir_input.text()
