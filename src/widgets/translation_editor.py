"""
TranslateHub - Translation Editor
Widget for editing translations
"""

from typing import Dict, Optional, Set

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QCheckBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QTextEdit, QVBoxLayout, QWidget
)


class TranslationEditor ( QWidget ) :
    """Widget for editing translations"""

    translation_changed = pyqtSignal( str, str, str, str )
    key_action_requested = pyqtSignal( str, str )
    translate_requested = pyqtSignal( str, str, str )

    def __init__ ( self, parent: Optional[ QWidget ] = None ) :
        """
        Initialize translation editor
        Args:
            parent: Parent widget
        """

        super().__init__( parent )
        self.current_lang = None
        self.current_ns = None
        self.data = {}
        self.hide_translated = False
        self.modified_keys: Set[ str ] = set()

        self.layout: QVBoxLayout = QVBoxLayout()

        # Options
        options_layout = QHBoxLayout()

        self.hide_translated_cb = QCheckBox( "Hide Translated Values" )
        self.hide_translated_cb.toggled.connect( self._toggle_hide_translated )

        options_layout.addWidget( self.hide_translated_cb )
        options_layout.addStretch()

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText( "Filter key or value ..." )
        self.filter_input.textChanged.connect( self._refresh_grid )

        options_layout.addWidget( self.filter_input )

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
        """
        Load translations into the editor
        Args:
            lang: Language code
            ns: Namespace name
            data: Translation data
        """

        self.current_lang = lang
        self.current_ns = ns
        self.data = data
        self.modified_keys.clear()

        self._refresh_grid()


    def reset_filter ( self ) -> None :
        """Reset the filter input"""

        self.hide_translated_cb.setChecked( False )
        self.filter_input.setText( "" )

        self._refresh_grid()


    def mark_as_modified ( self, key: str ) -> None :
        """Mark a key as modified"""

        self.modified_keys.add( key )


    def clear_modified ( self ) -> None :
        """Clear all modified keys"""

        self.modified_keys.clear()
        self._refresh_grid()


    def jump_to_key ( self, key: str ) -> bool :
        """Jump to a specific key in the editor"""

        if not key in self.data:
            return False

        # Reset filters to ensure the key is visible
        self.hide_translated_cb.setChecked( False )
        self.filter_input.setText( key )

        # Refresh grid to show only the filtered key
        self._refresh_grid()

        return True


    def _refresh_grid ( self ) -> None :
        """Refresh the translation grid"""

        q = self.filter_input.text().lower().strip()

        # Clear existing widgets
        while self.grid_layout.count() :
            item = self.grid_layout.takeAt( 0 )
            if item and ( widget := item.widget() ) :
                widget.deleteLater()

        # Add translation rows
        row = 1
        for key, value in sorted( self.data.items() ) :
            # Skip translated values if hide_translated is enabled
            if ( self.hide_translated and value.strip() ) or (
                q and q not in key.lower() and q not in value.lower()
            ) :
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

            # Highlight modified keys
            if key in self.modified_keys :
                self._highlight_text_field( t_input )

            # Actions
            actions_widget = QWidget()
            actions_layout = QVBoxLayout()
            actions_layout.setAlignment( Qt.AlignmentFlag.AlignTop )
            actions_layout.setContentsMargins( 0, 0, 0, 0 )
            actions_layout.setSpacing( 2 )

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

            translate_btn = QPushButton( "Translate" )
            translate_btn.setProperty( "key", key )
            translate_btn.clicked.connect(
                lambda checked, btn= translate_btn: self.translate_requested.emit(
                    self.current_lang, self.current_ns, btn.property( "key" )
                )
            )

            actions_layout.addWidget( rename_btn )
            actions_layout.addWidget( delete_btn )
            actions_layout.addWidget( translate_btn )

            actions_widget.setLayout( actions_layout )

            self.grid_layout.addWidget( key_label, row, 0 )
            self.grid_layout.addWidget( t_input, row, 1 )
            self.grid_layout.addWidget( actions_widget, row, 2 )
            row += 1

        # Add headers if there are rows
        if row > 1 :
            self.grid_layout.addWidget( QLabel( "Key" ), 0, 0 )
            self.grid_layout.addWidget( QLabel( "Translation" ), 0, 1 )
            self.grid_layout.addWidget( QLabel( "Actions" ), 0, 2 )


    def _on_translation_changed ( self, input_widget: QTextEdit ) -> None :
        """Handle translation text changes"""

        if not self.current_lang or not self.current_ns :
            return

        key = input_widget.property( "key" )
        value = input_widget.toPlainText()

        if key in self.data :
            self.mark_as_modified( key )
            self._highlight_text_field( input_widget )

            # Update data and emit signal
            self.data[ key ] = value
            self.translation_changed.emit(
                self.current_lang, self.current_ns, key, value
            )


    def _highlight_text_field ( self, input_widget: QTextEdit ) -> None :
        """Highlight a text field to indicate modification"""

        palette = input_widget.palette()
        palette.setColor( QPalette.ColorRole.Text, QColor( 76, 187, 23 ) )
        input_widget.setPalette( palette )
        input_widget.setFont( QFont( "Sans-serif", weight= QFont.Weight.Bold ) )


    def _toggle_hide_translated ( self, checked: bool ) -> None :
        """Toggle hiding of translated values"""

        self.hide_translated = checked
        if self.current_lang and self.current_ns :
            self._refresh_grid()
