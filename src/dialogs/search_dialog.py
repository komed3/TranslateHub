"""
TranslateHub - Search Dialog
Dialog to search translations in the loaded translation files
"""

from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget
)

from ..core import TranslationManager
from ..helpers import close


class SearchDialog ( QDialog ) :
    """Dialog to search translations in the loaded translation files"""

    # Signal to jump to a specific translation in the editor
    jump_to_translation = pyqtSignal( str, str, str )

    def __init__ (
        self, parent: Optional[ QWidget ] = None,
        t_manager: Optional[ TranslationManager ] = None
    ) :
        """
        Initialize search dialog
        Args:
            parent: Parent widget
            t_manager: Translation manager
        """

        super().__init__( parent )
        self.t_manager = t_manager
        self.setWindowTitle( "Search Translations" )
        self.resize( 900, 600 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Search input and options
        self.search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText( "Search ..." )

        self.case_sensitive_cb = QCheckBox( "Case sensitive" )

        self.search_layout.addWidget( self.search_input, 1 )
        self.search_layout.addWidget( self.case_sensitive_cb )
        self.layout.addLayout( self.search_layout )

        # Results table
        self.table = QTableWidget()
        self.table.setEditTriggers( QTableWidget.EditTrigger.NoEditTriggers )
        self.table.cellDoubleClicked.connect( self._on_cell_double_clicked )
        self.layout.addWidget( self.table )

        # Close button
        self.layout.addWidget( close( self.reject ) )

        self.setLayout( self.layout )

        # Connect signals
        self.search_input.textChanged.connect( self._search )
        self.case_sensitive_cb.toggled.connect( self._search )


    def _search ( self ) -> None :
        """Perform search and update results table"""

        if not self.t_manager :
            return

        # Get search parameters
        q = self.search_input.text()
        cs = self.case_sensitive_cb.isChecked()

        # Perform search
        results = self.t_manager.search( q, cs )

        # Flatten results
        rows: List[ Tuple[ str, str, str, str ] ] = []
        for lang, ns_dict in results.items() :
            for ns, key_dict in ns_dict.items() :
                for key, value in key_dict.items() :
                    rows.append( ( lang, ns, key, value ) )

        # Populate table
        self.table.clear()
        self.table.setColumnCount( 4 )
        self.table.setHorizontalHeaderLabels( [ "Language", "Namespace", "Key", "Value" ] )
        self.table.setRowCount( len( rows ) )

        for i, ( lang, ns, key, value ) in enumerate( rows ) :
            lang_item = QTableWidgetItem( lang )
            ns_item = QTableWidgetItem( ns )
            key_item = QTableWidgetItem( key )
            value_item = QTableWidgetItem( value )

            # Store data for double-click handling
            lang_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )
            ns_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )
            key_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )
            value_item.setData( Qt.ItemDataRole.UserRole, ( lang, ns, key ) )

            # Set tooltip to indicate double-click action
            tooltip = "Double-click to jump to this translation"
            lang_item.setToolTip( tooltip )
            ns_item.setToolTip( tooltip )
            key_item.setToolTip( tooltip )
            value_item.setToolTip( tooltip )

            self.table.setItem( i, 0, lang_item )
            self.table.setItem( i, 1, ns_item )
            self.table.setItem( i, 2, key_item )
            self.table.setItem( i, 3, value_item )

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
