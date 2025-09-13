"""
TranslateHub - Statistics Dialog
Dialog showing translation statistics
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget
)

from ..core import TranslationManager
from ..helpers import refresh_close


class StatisticsDialog ( QDialog ) :
    """Dialog showing translation statistics"""

    lang_ns_selected = pyqtSignal( str, str )

    def __init__ (
        self, parent: Optional[ QWidget ] = None,
        t_manager: Optional[ TranslationManager ] = None
    ) :
        """
        Initialize statistics dialog
        Args:
            parent: Parent widget
            t_manager: Translation manager
        """

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
        self.layout.addWidget( refresh_close( self._populate, self.reject ) )

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
        langs = sorted( self.t_manager.get_languages() )
        ns_len = len( ns )
        langs_len = len( langs )

        # Set up table
        self.table.clear()
        self.table.setColumnCount( ns_len + 1 )
        self.table.setRowCount( langs_len + 1 )

        # Set horizontal headers (namespaces)
        self.table.setHorizontalHeaderItem( ns_len, QTableWidgetItem( "Total" ) )
        for i, n in enumerate( ns ) :
            self.table.setHorizontalHeaderItem( i, QTableWidgetItem( n ) )

        # Set vertical headers (languages)
        self.table.setVerticalHeaderItem( langs_len, QTableWidgetItem( "Total" ) )
        for i, l in enumerate( langs ) :
            self.table.setVerticalHeaderItem( i, QTableWidgetItem( l ) )

        total_translated = 0
        total_keys = 0

        ns_total_translated = [ 0 ] * ns_len
        ns_total_keys = [ 0 ] * ns_len
        langs_total_translated = [ 0 ] * langs_len
        langs_total_keys = [ 0 ] * langs_len

        # Fill data
        for i, l in enumerate( langs ) :
            for j, n in enumerate( ns ) :
                if l in pg_data and n in pg_data[ l ] :
                    done, total = pg_data[ l ][ n ]
                    item = self._progress_cell( done, total )

                    # Store language and namespace for double-click handling
                    item.setData( Qt.ItemDataRole.UserRole, ( l, n ) )
                    item.setToolTip( "Double-click to open this translation" )

                    self.table.setItem( i, j, item )

                    total_translated += done
                    total_keys += total

                    ns_total_translated[ j ] += done
                    ns_total_keys[ j ] += total
                    langs_total_translated[ i ] += done
                    langs_total_keys[ i ] += total

        # Fill totals for languages
        for i, t in enumerate( langs_total_keys ) :
            item = self._progress_cell( langs_total_translated[ i ], t )
            self.table.setItem( i, ns_len, item )

        # Fill totals for namespaces
        for j, t in enumerate( ns_total_keys ) :
            item = self._progress_cell( ns_total_translated[ j ], t )
            self.table.setItem( langs_len, j, item )

        # Fill overall total
        item = self._progress_cell( total_translated, total_keys )
        self.table.setItem( langs_len, ns_len, item )

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
                item.setBackground( QColor( 200, 255, 200 ) )  # Light green
            elif pct >= 75 :
                item.setBackground( QColor( 255, 255, 200 ) )  # Light yellow
            elif pct >= 50 :
                item.setBackground( QColor( 255, 225, 200 ) )  # Light orange
            elif pct >= 25 :
                item.setBackground( QColor( 255, 200, 200 ) )  # Light red
            else:
                item.setBackground( QColor( 255, 200, 255 ) )  # Light purple

        else:
            item = QTableWidgetItem( "N/A" )

        return item


    def _on_cell_double_clicked ( self, row: int, col: int ) -> None :
        """Handle cell double click to navigate to language/namespace"""

        if not self.t_manager :
            return

        langs = sorted( self.t_manager.get_languages() )
        ns = sorted( self.t_manager.get_namespaces() )

        if 0 <= row < len( langs ) and 0 <= col < len( ns ) :
            item = self.table.item( row, col )
            if item :
                data = item.data( Qt.ItemDataRole.UserRole )
                if data :
                    lang, namespace = data
                    self.lang_ns_selected.emit( lang, namespace )
                    self.accept()
