"""
TranslateHub - Main Application
Cross-platform translation management tool for i18n projects
"""

from typing import Dict

import os
from PyQt6.QtCore import QSettings, Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMenu, QMessageBox,
    QProgressBar, QPushButton, QSplitter, QStatusBar, QVBoxLayout, QWidget
)

from .core import TranslationManager
from .dialogs import (
    AboutDialog, ConfigDialog, ExportDialog, MissingTranslationsDialog,
    OptionsDialog, RenameKeyDialog, SearchDialog, StatisticsDialog,
    TranslationKeyDialog, UpdateDialog
)
from .helpers import dialog_label, ui_action, ui_menu, ui_toolbar
from .utils import TranslationAPI
from .widgets import FilterableListWidget, TranslationEditor

# Application version
VERSION = "0.2.0"
GITHUB_OWNER = "komed3"
GITHUB_REPO = "TranslateHub"
YEAR = "2025"


class TranslateHub ( QMainWindow ) :
    """Main application window"""

    def __init__ ( self ) :
        """Initialize main window"""

        super().__init__()

        # Initialize settings
        self.settings = QSettings( "TranslateHub", "TranslateHub" )

        # Initialize translation manager with schema directory name from settings
        self.t_manager = TranslationManager(
            schema_dir_name= self.settings.value( "schema_dir_name", "_schema", str )
        )

        # Initialize translation API
        self.translation_api = TranslationAPI(
            enabled= self.settings.value( "api_enabled", False, bool ),
            api_url= self.settings.value( "api_url", "", str ),
            api_key= self.settings.value( "api_key", "", str ),
            api_pattern= self.settings.value( "api_pattern", "", str )
        )

        self.setWindowTitle( "TranslateHub" )
        self.resize( 1200, 800 )

        # Set application icon
        icon_path = os.path.join( os.path.dirname( __file__ ), "../resources/icon.ico" )
        if os.path.exists( icon_path ) :
            self.setWindowIcon( QIcon( icon_path ) )

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

        # Get auto-save interval from settings (default 5 minutes)
        auto_save_enabled = self.settings.value( "auto_save", True, bool )
        auto_save_interval = self.settings.value( "auto_save_interval", 3e5, int )

        if auto_save_enabled :
            self.auto_save_timer.start( auto_save_interval )

        # Status message reset timer
        self.status_timer = QTimer( self )
        self.status_timer.setSingleShot( True )
        self.status_timer.timeout.connect( self._reset_status )

        # Get status timeout from settings (default 5 seconds)
        self.status_timeout = self.settings.value( "status_timeout", 5e3, int )


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
        self.add_lang_button = QPushButton( "Add" )
        self.add_lang_button.clicked.connect( self._add_language )

        lang_header.addWidget( dialog_label( "Languages" ) )
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
        self.add_ns_button = QPushButton( "Add" )
        self.add_ns_button.clicked.connect( self._add_namespace )

        ns_header.addWidget( dialog_label( "Namespaces" ) )
        ns_header.addWidget( self.add_ns_button )

        self.ns_list = FilterableListWidget()
        self.ns_list.item_selected.connect( self._on_namespace_selected )
        self.ns_list.set_context_menu_policy( Qt.ContextMenuPolicy.CustomContextMenu )
        self.ns_list.customContextMenuRequested( self._show_namespace_context_menu )

        ns_layout.addLayout( ns_header )
        ns_layout.addWidget( self.ns_list )

        # Progress bars
        progress_layout = QVBoxLayout()
        self.language_progress = QProgressBar()
        self.language_progress.setFormat( "%v/%m (%p%)" )
        self.namespace_progress = QProgressBar()
        self.namespace_progress.setFormat( "%v/%m (%p%)" )

        progress_layout.addWidget( dialog_label( "Translation Progress" ) )
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
        self.editor_title = dialog_label( "No Translation Selected", 14 )

        self.add_key_button = QPushButton( "Add Key" )
        self.add_key_button.clicked.connect( self._add_translation_key )
        self.add_key_button.setEnabled( False )

        editor_header.addWidget( self.editor_title, 1 )
        editor_header.addWidget( self.add_key_button )

        # Translation editor
        self.t_editor = TranslationEditor()
        self.t_editor.translation_changed.connect( self._on_translation_changed )
        self.t_editor.key_action_requested.connect( self._on_key_action_requested )
        self.t_editor.translate_requested.connect( self._on_translate_requested )

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
        self.open_action = ui_action( "&Open Project", self, self._show_config_dialog, "Ctrl+O" )
        self.close_action = ui_action( "&Close Project", self, self._close_project, "Ctrl+X" )
        self.save_all_action = ui_action( "&Save All", self, self._save_all, "Ctrl+S" )
        self.export_action = ui_action( "&Export", self, self._show_export_dialog, "Ctrl+E" )
        self.import_action = ui_action( "&Import", self, None, "Ctrl+I" )
        self.options_action = ui_action( "&Options", self, self._show_options_dialog )
        self.exit_action = ui_action( "E&xit", self, self.close, "Ctrl+Q" )

        # Edit actions
        self.sync_action = ui_action( "Synchronize &Keys", self, self._synchronize_keys, "F5" )
        self.reset_filter_action = ui_action( "&Reset Filter", self, self._reset_filter, "Ctrl+R" )
        self.search_action = ui_action( "S&earch", self, self._searching, "F6" )
        self.move_keys_action = ui_action( "&Move Keys", self )
        self.split_ns_action = ui_action( "&Split Namespace", self )
        self.join_ns_action = ui_action( "&Join Namespaces", self )
        self.missing_action = ui_action( "&Missing Translations", self, self._show_missing )
        self.stats_action = ui_action( "S&tatistics", self, self._show_statistics )

        # Help actions
        self.check_updates_action = ui_action( "Check for &Updates", self, self._check_updates )
        self.about_action = ui_action( "&About TranslateHub", self, self._show_about_dialog )
        self.github_action = ui_action(
            "Visit &GitHub Repository", self,
            lambda: QDesktopServices.openUrl(
                QUrl( f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}" )
            )
        )


    def _create_menus ( self ) -> None :
        """Create application menus"""

        self.file_menu = ui_menu( self, "&File", [
            self.open_action, self.save_all_action, self.export_action, self.import_action,
            None, self.options_action, None, self.close_action, self.exit_action
        ] )
        self.edit_menu = ui_menu( self, "&Edit", [
            self.sync_action, self.reset_filter_action, self.search_action, None,
            self.move_keys_action, self.split_ns_action, self.join_ns_action, None,
            self.missing_action, self.stats_action
        ] )
        self.help_menu = ui_menu( self, "&Help", [
            self.check_updates_action, self.github_action, None, self.about_action
        ] )


    def _create_toolbars ( self ) -> None :
        """Create application toolbars"""

        self.main_toolbar = ui_toolbar( "Main", [
            self.open_action, self.save_all_action, self.sync_action,
            self.search_action, self.stats_action
        ], self, False )

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

        dialog = ConfigDialog( self, self.t_manager.file_ops.root_dir )

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


    def _show_options_dialog ( self ) -> None :
        """Show options dialog"""

        dialog = OptionsDialog( self, self.settings )

        if dialog.exec() :
            # Get settings
            settings_dict: Dict = dialog.get_settings_dict()

            # Update schema directory name if changed
            schema_dir_name = settings_dict[ "schema_dir_name" ]
            if schema_dir_name != self.t_manager.file_ops.schema_dir_name :
                self.t_manager.set_schema_dir_name( schema_dir_name )

            # Update auto-save timer
            auto_save_enabled = settings_dict[ "auto_save" ]
            auto_save_interval = settings_dict[ "auto_save_interval" ]

            if auto_save_enabled :
                self.auto_save_timer.start( auto_save_interval )
            else :
                self.auto_save_timer.stop()

            # Update status timeout
            self.status_timeout = settings_dict[ "status_timeout" ]

            # Update translation API
            self.translation_api.update_config(
                settings_dict[ "api_enabled" ],
                settings_dict[ "api_url" ],
                settings_dict[ "api_key" ],
                settings_dict[ "api_pattern" ]
            )


    def _close_project ( self ) -> None :
        """Close the current project"""

        self.settings.remove( "last_directory" )
        self.close()


    def _refresh_ui ( self ) -> None :
        """Refresh the UI with current data"""

        # Update directory label
        if self.t_manager.file_ops.root_dir :
            self.dir_label.setText( self.t_manager.file_ops.root_dir )
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
        if item := self.lang_list.current_item() :
            progress = self.t_manager.get_language_progress( item.text() )
            self.language_progress.setMaximum( progress[ 1 ] )
            self.language_progress.setValue( progress[ 0 ] )
        else :
            self.language_progress.setMaximum( 100 )
            self.language_progress.setValue( 0 )

        # Namespace progress
        if ns_item := self.ns_list.current_item() :
            ns = ns_item.text()

            if lang_item := self.lang_list.current_item() :
                lang = lang_item.text()
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

        lang = self.lang_list.current_item_safe().text()
        ns = self.ns_list.current_item_safe().text()
        translations = self.t_manager.get_translations( lang, ns )

        self.editor_title.setText( f"{lang} - {ns}" )
        self.t_editor.load_translations( lang, ns, translations )
        self.add_key_button.setEnabled( True )

        self._update_progress_bars()


    def _on_translation_changed ( self, lang: str, ns: str, key: str, value: str ) -> None :
        """Handle translation changes"""

        # We don't save immediately to avoid excessive disk I/O
        # Auto-save timer will handle periodic saving
        if key in ( translations := self.t_manager.get_translations( lang, ns ) ) :
            translations[ key ] = value

            # Mark as modified in translation manager
            self.t_manager.mark_as_modified( lang, ns, key )


    def _auto_save ( self ) -> bool :
        """Auto-save current translations"""

        if (
            self.t_editor.current_lang
            and self.t_editor.current_ns
            and self.t_editor.data
            and self.t_editor.modified_keys
        ) :
            # Get compression setting
            self.t_manager.save_translations(
                self.t_editor.current_lang, self.t_editor.current_ns, self.t_editor.data,
                self.settings.value( "compress_json", False, bool )
            )

            self._update_progress_bars()
            self.t_editor.clear_modified()
            self._set_status_message( "Auto-saved translations" )
            return True

        return False


    def _save_all ( self ) -> None :
        """Save all translations"""

        if self._auto_save() :
            self._set_status_message( "All translations saved" )
        else:
            self._set_status_message( "Translation up to date" )


    def _reset_filter ( self ) -> None :
        """Reset filters on language/namespace lists and editor"""

        self.t_editor.reset_filter()
        self.lang_list.filter_input.setText( "" )
        self.ns_list.filter_input.setText( "" )

        self._refresh_ui()


    def _add_language ( self ) -> None :
        """Add a new language"""

        lang, ok = QInputDialog.getText(
            self, "Add Language", "Enter language code (e.g., en-US, de-DE):"
        )

        if ok and lang :
            if self.t_manager.create_language( lang ) :
                self._refresh_ui()
                self._set_status_message( f"Language {lang} added" )
            else :
                QMessageBox.warning( self, "Error", f"Could not create language {lang}" )


    def _add_namespace ( self ) -> None :
        """Add a new namespace"""

        ns, ok = QInputDialog.getText(
            self, "Add Namespace", "Enter namespace name (e.g., app.home):"
        )

        if ok and ns :
            if not ns.endswith( ".json" ) :
                ns = f"{ns}.json"

            if self.t_manager.create_namespace( ns ) :
                self._refresh_ui()
                self._set_status_message( f"Namespace {ns} added" )
            else :
                QMessageBox.warning( self, "Error", f"Could not create namespace {ns}" )


    def _show_language_context_menu ( self, position ) -> None :
        """Show context menu for language list"""

        if not ( item := self.lang_list.current_item() ) :
            return

        lang = item.text()

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

        if not ( item := self.ns_list.current_item() ) :
            return

        ns = item.text()

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
            self, "Rename Language", "Enter new language code:", text= lang
        )

        if ok and new_code and new_code != lang :
            if self.t_manager.rename_language( lang, new_code ) :
                self._refresh_ui()
                self._set_status_message( f"Language renamed to {new_code}" )
            else :
                QMessageBox.warning( self, "Error", f"Could not rename language {lang}" )


    def _rename_namespace ( self, ns: str ) -> None :
        """Rename a namespace"""

        new_name, ok = QInputDialog.getText(
            self, "Rename Namespace", "Enter new namespace name:", text= ns
        )

        if ok and new_name and new_name != ns :
            if not new_name.endswith( ".json" ) :
                new_name = f"{new_name}.json"

            if self.t_manager.rename_namespace( ns, new_name ) :
                self._refresh_ui()
                self._set_status_message( f"Namespace renamed to {new_name}" )
            else :
                QMessageBox.warning( self, "Error", f"Could not rename namespace {ns}" )


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
                self._set_status_message( f"Language {lang} deleted" )
            else :
                QMessageBox.warning( self, "Error", f"Could not delete language {lang}" )


    def _delete_namespace ( self, ns: str ) -> None :
        """Delete a namespace"""

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the namespace '{ns}' from all languages?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes :
            if self.t_manager.delete_namespace( ns ) :
                self._refresh_ui()
                self._set_status_message( f"Namespace {ns} deleted" )
            else:
                QMessageBox.warning( self, "Error", f"Could not delete namespace {ns}" )


    def _add_translation_key ( self ) -> None :
        """Add a new translation key"""

        if not ( item := self.ns_list.current_item() ) :
            return

        ns = item.text()
        dialog = TranslationKeyDialog( self )

        if dialog.exec() :
            key, value = dialog.get_key_value()

            if key :
                if self.t_manager.add_translation_key( ns, key, value ) :
                    self._load_current_translations()
                    self._set_status_message( f"Key '{key}' added to {ns}" )
                else :
                    QMessageBox.warning(
                        self, "Error", f"Could not add key '{key}' to {ns}"
                    )


    def _on_key_action_requested ( self, action: str, key: str ) -> None :
        """Handle key action requests from the editor"""

        if not ( item := self.ns_list.current_item() ) :
            return

        ns = item.text()

        if action == "rename" :
            self._rename_translation_key( ns, key )
        elif action == "delete" :
            self._delete_translation_key( ns, key )


    def _on_translate_requested ( self, lang: str, ns: str, key: str ) -> None :
        """Handle translation request from the editor"""

        if not self.translation_api.is_configured() :
            QMessageBox.warning(
                self, "Translation API Not Configured",
                "Please configure the translation API in the options dialog."
            )
            return

        # Get source text from schema or another language
        source_text = ""
        source_lang = ""

        # First try to get from schema
        schema_data = self.t_manager.get_translations(
            self.t_manager.file_ops.schema_dir_name, ns
        )

        if key in schema_data and schema_data[ key ] :
            source_text = schema_data[ key ]
            source_lang = "en"  # Assume schema is in English

        else :
            # Try to find a non-empty translation in any language
            for other_lang in self.t_manager.get_languages() :
                if other_lang != lang :
                    other_data = self.t_manager.get_translations( other_lang, ns )
                    if key in other_data and other_data[ key ] :
                        source_text = other_data[ key ]
                        source_lang = other_lang.split( "-" )[ 0 ]  # Use base language code
                        break

        if not source_text :
            QMessageBox.warning(
                self, "No Source Text", "Could not find source text for translation."
            )
            return

        # Perform translation
        success, translated_text, error = self.translation_api.translate(
            source_text, source_lang, lang
        )

        if success :
            # Update translation
            translations = self.t_manager.get_translations( lang, ns )
            if key in translations :
                translations[ key ] = translated_text

                # Update editor
                self.t_editor.data[ key ] = translated_text
                self._refresh_ui()
                self._set_status_message( f"Translated key '{key}'" )

                # Mark as modified
                self.t_manager.mark_as_modified( lang, ns, key )
                self.t_editor.mark_as_modified( key )
        else :
            QMessageBox.warning(
                self, "Translation Failed", f"Could not translate text: {error}"
            )


    def _rename_translation_key ( self, ns: str, key: str ) -> None :
        """Rename a translation key"""

        dialog = RenameKeyDialog( self, key )

        if dialog.exec() :
            new_key = dialog.get_new_key()

            if new_key and new_key != key :
                if self.t_manager.rename_translation_key( ns, key, new_key ) :
                    self._load_current_translations()
                    self._set_status_message( f"Key '{key}' renamed to '{new_key}'" )
                else :
                    QMessageBox.warning(
                        self, "Error", f"Could not rename key '{key}' to '{new_key}'"
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
                self._set_status_message( f"Key '{key}' deleted from {ns}" )
            else :
                QMessageBox.warning(
                    self, "Error", f"Could not delete key '{key}' from {ns}"
                )


    def _synchronize_keys ( self ) -> None :
        """Synchronize keys across all languages and namespaces"""

        if changes := self.t_manager.synchronize_keys() :
            total_changes = sum( changes.values() )
            message = (
                f"Synchronized {total_changes} keys across {len( changes )} namespaces"
            )

            QMessageBox.information( self, "Synchronization Complete", message )

            self._refresh_ui()
            self._set_status_message( message )

        else :
            QMessageBox.information(
                self, "Synchronization Complete", "All keys are already synchronized."
            )

            self._set_status_message( "All keys are already synchronized" )


    def _show_missing ( self ) -> None :
        """Show missing translations dialog"""

        dialog = MissingTranslationsDialog( self, self.t_manager )
        dialog.jump_to_translation.connect( self._jump_to_translation )
        dialog.exec()


    def _show_statistics ( self ) -> None :
        """Show translation statistics dialog"""

        dialog = StatisticsDialog( self, self.t_manager )
        dialog.lang_ns_selected.connect( self._select_lang_ns )
        dialog.exec()


    def _searching ( self ) -> None :
        """Open searching dialog"""

        dialog = SearchDialog( self, self.t_manager )
        dialog.jump_to_translation.connect( self._jump_to_translation )
        dialog.exec()


    def _show_export_dialog ( self ) -> None :
        """Show export dialog"""

        dialog = ExportDialog( self, self.t_manager )
        dialog.exec()


    def _select_lang_ns ( self, lang: str, ns: str ) -> None :
        """Select a language and namespace from statistics dialog"""

        # Reset filters
        self._reset_filter()

        # Find and select language and namespace
        self.lang_list.select_item( lang )
        self.ns_list.select_item( ns )


    def _jump_to_translation ( self, lang: str, ns: str, key: str ) -> None :
        """Jump to a specific translation"""

        # Select language and namespace
        self._select_lang_ns( lang, ns )

        # Jump to key in editor
        self.t_editor.jump_to_key( key )


    def _check_updates ( self ) -> None :
        """Check for updates"""

        dialog = UpdateDialog( VERSION, GITHUB_OWNER, GITHUB_REPO, self )
        dialog.exec()


    def _show_about_dialog ( self ) -> None :
        """Show about dialog"""

        dialog = AboutDialog( VERSION, YEAR, GITHUB_OWNER, GITHUB_REPO, self )
        dialog.exec()


    def _set_status_message ( self, message: str ) -> None :
        """Set status bar message with auto-reset"""

        self.status_label.setText( message )

        # Reset status after timeout
        self.status_timer.start( self.status_timeout )


    def _reset_status ( self ) -> None :
        """Reset status bar message to default"""

        self.status_label.setText( "Ready" )


    def closeEvent ( self, event ) -> None :  # pylint: disable=invalid-name
        """Handle window close event"""

        # Save current translations before closing
        self._save_all()
        event.accept()
