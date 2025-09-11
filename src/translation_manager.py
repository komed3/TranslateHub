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


    def _write_file ( self, lang: str, namespace: str, data: object = {} ) -> None :
        """Write data to a specific language and namespace file"""

        with open( os.path.join( self.root_dir or '', lang, namespace ), 'w', encoding= 'utf-8' ) as nf :
            json.dump( data, nf, ensure_ascii= False, indent= 2 )
            nf.write( '\n\n' )


    def get_languages ( self ) -> List[ str ] :
        """Get all available languages"""
        return sorted( list( self.languages ) )


    def get_namespaces ( self ) -> List[ str ] :
        """Get all available namespaces"""
        return sorted( list( self.namespaces ) )


    def create_language ( self, language_code: str ) -> bool :
        """Create a new language with all existing namespaces"""

        if not self.root_dir or language_code in self.languages :
            return False

        # Create language directory
        lang_dir = os.path.join( self.root_dir, language_code )
        os.makedirs( lang_dir, exist_ok= True )

        # Create all namespace files with empty translations
        # For each namespace, copy keys from an existing language
        for namespace in self.namespaces :
            if self.languages :

                # Use the first language as a template
                template_lang = next( iter( self.languages ) )
                template_file = os.path.join( self.root_dir, template_lang, namespace )
                if os.path.exists( template_file ) :
                    with open( template_file, 'r', encoding= 'utf-8' ) as f :

                        # Create empty translations with the same keys
                        # If template file is invalid, create empty file
                        try:
                            empty_data = { k: "" for k in json.load( f ).keys() }
                            self._write_file( language_code, namespace, empty_data )
                        except json.JSONDecodeError :
                            self._write_file( language_code, namespace )

            # If no languages exist yet, create empty file
            else:
                with open( os.path.join( lang_dir, namespace ), 'w', encoding= 'utf-8' ) as f :
                    json.dump( {}, f, ensure_ascii= False, indent= 2 )

        self.languages.add( language_code )
        return True


    def create_namespace ( self, namespace: str ) -> bool :
        """Create a new namespace in all languages"""

        if not namespace.endswith( '.json' ):
            namespace = f"{namespace}.json"

        if not self.root_dir or namespace in self.namespaces :
            return False

        # Create namespace file in all languages
        for lang in self.languages :
            self._write_file( lang, namespace )

        self.namespaces.add( namespace )
        return True
