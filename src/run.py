"""
TranslateHub - Runner
Run the TranslateHub application
"""

import sys
from PyQt6.QtWidgets import QApplication

from .main import TranslateHub, VERSION


def launch () -> None :
    """Main application entry point"""

    app = QApplication( sys.argv )

    # Use Fusion style for consistent cross-platform look
    app.setStyle( "Fusion" )

    # Set application information
    app.setApplicationName( "TranslateHub" )
    app.setApplicationVersion( VERSION )
    app.setOrganizationName( "komed3 (Paul Köhler)" )

    window = TranslateHub()
    window.show()

    sys.exit( app.exec() )
