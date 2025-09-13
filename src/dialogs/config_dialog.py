"""
TranslateHub - Config Dialog
Dialog for configuring the application
"""


from pathlib import Path
from typing import Union

from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget
)

from ..lib._button_box import ok_close


class ConfigDialog ( QDialog ) :
    """Dialog for configuring the application"""

    def __init__ (
        self, parent: Union[ QWidget, None ] = None,
        current_dir: Union[ str, None ] = None
    ) :
        """Initialize configuration dialog"""

        super().__init__( parent )
        self.setWindowTitle( "Configuration" )
        self.resize( 500, 200 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Root directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel( "Translation Root Directory:" )
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton( "Browse..." )
        self.dir_button.clicked.connect( self.browse_directory )

        if current_dir:
            self.dir_input.setText( current_dir )

        dir_layout.addWidget( self.dir_label )
        dir_layout.addWidget( self.dir_input, 1 )
        dir_layout.addWidget( self.dir_button )

        self.layout.addLayout( dir_layout )

        # Dialog buttons
        self.button_box = ok_close( self.accept, self.reject )
        self.layout.addWidget( self.button_box )

        self.setLayout( self.layout )


    def browse_directory ( self ) -> None :
        """Open file dialog to select root directory"""

        directory = QFileDialog.getExistingDirectory(
            self, "Select Translation Root Directory",
            self.dir_input.text() or str( Path.home() )
        )

        if directory:
            self.dir_input.setText( directory )


    def get_root_directory( self ) -> str :
        """Get the selected root directory"""
        return self.dir_input.text()
