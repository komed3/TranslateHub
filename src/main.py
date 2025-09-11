"""
TranslateHub - Main Application
Cross-platform translation management tool for i18n projects
"""


import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

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
VERSION = "0.1.0"
GITHUB_REPO = "https://github.com/komed3/TranslateHub"
YEAR = "2025"


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
        self.layout: QVBoxLayout = QVBoxLayout()

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
        self.layout.addLayout( dir_layout )

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )
        self.setLayout( self.layout )


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
        self.layout: QVBoxLayout = QVBoxLayout()

        # Key input
        key_layout = QHBoxLayout()
        self.key_label = QLabel( "Key:" )
        self.key_input = QLineEdit( key )

        if edit_mode:
            self.key_input.setReadOnly( True )

        key_layout.addWidget( self.key_label )
        key_layout.addWidget( self.key_input, 1 )
        self.layout.addLayout( key_layout )

        # Value input
        value_layout = QVBoxLayout()
        self.value_label = QLabel( "Default Value:" )
        self.value_input = QTextEdit()
        self.value_input.setPlainText( value )

        value_layout.addWidget( self.value_label )
        value_layout.addWidget( self.value_input )
        self.layout.addLayout( value_layout )

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )
        self.setLayout( self.layout )


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
        self.layout: QVBoxLayout = QVBoxLayout()

        # Old key display
        old_key_layout = QHBoxLayout()
        self.old_key_label = QLabel( "Current Key:" )
        self.old_key_display = QLineEdit( old_key )
        self.old_key_display.setReadOnly( True )

        old_key_layout.addWidget( self.old_key_label )
        old_key_layout.addWidget( self.old_key_display, 1 )
        self.layout.addLayout( old_key_layout )

        # New key input
        new_key_layout = QHBoxLayout()
        self.new_key_label = QLabel( "New Key:" )
        self.new_key_input = QLineEdit()

        new_key_layout.addWidget( self.new_key_label )
        new_key_layout.addWidget( self.new_key_input, 1 )
        self.layout.addLayout( new_key_layout )

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect( self.accept )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )
        self.setLayout( self.layout )


    def get_new_key ( self ) -> str :
        """Get the entered new key"""
        return self.new_key_input.text()


class AboutDialog ( QDialog ) :
    """About dialog showing application information"""

    def __init__ ( self, parent: Union[ QWidget, None ] = None ) :
        """Initialize about dialog"""

        super().__init__( parent )
        self.setWindowTitle( "About TranslateHub" )
        self.resize( 400, 300 )
        self.layout: QVBoxLayout = QVBoxLayout()

        # App title
        title_label = QLabel( "TranslateHub" )
        title_label.setFont( QFont( "", 16, QFont.Weight.Bold ) )
        title_label.setAlignment( Qt.AlignmentFlag.AlignCenter )
        self.layout.addWidget( title_label )

        # Version
        version_label = QLabel( f"Version {VERSION}" )
        version_label.setAlignment( Qt.AlignmentFlag.AlignCenter )
        self.layout.addWidget( version_label )

        # Description
        desc_label = QLabel( " \
            A cross-platform translation management tool for i18n projects. \
            Designed to make translation work quick and efficient. \
        " )

        desc_label.setAlignment( Qt.AlignmentFlag.AlignCenter )
        desc_label.setWordWrap( True )
        self.layout.addWidget( desc_label )
        self.layout.addSpacing( 20 )

        # Copyright
        copyright_label = QLabel( f"© {YEAR} komed3 (Paul Köhler)" )
        copyright_label.setAlignment( Qt.AlignmentFlag.AlignCenter )
        self.layout.addWidget( copyright_label )
        
        # GitHub link
        github_button = QPushButton( "Visit GitHub Repository" )
        github_button.clicked.connect( lambda: QDesktopServices.openUrl( QUrl( GITHUB_REPO ) ) )
        self.layout.addWidget( github_button )
        self.layout.addSpacing( 20 )

        # System info
        sys_info = QLabel( f" \
            Python: {sys.version.split()[ 0 ]}\n \
            PyQt: {QT_VERSION_STR} / {PYQT_VERSION_STR}\n \
            OS: {sys.platform} \
        " )

        sys_info.setAlignment( Qt.AlignmentFlag.AlignCenter )
        self.layout.addWidget( sys_info )

        # Close button
        self.button_box = QDialogButtonBox( QDialogButtonBox.StandardButton.Close )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )
        self.setLayout( self.layout )


class FilterableListWidget ( QWidget ) :
    """List widget with search/filter functionality"""

    item_selected = pyqtSignal( QListWidgetItem )

    def __init__ ( self, parent: Union[ QWidget, None ] = None ) :
        """Initialize filterable list widget"""

        super().__init__( parent )
        self.all_items = []

        self.layout: QVBoxLayout = QVBoxLayout()
        self.layout.setContentsMargins( 0, 0, 0, 0 )

        # Header with title and filter
        header_layout = QHBoxLayout()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText( "Filter..." )
        self.filter_input.textChanged.connect( self._apply_filter )

        header_layout.addWidget( self.filter_input )
        self.layout.addLayout( header_layout )

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect( self._on_item_selected )
        self.list_widget.setContextMenuPolicy( Qt.ContextMenuPolicy.CustomContextMenu )

        self.layout.addWidget( self.list_widget )
        self.setLayout( self.layout )


    def add_item ( self, text: str ) -> None :
        """Add an item to the list"""

        self.all_items.append( text )
        self._apply_filter( self.filter_input.text() )


    def clear ( self ) -> None :
        """Clear all items"""

        self.list_widget.clear()
        self.all_items = []


    def set_items ( self, items: List[ str ] ) -> None :
        """Set the list of items"""

        self.clear()
        for item_text in items :
            self.add_item( item_text )

    def current_item ( self ) -> Union[ QListWidgetItem, None ] :
        """Get the current selected item"""
        return self.list_widget.currentItem()


    def set_context_menu_policy ( self, policy ) -> None :
        """Set the context menu policy"""
        self.list_widget.setContextMenuPolicy( policy )


    def customContextMenuRequested ( self, handler ) -> None :
        """Connect custom context menu handler"""
        self.list_widget.customContextMenuRequested.connect( handler )


    def _apply_filter ( self, filter_text: str = "" ) -> None :
        """Apply filter to the list"""

        self.list_widget.clear()
        filter_text = filter_text.lower()

        for text in self.all_items :
            if not filter_text or filter_text in text.lower() :
                self.list_widget.addItem( QListWidgetItem( text ) )


    def _on_item_selected ( self, current ) :
        """Handle item selection"""

        if current:
            self.item_selected.emit( current )
