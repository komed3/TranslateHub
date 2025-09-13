"""
TranslateHub - Export Dialog
Dialog for exporting translations
"""

from typing import List, Optional, Tuple

import os
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QVBoxLayout, QWidget
)

from ..core import TranslationManager
from ..helpers import export_button_box


class ExportDialog ( QDialog ) :
    """Dialog for exporting translations"""

    def __init__ (
        self, parent: Optional[ QWidget ] = None,
        t_manager: Optional[ TranslationManager ] = None
    ) :
        """
        Initialize export dialog
        Args:
            parent: Parent widget
            t_manager: Translation manager
        """

        super().__init__( parent )
        self.t_manager = t_manager
        self.setWindowTitle( "Export Translations" )
        self.resize( 700, 500 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Selection area
        selection_layout = QHBoxLayout()

        # Languages selection
        self.lang_list = QListWidget()
        self.lang_list.setSelectionMode( QListWidget.SelectionMode.MultiSelection )

        lang_layout = QVBoxLayout()
        lang_layout.addWidget( QLabel( "Languages:" ) )
        lang_layout.addWidget( self.lang_list )

        # Namespaces selection
        self.ns_list = QListWidget()
        self.ns_list.setSelectionMode( QListWidget.SelectionMode.MultiSelection )

        ns_layout = QVBoxLayout()
        ns_layout.addWidget( QLabel( "Namespaces:" ) )
        ns_layout.addWidget( self.ns_list )

        selection_layout.addLayout( lang_layout )
        selection_layout.addLayout( ns_layout )

        self.layout.addLayout( selection_layout )

        # Options
        options_layout = QHBoxLayout()

        self.include_schema_cb = QCheckBox( "Include schema directory" )
        options_layout.addWidget( self.include_schema_cb )
        options_layout.addStretch()

        self.layout.addLayout( options_layout )

        # Dialog buttons
        self.button_box = export_button_box( self._export_selected, self._export_all, self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )

        # Populate lists
        self._populate_lists()


    def _populate_lists ( self ) -> None :
        """Populate language and namespace lists"""

        if not self.t_manager :
            return

        # Populate language list
        self.lang_list.clear()
        for lang in self.t_manager.get_languages() :
            self.lang_list.addItem( QListWidgetItem( lang ) )

        # Populate namespace list
        self.ns_list.clear()
        for ns in self.t_manager.get_namespaces() :
            self.ns_list.addItem( QListWidgetItem( ns ) )


    def _get_selected_items ( self ) -> Tuple[ List[ str ], List[ str ] ] :
        """Get selected languages and namespaces"""

        selected_langs = []
        for i in range( self.lang_list.count() ) :
            item = self.lang_list.item( i )
            if item and item.isSelected() :
                selected_langs.append( item.text() )

        selected_ns = []
        for i in range( self.ns_list.count() ) :
            item = self.ns_list.item( i )
            if item and item.isSelected() :
                selected_ns.append( item.text() )

        return selected_langs, selected_ns


    def _export_selected ( self ) -> None :
        """Export selected languages and namespaces"""

        if not self.t_manager :
            return

        selected_langs, selected_ns = self._get_selected_items()

        if not selected_langs or not selected_ns :
            return

        self._perform_export( selected_langs, selected_ns )


    def _export_all ( self ) -> None :
        """Export all languages and namespaces"""

        if not self.t_manager :
            return

        languages = self.t_manager.get_languages()
        namespaces = self.t_manager.get_namespaces()

        self._perform_export( languages, namespaces )


    def _perform_export ( self, languages: List[ str ], namespaces: List[ str ] ) -> None :
        """Perform the export operation"""

        if not self.t_manager :
            return

        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export File",
            os.path.expanduser( "~/translations_export.zip" ),
            "ZIP Files (*.zip)"
        )

        if not file_path :
            return

        # Add .zip extension if not present
        if not file_path.lower().endswith( ".zip" ) :
            file_path += ".zip"

        # Perform export
        include_schema = self.include_schema_cb.isChecked()

        self.t_manager.export_translations(
            languages, namespaces, include_schema, file_path
        )

        self.accept()
