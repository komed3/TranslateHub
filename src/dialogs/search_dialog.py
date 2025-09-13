"""
TranslateHub - Search Dialog
Dialog to search translations in the loaded translation files
"""


from typing import Union

from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget
)

from ..lib._button_box import close
from ..translation_manager import TranslationManager


class SearchDialog ( QDialog ) :
    """Dialog to search translations in the loaded translation files"""

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        t_manager: Union[ TranslationManager, None ] = None
    ) :
        """Initialize search dialog"""

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
        self.layout.addWidget( self.table )

        # Close button
        self.button_box = close( self.reject )
        self.layout.addWidget( self.button_box )

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
        rows = []
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
            self.table.setItem( i, 0, QTableWidgetItem( lang ) )
            self.table.setItem( i, 1, QTableWidgetItem( ns ) )
            self.table.setItem( i, 2, QTableWidgetItem( key ) )
            self.table.setItem( i, 3, QTableWidgetItem( value ) )

        # Resize columns/rows to content
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
