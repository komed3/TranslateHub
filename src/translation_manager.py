"""
TranslateHub - Translation Manager Module
Handles all operations related to translation files
"""

import json
import os
import shutil
from typing import List

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


    def _write_file ( self, lang: str, namespace: str, data: object | None = None ) -> None :
        """Write data to a specific language and namespace file"""

        path = os.path.join( self.root_dir or '', lang, namespace )
        with open( path, 'w', encoding= 'utf-8' ) as nf :
            json.dump( data or {}, nf, ensure_ascii= False, indent= 2 )
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
                        try :
                            empty_data = { k: "" for k in json.load( f ).keys() }
                            self._write_file( language_code, namespace, empty_data )
                        except json.JSONDecodeError :
                            self._write_file( language_code, namespace )

            # If no languages exist yet, create empty file
            else :
                with open( os.path.join( lang_dir, namespace ), 'w', encoding= 'utf-8' ) as f :
                    json.dump( {}, f, ensure_ascii= False, indent= 2 )

        self.languages.add( language_code )
        return True


    def create_namespace ( self, namespace: str ) -> bool :
        """Create a new namespace in all languages"""

        if not namespace.endswith( '.json' ) :
            namespace = f"{namespace}.json"

        if not self.root_dir or namespace in self.namespaces :
            return False

        # Create namespace file in all languages
        for lang in self.languages :
            self._write_file( lang, namespace )

        self.namespaces.add( namespace )
        return True


    def delete_language ( self, language_code: str ) -> bool :
        """Delete a language and all its namespace files"""

        if not self.root_dir or language_code not in self.languages :
            return False

        lang_dir = os.path.join( self.root_dir, language_code )
        try :
            shutil.rmtree( lang_dir )
            self.languages.remove( language_code )
            return True
        except shutil.Error :
            return False


    def delete_namespace ( self, namespace: str ) -> bool :
        """Delete a namespace from all languages"""

        if not self.root_dir or namespace not in self.namespaces :
            return False

        success = True
        for lang in self.languages :
            file_path = os.path.join( self.root_dir, lang, namespace )
            try :
                if os.path.exists( file_path ) :
                    os.remove( file_path )
            except OSError :
                success = False

        if success :
            self.namespaces.remove( namespace )

        return success


    def rename_language ( self, old_code: str, new_code: str ) -> bool :
        """Rename a language folder"""

        if not self.root_dir or old_code not in self.languages or new_code in self.languages :
            return False

        old_path = os.path.join( self.root_dir, old_code )
        new_path = os.path.join( self.root_dir, new_code )
        try :
            os.rename( old_path, new_path )
            self.languages.remove( old_code )
            self.languages.add( new_code )
            return True
        except OSError :
            return False


    def rename_namespace ( self, old_name: str, new_name: str ) -> bool :
        """Rename a namespace in all languages"""

        if not self.root_dir or old_name not in self.namespaces or new_name in self.namespaces :
            return False

        if not new_name.endswith( '.json' ) :
            new_name = f"{new_name}.json"

        success = True
        for lang in self.languages :
            old_path = os.path.join( self.root_dir, lang, old_name )
            new_path = os.path.join( self.root_dir, lang, new_name )
            try :
                if os.path.exists( old_path ) :
                    os.rename( old_path, new_path )
            except OSError :
                success = False

        if success :
            self.namespaces.remove( old_name )
            self.namespaces.add( new_name )

        return success
