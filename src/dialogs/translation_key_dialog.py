"""
TranslateHub - Translation Key Dialog
Dialog for adding or editing translation keys
"""


from typing import Tuple, Union

from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget
)

from ..helper._button_box import ok_close


class TranslationKeyDialog ( QDialog ) :
    """Dialog for adding or editing translation keys"""

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        key: str = "", value: str = "", edit_mode: bool = False
    ) :
        """Initialize translation key dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Add Translation Key" if not edit_mode else "Edit Translation Key" )
        self.resize( 400, 200 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Key input
        key_layout = QHBoxLayout()
        self.key_label = QLabel( "Key:" )
        self.key_input = QLineEdit( key )
        self.key_input.setReadOnly( edit_mode )

        key_layout.addWidget( self.key_label )
        key_layout.addWidget( self.key_input, 1 )

        self.layout.addLayout( key_layout )

        # Value input
        value_layout = QVBoxLayout()
        self.value_label = QLabel( "Default Value:" )
        self.value_input = QTextEdit()
        self.value_input.setPlainText( value )

        value_layout.addWidget( self.value_label )
        value_layout.addWidget( self.value_input )

        self.layout.addLayout( value_layout )

        # Dialog buttons
        self.button_box = ok_close( self.accept, self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )


    def get_key_value ( self ) -> Tuple[ str, str ] :
        """Get the entered key and value"""
        return self.key_input.text(), self.value_input.toPlainText()
