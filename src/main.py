"""
TranslateHub - Main Application
Cross-platform translation management tool for i18n projects
"""


import os
import sys
from pathlib import Path
from typing import cast, Dict, List, Tuple, Union

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

from .translation_manager import TranslationManager
from .widgets.about_dialog import AboutDialog
from .widgets.config_dialog import ConfigDialog
from .widgets.filterable_list_widget import FilterableListWidget
from .widgets.rename_key_dialog import RenameKeyDialog
from .widgets.translation_key_dialog import TranslationKeyDialog


# Application version
VERSION = "0.1.0"
GITHUB_REPO = "https://github.com/komed3/TranslateHub"
YEAR = "2025"


class TranslationEditor ( QWidget ) :
    """Widget for editing translations"""

    translation_changed = pyqtSignal( str, str, str, str )
    key_action_requested = pyqtSignal( str, str )

    def __init__ ( self, parent: Union[ QWidget, None ] = None ) :
        """Initialize translation editor"""

        super().__init__( parent )
        self.current_lang = None
        self.current_ns = None
        self.data = {}
        self.hide_translated = False
        self.layout: QVBoxLayout = QVBoxLayout()

        # Options
        options_layout = QHBoxLayout()

        self.hide_translated_cb = QCheckBox( "Hide Translated Values" )
        self.hide_translated_cb.toggled.connect( self._toggle_hide_translated )

        options_layout.addWidget( self.hide_translated_cb )
        options_layout.addStretch()
        self.layout.addLayout( options_layout )

        # Translation grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable( True )
        self.scroll_widget = QWidget()

        self.grid_layout = QGridLayout( self.scroll_widget )

        self.scroll_area.setWidget( self.scroll_widget )
        self.layout.addWidget( self.scroll_area )
        self.setLayout( self.layout )


    def load_translations ( self, lang: str, ns: str, data: Dict[ str, str ] ) -> None :
        """Load translations into the editor"""

        self.current_lang = lang
        self.current_ns = ns
        self.data = data
        self._refresh_grid()


    def _refresh_grid ( self ) -> None :
        """Refresh the translation grid"""

        # Clear existing widgets
        while self.grid_layout.count() :
            item = self.grid_layout.takeAt( 0 )
            if item and ( widget := item.widget() ) :
                widget.deleteLater()

        # Add headers
        self.grid_layout.addWidget( QLabel( "Key" ), 0, 0 )
        self.grid_layout.addWidget( QLabel( "Translation" ), 0, 1 )
        self.grid_layout.addWidget( QLabel( "Actions" ), 0, 2 )

        # Add translation rows
        row = 1
        for key, value in sorted( self.data.items() ) :

            # Skip translated values if hide_translated is enabled
            if self.hide_translated and value.strip() :
                continue

            # Key label
            key_label = QLabel( key )
            key_label.setTextInteractionFlags( Qt.TextInteractionFlag.TextSelectableByMouse )
            key_label.setWordWrap( True )

            # Translation input
            t_input = QTextEdit()
            t_input.setPlainText( value )
            t_input.setProperty( "key", key )
            t_input.textChanged.connect(
                lambda input_widget= t_input: self._on_translation_changed( input_widget )
            )

            # Actions
            actions_layout = QHBoxLayout()

            rename_btn = QPushButton( "Rename" )
            rename_btn.setProperty( "key", key )
            rename_btn.clicked.connect(
                lambda checked, btn= rename_btn: self.key_action_requested.emit(
                    "rename", btn.property( "key" )
                )
            )

            delete_btn = QPushButton( "Delete" )
            delete_btn.setProperty( "key", key )
            delete_btn.clicked.connect(
                lambda checked, btn= delete_btn: self.key_action_requested.emit(
                    "delete", btn.property( "key" )
                )
            )

            actions_layout.addWidget( rename_btn )
            actions_layout.addWidget( delete_btn )

            actions_widget = QWidget()
            actions_widget.setLayout( actions_layout )

            self.grid_layout.addWidget( key_label, row, 0 )
            self.grid_layout.addWidget( t_input, row, 1 )
            self.grid_layout.addWidget( actions_widget, row, 2 )
            row += 1


    def _on_translation_changed ( self, input_widget: QTextEdit ) -> None :
        """Handle translation text changes"""

        if not self.current_lang or not self.current_ns :
            return

        key = input_widget.property( "key" )
        value = input_widget.toPlainText()

        if key in self.data :
            self.data[ key ] = value
            self.translation_changed.emit(
                self.current_lang,
                self.current_ns,
                key, value
            )


    def _toggle_hide_translated ( self, checked: bool ) -> None :
        """Toggle hiding of translated values"""

        self.hide_translated = checked
        if self.current_lang and self.current_ns :
            self._refresh_grid()


