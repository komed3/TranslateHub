"""
TranslateHub - Missing Translations Dialog
Dialog showing missing translations for all languages and namespaces
"""

from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..core import TranslationManager
from ..helpers import refresh_close


class MissingTranslationsDialog ( QDialog ) :
    """Dialog showing missing translations for all languages and namespaces"""

    # Signal to jump to a specific translation in the editor
    jump_to_translation = pyqtSignal( str, str, str )

    def __init__ (
        self, parent: Optional[ QWidget ] = None,
        t_manager: Optional[ TranslationManager ] = None
    ) :
        """
        Initialize missing translations dialog
        Args:
            parent: Parent widget
            t_manager: Translation manager
        """

        super().__init__( parent )
        self.t_manager = t_manager
        self.setWindowTitle( "Missing Translations" )
        self.resize( 900, 600 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Missing translations table
        self.table = QTableWidget()
        self.table.setEditTriggers( QTableWidget.EditTrigger.NoEditTriggers )
        self.table.cellDoubleClicked.connect( self._on_cell_double_clicked )
        self.layout.addWidget( self.table )

        # Refresh and close button
        self.layout.addWidget( refresh_close( self._populate, self.reject ) )

        self.setLayout( self.layout )

        # Populate missing translations
        self._populate()


    def _populate ( self ) -> None :
        """Populate table with missing translations"""

        if not self.t_manager :
            return

        # Gather missing translations
        rows: List[ Tuple[ str, str, str ] ] = []
        for lang in self.t_manager.get_languages() :
            for ns in self.t_manager.get_namespaces() :
                data = self.t_manager.get_translations( lang, ns )

                for key, value in data.items() :
                    if not value.strip() :
                        rows.append( ( lang, ns, key ) )

        # Populate table
        self.table.clear()
        self.table.setColumnCount( 3 )
        self.table.setHorizontalHeaderLabels( [ "Language", "Namespace", "Key" ] )
        self.table.setRowCount( len( rows ) )

        for i, ( lang, ns, key ) in enumerate( rows ) :
            lang_item = QTableWidgetItem( lang )
            ns_item = QTableWidgetItem( ns )
            key_item = QTableWidgetItem( key )

            # Store data for double-click handling
            lang_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )
            ns_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )
            key_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )

            # Set tooltip to indicate double-click action
            tooltip = "Double-click to jump to this translation"
            lang_item.setToolTip( tooltip )
            ns_item.setToolTip( tooltip )
            key_item.setToolTip( tooltip )

            self.table.setItem( i, 0, lang_item )
            self.table.setItem( i, 1, ns_item )
            self.table.setItem( i, 2, key_item )

        # Resize columns/rows to content
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()


    def _on_cell_double_clicked ( self, row: int, column: int ) -> None :
        """Handle cell double-click to jump to translation"""

        if item := self.table.item( row, column ) :
            data = item.data( Qt.ItemDataRole.UserRole )
            if data :
                lang, ns, key = data
                self.jump_to_translation.emit( lang, ns, key )
                self.accept()
