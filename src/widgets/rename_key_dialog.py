"""
TranslateHub - Rename Key Dialog
Dialog for renaming translation keys
"""


from typing import Union

from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout,
    QWidget
)

from ._button_box import ok_close


class RenameKeyDialog ( QDialog ) :
    """Dialog for renaming translation keys"""

    def __init__ ( self, parent: Union[ QWidget, None ] = None, old_key: str = "" ) :
        """Initialize rename translation key dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Rename Translation Key" )
        self.resize( 400, 120 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Old key display
        old_key_layout = QHBoxLayout()
        self.old_key_label = QLabel( "Current Key:" )
        self.old_key_display = QLineEdit( old_key )
        self.old_key_display.setReadOnly( True )

        old_key_layout.addWidget( self.old_key_label )
        old_key_layout.addWidget( self.old_key_display, 1 )

        self.layout.addLayout( old_key_layout )

        # New key input
        new_key_layout = QHBoxLayout()
        self.new_key_label = QLabel( "New Key:" )
        self.new_key_input = QLineEdit()

        new_key_layout.addWidget( self.new_key_label )
        new_key_layout.addWidget( self.new_key_input, 1 )

        self.layout.addLayout( new_key_layout )

        # Dialog buttons
        self.button_box = ok_close( self.accept, self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )


    def get_new_key ( self ) -> str :
        """Get the entered new key"""
        return self.new_key_input.text()