class StatisticsDialog ( QDialog ) :
    """Dialog showing translation statistics"""

    lang_ns_selected = pyqtSignal( str, str )

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        t_manager: Union[ TranslationManager, None ] = None
    ) :
        """Initialize statistics dialog"""

        super().__init__( parent )
        self.t_manager = t_manager
        self.setWindowTitle( "Translation Statistics" )
        self.resize( 800, 600 )
        self.layout: QVBoxLayout = QVBoxLayout()

        # Statistics table
        self.table = QTableWidget()
        self.table.setEditTriggers( QAbstractItemView.EditTrigger.NoEditTriggers )
        self.table.setSelectionBehavior( QAbstractItemView.SelectionBehavior.SelectItems )
        self.table.setSelectionMode( QAbstractItemView.SelectionMode.SingleSelection )
        self.table.cellDoubleClicked.connect( self._on_cell_double_clicked )
        self.layout.addWidget( self.table )

        # Refresh button
        refresh_btn = QPushButton( "Refresh" )
        refresh_btn.clicked.connect( self._load_statistics )
        self.layout.addWidget( refresh_btn )

        # Close button
        self.button_box = QDialogButtonBox( QDialogButtonBox.StandardButton.Close )
        self.button_box.rejected.connect( self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )

        # Load statistics
        self._load_statistics()


    def _load_statistics ( self ) -> None :
        """Load translation statistics"""

        if not self.t_manager :
            return

        # Get all progress data
        pg_data = self.t_manager.get_all_progress()
        ns = sorted( self.t_manager.get_namespaces() )
        lngs = sorted( self.t_manager.get_languages() )
        ns_len = len( ns )
        lngs_len = len( lngs )

        # Set up table
        self.table.clear()
        self.table.setColumnCount( ns_len + 1 )
        self.table.setRowCount( lngs_len + 1 )
        self.table.setHorizontalHeaderItem( ns_len, QTableWidgetItem( "Total" ) )
        self.table.setVerticalHeaderItem( lngs_len, QTableWidgetItem( "Total" ) )

        total_translated = 0
        total_keys = 0

        ns_total_translated = []
        ns_total_keys = []
        lngs_total_translated = []
        lngs_total_keys = []

        # Fill headers and data
        for i, n in enumerate( ns ) :
            ns_total_translated.append( 0 )
            ns_total_keys.append( 0 )
            self.table.setHorizontalHeaderItem( i, QTableWidgetItem( n ) )

        for i, l in enumerate( lngs ) :
            lngs_total_translated.append( 0 )
            lngs_total_keys.append( 0 )
            self.table.setVerticalHeaderItem( i, QTableWidgetItem( l ) )

            for j, n in enumerate( ns ) :
                if l in pg_data and n in pg_data[ l ] :
                    done, total = pg_data[ l ][ n ]
                    item = self._progress_cell( done, total )
                    self.table.setItem( i, j, item )

                    total_translated += done
                    total_keys += total

                    ns_total_translated[ j ] += done
                    ns_total_keys[ j ] += total
                    lngs_total_translated[ i ] += done
                    lngs_total_keys[ i ] += total

        # Fill totals
        for i, t in enumerate( lngs_total_keys ) :
            item = self._progress_cell( lngs_total_translated[ i ], t )
            self.table.setItem( i, ns_len, item )

        for j, t in enumerate( ns_total_keys ) :
            item = self._progress_cell( ns_total_translated[ j ], t )
            self.table.setItem( lngs_len, j, item )

        item = self._progress_cell( total_translated, total_keys )
        self.table.setItem( lngs_len, ns_len, item )

        # Resize columns/rows to content
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()


    def _progress_cell ( self, done: int, total: int ) -> QTableWidgetItem :
        """Create a table item showing progress with color coding"""

        if total > 0 :
            pct = int( done / total * 100 )
            item = QTableWidgetItem( f"{done}/{total} ({pct}%)" )
            item.setForeground( QColor( 0, 0, 0 ) )

            if pct == 100 :
                item.setBackground( QColor( 200, 255, 200 ) )
            elif pct >= 75 :
                item.setBackground( QColor( 255, 255, 200 ) )
            elif pct >= 50 :
                item.setBackground( QColor( 255, 225, 200 ) )
            elif pct >= 25 :
                item.setBackground( QColor( 255, 200, 200 ) )
            else :
                item.setBackground( QColor( 255, 200, 255 ) )

        else :
            item = QTableWidgetItem( "N/A" )

        return item


    def _on_cell_double_clicked ( self, row: int, col: int ) -> None :
        """Handle cell double click to navigate to language/namespace"""

        if not self.t_manager :
            return

        lngs = sorted( self.t_manager.get_languages() )
        ns = sorted( self.t_manager.get_namespaces() )

        if 0 <= row < len( lngs ) and 0 <= col < len( ns ) :
            self.lang_ns_selected.emit( lngs[ row ], ns[ col ] )
            self.accept()


