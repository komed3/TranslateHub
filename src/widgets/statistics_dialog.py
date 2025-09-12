"""
TranslateHub - Statistics Dialog
Dialog showing translation statistics
"""


from typing import Union

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget
)

from ._button_box import refresh_close
from ..translation_manager import TranslationManager


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

        # Refresh and close button
        self.button_box = refresh_close( self._populate, self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )

        # Load statistics
        self._populate()


    def _populate ( self ) -> None :
        """Populate translation statistics"""

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
