"""
TranslateHub - Missing Translations Dialog
Dialog showing missing translations for all languages and namespaces
"""


from typing import Union

from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..helper._button_box import refresh_close
from ..translation_manager import TranslationManager


class MissingTranslationsDialog ( QDialog ) :
    """Dialog showing missing translations for all languages and namespaces"""

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        t_manager: Union[ TranslationManager, None ] = None
    ) :
        """Initialize missing translations dialog"""

        super().__init__( parent )
        self.t_manager = t_manager
        self.setWindowTitle( "Missing Translations" )
        self.resize( 900, 600 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Missing translations table
        self.table = QTableWidget()
        self.layout.addWidget( self.table )

        # Refresh and close button
        self.button_box = refresh_close( self._populate, self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )

        self._populate()


    def _populate ( self ) -> None :
        """Populate table with missing translations"""

        if not self.t_manager :
            return

        # Gather missing translations
        rows = []
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
            self.table.setItem( i, 0, QTableWidgetItem( lang ) )
            self.table.setItem( i, 1, QTableWidgetItem( ns ) )
            self.table.setItem( i, 2, QTableWidgetItem( key ) )

        # Resize columns/rows to content
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