class MainWindow ( QMainWindow ) :
    """Main application window"""

    def __init__ ( self ) :
        """Initialize main window"""

        super().__init__()
        self.t_manager = TranslationManager()
        self.settings = QSettings( "TranslateHub", "TranslateHub" )

        self.setWindowTitle( "TranslateHub" )
        self.resize( 1200, 800 )

        self._create_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()

        # Load last directory if available
        last_dir = self.settings.value( "last_directory" )
        if last_dir and os.path.isdir( last_dir ) :
            self.t_manager.set_root_dir( last_dir )
            self._refresh_ui()
        else :
            self._show_config_dialog()

        # Auto-save timer
        self.auto_save_timer = QTimer( self )
        self.auto_save_timer.timeout.connect( self._auto_save )
        self.auto_save_timer.start( 30000 )


    def _create_ui ( self ) -> None :
        """Create the main user interface"""

        self.central_widget = QWidget()
        self.setCentralWidget( self.central_widget )
        main_layout = QVBoxLayout()

        # Main splitter
        self.main_splitter = QSplitter( Qt.Orientation.Horizontal )

        # Left panel - Languages and namespaces
        self.left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Languages section
        lang_layout = QVBoxLayout()
        lang_header = QHBoxLayout()
        lang_label = QLabel( "Languages" )
        lang_label.setFont( QFont( "", 12, QFont.Weight.Bold ) )
        self.add_lang_button = QPushButton( "Add" )
        self.add_lang_button.clicked.connect( self._add_language )

        lang_header.addWidget( lang_label )
        lang_header.addWidget( self.add_lang_button )

        self.lang_list = FilterableListWidget()
        self.lang_list.item_selected.connect( self._on_language_selected )
        self.lang_list.set_context_menu_policy( Qt.ContextMenuPolicy.CustomContextMenu )
        self.lang_list.customContextMenuRequested( self._show_language_context_menu )

        lang_layout.addLayout( lang_header )
        lang_layout.addWidget( self.lang_list )

        # Namespaces section
        ns_layout = QVBoxLayout()
        ns_header = QHBoxLayout()
        ns_label = QLabel( "Namespaces" )
        ns_label.setFont( QFont( "", 12, QFont.Weight.Bold ) )
        self.add_ns_button = QPushButton( "Add" )
        self.add_ns_button.clicked.connect( self._add_namespace )

        ns_header.addWidget( ns_label )
        ns_header.addWidget( self.add_ns_button )

        self.ns_list = FilterableListWidget()
        self.ns_list.item_selected.connect( self._on_namespace_selected )
        self.ns_list.set_context_menu_policy( Qt.ContextMenuPolicy.CustomContextMenu )
        self.ns_list.customContextMenuRequested( self._show_namespace_context_menu )

        ns_layout.addLayout( ns_header )
        ns_layout.addWidget( self.ns_list )

        # Progress bars
        progress_layout = QVBoxLayout()
        progress_label = QLabel( "Translation Progress" )
        progress_label.setFont( QFont( "", 12, QFont.Weight.Bold ) )

        self.language_progress = QProgressBar()
        self.language_progress.setFormat( "%v/%m (%p%)" )

        self.namespace_progress = QProgressBar()
        self.namespace_progress.setFormat( "%v/%m (%p%)" )

        progress_layout.addWidget( progress_label )
        progress_layout.addWidget( QLabel( "Selected Language:" ) )
        progress_layout.addWidget( self.language_progress )
        progress_layout.addWidget( QLabel( "Selected Namespace:" ) )
        progress_layout.addWidget( self.namespace_progress )

        # Combine left panel layouts
        left_layout.addLayout( lang_layout, 1 )
        left_layout.addLayout( ns_layout, 1 )
        left_layout.addLayout( progress_layout )
        self.left_panel.setLayout( left_layout )

        # Right panel - Translation editor
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Editor header
        editor_header = QHBoxLayout()
        self.editor_title = QLabel( "No Translation Selected" )
        self.editor_title.setFont( QFont( "", 14, QFont.Weight.Bold ) )

        self.add_key_button = QPushButton( "Add Key" )
        self.add_key_button.clicked.connect( self._add_translation_key )
        self.add_key_button.setEnabled( False )

        editor_header.addWidget( self.editor_title, 1 )
        editor_header.addWidget( self.add_key_button )

        # Translation editor
        self.t_editor = TranslationEditor()
        self.t_editor.translation_changed.connect( self._on_translation_changed )
        self.t_editor.key_action_requested.connect( self._on_key_action_requested )

        right_layout.addLayout( editor_header )
        right_layout.addWidget( self.t_editor, 1 )
        self.right_panel.setLayout( right_layout )

        # Add panels to splitter
        self.main_splitter.addWidget( self.left_panel )
        self.main_splitter.addWidget( self.right_panel )
        self.main_splitter.setSizes( [ 300, 900 ] )

        main_layout.addWidget( self.main_splitter )
        self.central_widget.setLayout( main_layout )


    def _create_actions ( self ) -> None :
        """Create application actions"""

        # File actions
        self.open_action = QAction( "&Open Project...", self )
        self.open_action.setShortcut( "Ctrl+O" )
        self.open_action.triggered.connect( self._show_config_dialog )

        self.save_all_action = QAction( "&Save All", self )
        self.save_all_action.setShortcut( "Ctrl+S" )
        self.save_all_action.triggered.connect( self._save_all )

        self.exit_action = QAction( "E&xit", self )
        self.exit_action.setShortcut( "Ctrl+Q" )
        self.exit_action.triggered.connect( self.close )

        # Edit actions
        self.sync_action = QAction( "&Synchronize Keys", self )
        self.sync_action.setShortcut( "F5" )
        self.sync_action.triggered.connect( self._synchronize_keys )

        self.stats_action = QAction( "Show Statistics", self )
        self.stats_action.triggered.connect( self._show_statistics )

        # Help actions
        self.check_updates_action = QAction( "Check for &Updates", self )
        self.check_updates_action.triggered.connect( self._check_updates )

        self.github_action = QAction( "Visit &GitHub Repository", self )
        self.github_action.triggered.connect(
            lambda: QDesktopServices.openUrl( QUrl( GITHUB_REPO ) )
        )

        self.about_action = QAction( "&About TranslateHub", self )
        self.about_action.triggered.connect( self._show_about_dialog )


    def _new_menu ( self, title: str ) -> QMenu :
        """Create a menu by title"""

        menu_bar = self.menuBar()
        assert menu_bar is not None

        file_menu = menu_bar.addMenu( title )
        assert file_menu is not None

        return file_menu


    def _create_menus ( self ) -> None :
        """Create application menus"""

        # File menu
        self.file_menu = self._new_menu( "&File" )
        self.file_menu.addAction( self.open_action )
        self.file_menu.addAction( self.save_all_action )
        self.file_menu.addSeparator()
        self.file_menu.addAction( self.exit_action )

        # Edit menu
        self.edit_menu = self._new_menu( "&Edit" )
        self.edit_menu.addAction( self.sync_action )
        self.edit_menu.addAction( self.stats_action )

        # Help menu
        self.help_menu = self._new_menu( "&Help" )
        self.help_menu.addAction( self.check_updates_action )
        self.help_menu.addAction( self.github_action )
        self.help_menu.addSeparator()
        self.help_menu.addAction( self.about_action )


    def _create_toolbars ( self ) -> None :
        """Create application toolbars"""

        self.main_toolbar = QToolBar( "Main" )
        self.main_toolbar.setMovable( False )
        self.main_toolbar.setIconSize( QSize( 16, 16 ) )

        self.main_toolbar.addAction( self.open_action )
        self.main_toolbar.addAction( self.save_all_action )
        self.main_toolbar.addAction( self.sync_action )
        self.main_toolbar.addAction( self.stats_action )

        self.addToolBar( self.main_toolbar )


    def _create_statusbar ( self ) -> None :
        """Create application status bar"""

        self.status_bar = QStatusBar()
        self.setStatusBar( self.status_bar )

        self.status_label = QLabel( "Ready" )
        self.status_bar.addWidget( self.status_label, 1 )

        self.version_label = QLabel( f"v{VERSION}" )
        self.status_bar.addPermanentWidget( self.version_label )

        self.dir_label = QLabel( "No directory selected" )
        self.status_bar.addPermanentWidget( self.dir_label )


    def _show_config_dialog ( self ) -> None :
        """Show configuration dialog"""

        dialog = ConfigDialog( self, self.t_manager.root_dir )

        if dialog.exec() :
            root_dir = dialog.get_root_directory()

            if root_dir and self.t_manager.set_root_dir( root_dir ) :
                self.settings.setValue( "last_directory", root_dir )
                self._refresh_ui()
                self.status_label.setText( f"Loaded project from {root_dir}" )
            else :
                QMessageBox.warning(
                    self, "Invalid Directory",
                    "The selected directory is not valid."
                )


    def _refresh_ui ( self ) -> None :
        """Refresh the UI with current data"""

        # Update directory label
        if self.t_manager.root_dir :
            self.dir_label.setText( self.t_manager.root_dir )
        else :
            self.dir_label.setText( "No directory selected" )

        # Update language list
        self.lang_list.clear()
        for lang in self.t_manager.get_languages() :
            self.lang_list.add_item( lang )

        # Update namespace list
        self.ns_list.clear()
        for ns in self.t_manager.get_namespaces() :
            self.ns_list.add_item( ns )

        # Clear editor if no selection
        if not self.lang_list.current_item() or not self.ns_list.current_item() :
            self.editor_title.setText( "No Translation Selected" )
            self.t_editor.load_translations( "", "", {} )
            self.add_key_button.setEnabled( False )

        # Update progress bars
        self._update_progress_bars()


    def _update_progress_bars ( self ) -> None :
        """Update progress bars based on current selection"""

        # Language progress
        if self.lang_list.current_item() :
            lang = cast( QListWidgetItem, self.lang_list.current_item() ).text()
            progress = self.t_manager.get_language_progress( lang )
            self.language_progress.setMaximum( progress[ 1 ] )
            self.language_progress.setValue( progress[ 0 ] )
        else :
            self.language_progress.setMaximum( 100 )
            self.language_progress.setValue( 0 )

        # Namespace progress
        if self.ns_list.current_item() :
            ns = cast( QListWidgetItem, self.ns_list.current_item() ).text()

            if self.lang_list.current_item() :
                lang = cast( QListWidgetItem, self.lang_list.current_item() ).text()
                progress = self.t_manager.get_namespace_progress( ns )

                if lang in progress :
                    self.namespace_progress.setMaximum( progress[ lang ][ 1 ] )
                    self.namespace_progress.setValue( progress[ lang ][ 0 ] )
                else :
                    self.namespace_progress.setMaximum( 100 )
                    self.namespace_progress.setValue( 0 )

            else :
                self.namespace_progress.setMaximum( 100 )
                self.namespace_progress.setValue( 0 )

        else :
            self.namespace_progress.setMaximum( 100 )
            self.namespace_progress.setValue( 0 )


    def _on_language_selected ( self ) -> None :
        """Handle language selection change"""
        self._load_current_translations()


    def _on_namespace_selected ( self ) -> None :
        """Handle namespace selection change"""
        self._load_current_translations()


    def _load_current_translations ( self ) -> None :
        """Load translations for current language and namespace"""

        if not self.lang_list.current_item() or not self.ns_list.current_item() :
            self.editor_title.setText( "No Translation Selected" )
            self.t_editor.load_translations( "", "", {} )
            self.add_key_button.setEnabled( False )
            return

        lang = cast( QListWidgetItem, self.lang_list.current_item() ).text()
        ns = cast( QListWidgetItem, self.ns_list.current_item() ).text()

        translations = self.t_manager.get_translations( lang, ns )
        self.editor_title.setText( f"{lang} - {ns}" )
        self.t_editor.load_translations( lang, ns, translations )
        self.add_key_button.setEnabled( True )

        self._update_progress_bars()


    def _on_translation_changed ( self, lang: str, ns: str, key: str, value: str ) -> None :
        """Handle translation changes"""
        translations = self.t_manager.get_translations( lang, ns )
        if key in translations :
            translations[ key ] = value
            # We don't save immediately to avoid excessive disk I/O
            # Auto-save timer will handle periodic saving


    def _auto_save ( self ) :
        """Auto-save current translations"""

        if (
            self.t_editor.current_lang and
            self.t_editor.current_ns and
            self.t_editor.data
        ) :
            self.t_manager.save_translations (
                self.t_editor.current_lang,
                self.t_editor.current_ns,
                self.t_editor.data
            )
            self._update_progress_bars()


    def _save_all ( self ) :
        """Save all translations"""

        self._auto_save()
        self._update_progress_bars()
        self.status_label.setText( "All translations saved" )


    def _add_language ( self ) -> None :
        """Add a new language"""

        lang, ok = QInputDialog.getText(
            self, "Add Language",
            "Enter language code (e.g., en-US, de-DE):"
        )

        if ok and lang :
            if self.t_manager.create_language( lang ) :
                self._refresh_ui()
                self.status_label.setText( f"Language {lang} added" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not create language {lang}"
                )


    def _add_namespace ( self ) -> None :
        """Add a new namespace"""

        ns, ok = QInputDialog.getText(
            self, "Add Namespace",
            "Enter namespace name (e.g., app.home):"
        )

        if ok and ns :
            if not ns.endswith( '.json' ) :
                ns = f"{ns}.json"

            if self.t_manager.create_namespace( ns ) :
                self._refresh_ui()
                self.status_label.setText( f"Namespace {ns} added" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not create namespace {ns}"
                )


    def _show_language_context_menu ( self, position ) -> None :
        """Show context menu for language list"""

        if not self.lang_list.current_item() :
            return

        lang = cast( QListWidgetItem, self.lang_list.current_item() ).text()

        menu = QMenu()
        rename_action = menu.addAction( "Rename" )
        delete_action = menu.addAction( "Delete" )

        action = menu.exec( self.lang_list.list_widget.mapToGlobal( position ) )

        if action == rename_action :
            self._rename_language( lang )
        elif action == delete_action :
            self._delete_language( lang )


    def _show_namespace_context_menu ( self, position ) -> None :
        """Show context menu for namespace list"""

        if not self.ns_list.current_item() :
            return

        ns = cast( QListWidgetItem, self.ns_list.current_item() ).text()

        menu = QMenu()
        rename_action = menu.addAction( "Rename" )
        delete_action = menu.addAction( "Delete" )

        action = menu.exec( self.ns_list.list_widget.mapToGlobal( position ) )

        if action == rename_action :
            self._rename_namespace( ns )
        elif action == delete_action :
            self._delete_namespace( ns )


    def _rename_language ( self, lang: str ) -> None :
        """Rename a language"""

        new_code, ok = QInputDialog.getText(
            self, "Rename Language",
            "Enter new language code:",
            text= lang
        )

        if ok and new_code and new_code != lang :
            if self.t_manager.rename_language( lang, new_code ) :
                self._refresh_ui()
                self.status_label.setText( f"Language renamed to {new_code}" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not rename language {lang}"
                )


    def _rename_namespace ( self, ns: str ) -> None :
        """Rename a namespace"""

        new_name, ok = QInputDialog.getText(
            self, "Rename Namespace",
            "Enter new namespace name:",
            text= ns
        )

        if ok and new_name and new_name != ns :
            if not new_name.endswith( '.json' ) :
                new_name = f"{new_name}.json"

            if self.t_manager.rename_namespace( ns, new_name ) :
                self._refresh_ui()
                self.status_label.setText( f"Namespace renamed to {new_name}" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not rename namespace {ns}"
                )


    def _delete_language ( self, lang: str ) -> None :
        """Delete a language"""

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the language '{lang}' and all its translations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes :
            if self.t_manager.delete_language( lang ) :
                self._refresh_ui()
                self.status_label.setText( f"Language {lang} deleted" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not delete language {lang}"
                )


    def _delete_namespace( self, ns: str ) -> None :
        """Delete a namespace"""

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the namespace '{ns}' from all languages?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes :
            if self.t_manager.delete_namespace( ns ) :
                self._refresh_ui()
                self.status_label.setText( f"Namespace {ns} deleted" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not delete namespace {ns}"
                )


    def _add_translation_key ( self ) -> None :
        """Add a new translation key"""

        if not self.ns_list.current_item() :
            return

        ns = cast( QListWidgetItem, self.ns_list.current_item() ).text()
        dialog = TranslationKeyDialog( self )

        if dialog.exec() :
            key, value = dialog.get_key_value()

            if key :
                if self.t_manager.add_translation_key( ns, key, value ) :
                    self._load_current_translations()
                    self.status_label.setText( f"Key '{key}' added to {ns}" )
                else :
                    QMessageBox.warning(
                        self, "Error",
                        f"Could not add key '{key}' to {ns}"
                    )


    def _on_key_action_requested ( self, action: str, key: str ) -> None :
        """Handle key action requests from the editor"""

        if not self.ns_list.current_item() :
            return

        ns = cast( QListWidgetItem, self.ns_list.current_item() ).text()

        if action == "rename" :
            self._rename_translation_key( ns, key )
        elif action == "delete" :
            self._delete_translation_key( ns, key )


    def _rename_translation_key ( self, ns: str, key: str ) -> None :
        """Rename a translation key"""

        dialog = RenameKeyDialog( self, key )

        if dialog.exec() :
            new_key = dialog.get_new_key()

            if new_key and new_key != key :
                if self.t_manager.rename_translation_key( ns, key, new_key ) :
                    self._load_current_translations()
                    self.status_label.setText( f"Key '{key}' renamed to '{new_key}'" )
                else:
                    QMessageBox.warning(
                        self, "Error",
                        f"Could not rename key '{key}' to '{new_key}'"
                    )


    def _delete_translation_key ( self, ns: str, key: str ) -> None :
        """Delete a translation key"""

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the key '{key}' from all languages?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes :
            if self.t_manager.delete_translation_key( ns, key ) :
                self._load_current_translations()
                self.status_label.setText( f"Key '{key}' deleted from {ns}" )
            else :
                QMessageBox.warning(
                    self, "Error",
                    f"Could not delete key '{key}' from {ns}"
                )


    def _synchronize_keys ( self ) -> None :
        """Synchronize keys across all languages and namespaces"""

        changes = self.t_manager.synchronize_keys()

        if changes :
            total_changes = sum( changes.values() )
            message = f"Synchronized {total_changes} keys across {len( changes )} namespaces"

            QMessageBox.information(
                self, "Synchronization Complete",
                message
            )

            self._refresh_ui()
            self.status_label.setText( message )

        else :
            QMessageBox.information(
                self, "Synchronization Complete",
                "All keys are already synchronized."
            )

            self.status_label.setText( "All keys are already synchronized" )


    def _show_statistics ( self ) -> None :
        """Show translation statistics dialog"""

        dialog = StatisticsDialog( self, self.t_manager )
        dialog.lang_ns_selected.connect( self._select_lang_ns )
        dialog.exec()


    def _select_lang_ns ( self, lang: str, ns: str ) -> None :
        """Select a language and namespace from statistics dialog"""

        # Find and select the language
        for i in range( self.lang_list.list_widget.count() ) :
            item = cast( QListWidgetItem, self.lang_list.list_widget.item( i ) )
            if item.text() == lang:
                self.lang_list.list_widget.setCurrentItem( item )
                break

        # Find and select the namespace
        for i in range( self.ns_list.list_widget.count() ) :
            item = cast( QListWidgetItem, self.ns_list.list_widget.item( i ) )
            if item.text() == ns :
                self.ns_list.list_widget.setCurrentItem( item )
                break


    def _check_updates ( self ) -> None :
        """Check for updates"""

        try :
            # This is a placeholder for actual update checking logic
            # In a real application, you would connect to a server or GitHub API
            QMessageBox.information(
                self, "Check for Updates",
                f"You are running TranslateHub version {VERSION}.\n\n"
                "This is the latest version available."
            )

        except RuntimeError as e :
            QMessageBox.warning(
                self, "Update Check Failed",
                f"Could not check for updates: {str( e )}"
            )


    def _show_about_dialog ( self ) -> None :
        """Show about dialog"""

        dialog = AboutDialog( VERSION, YEAR, GITHUB_REPO, self )
        dialog.exec()


    def closeEvent ( self, event ) -> None :
        """Handle window close event"""

        # Save current translations before closing
        self._save_all()
        event.accept()


def main () :
    """Main application entry point"""

    app = QApplication( sys.argv )

    # Use Fusion style for consistent cross-platform look
    app.setStyle( 'Fusion' )

    # Set application information
    app.setApplicationName( "TranslateHub" )
    app.setApplicationVersion( VERSION )
    app.setOrganizationName( "komed3 (Paul Köhler)" )

    window = MainWindow()
    window.show()

    sys.exit( app.exec() )


if __name__ == "__main__" :
    main()
