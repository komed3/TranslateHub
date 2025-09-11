"""
TranslateHub - Translation Manager Module
Handles all operations related to translation files
"""

import json
import os
from pathlib import Path
import shutil
from typing import Dict, List, Tuple

class TranslationManager :
    """Manages translation files and operations"""

    def __init__ ( self, root_dir: str | None = None ) :
        """Initialize the translation manager with a root directory"""

        self.root_dir = root_dir
        self.languages = set()
        self.namespaces = set()
        self._load_structure()


    def set_root_dir ( self, root_dir: str ) -> bool :
        """Set the root directory and reload the structure"""

        if not os.path.isdir( root_dir ) :
            return False

        self.root_dir = root_dir
        self._load_structure()
        return True

    def _load_structure ( self ) -> None :
        """Load the existing languages and namespaces from the root directory"""

        if not self.root_dir or not os.path.isdir( self.root_dir ) :
            self.languages = set()
            self.namespaces = set()
            return

        # Get all language directories
        self.languages = {
            d for d in os.listdir( self.root_dir ) 
            if os.path.isdir( os.path.join( self.root_dir, d ) )
        }

        # Get all unique namespaces across all languages
        self.namespaces = set()
        for lang in self.languages :
            lang_dir = os.path.join( self.root_dir, lang )
            for file in os.listdir( lang_dir ) :
                if file.endswith( '.json' ) :
                    self.namespaces.add( file )

    def get_languages ( self ) -> List[ str ] :
        """Get all available languages"""
        return sorted( list( self.languages ) )

    def get_namespaces ( self ) -> List[ str ] :
        """Get all available namespaces"""
        return sorted( list( self.namespaces ) )

