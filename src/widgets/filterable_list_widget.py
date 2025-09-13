"""
TranslateHub - Filterable List Widget
List widget with search / filter functionality
"""

from typing import List, Optional, cast

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QVBoxLayout, QWidget
)


class FilterableListWidget ( QWidget ) :
    """List widget with search/filter functionality"""

    item_selected = pyqtSignal( QListWidgetItem )

    def __init__ ( self, parent: Optional[ QWidget ] = None ) :
        """
        Initialize filterable list widget
        Args:
            parent: Parent widget
        """

        super().__init__( parent )
        self.all_items = []

        self.layout: QVBoxLayout = QVBoxLayout()
        self.layout.setContentsMargins( 0, 0, 0, 0 )

        # Header with title and filter
        header_layout = QHBoxLayout()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText( "Filter ..." )
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


    def add_items ( self, items: List[ str ] ) -> None :
        """Add multiple items to the list"""

        self.all_items.extend( items )
        self._apply_filter( self.filter_input.text() )


    def clear ( self ) -> None :
        """Clear all items"""

        self.list_widget.clear()
        self.all_items = []


    def current_item ( self ) -> Optional[ QListWidgetItem ] :
        """Get the current selected item"""

        return self.list_widget.currentItem()


    def current_item_safe ( self ) -> QListWidgetItem :
        """Get the current selected item, guaranteed to be not None"""

        return cast( QListWidgetItem, self.list_widget.currentItem() )


    def set_context_menu_policy ( self, policy ) -> None :
        """Set the context menu policy"""

        self.list_widget.setContextMenuPolicy( policy )


    def customContextMenuRequested ( self, handler ) -> None :
        """Connect custom context menu handler"""

        self.list_widget.customContextMenuRequested.connect( handler )


    def select_item ( self, text: str ) -> bool :
        """Select an item by its text; returns True if selected, False otherwise"""

        for i in range( self.list_widget.count() ) :
            item = self.list_widget.item( i )
            if item and item.text() == text :
                self.list_widget.setCurrentItem( item )
                return True
        return False


    def _apply_filter ( self, filter_text: str = "" ) -> None :
        """Apply filter to the list"""

        self.list_widget.clear()
        filter_text = filter_text.lower()

        for text in self.all_items :
            if not filter_text or filter_text in text.lower() :
                self.list_widget.addItem( QListWidgetItem( text ) )


    def _on_item_selected ( self, current ) -> None :
        """Handle item selection"""

        if current :
            self.item_selected.emit( current )
