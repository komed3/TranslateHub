"""
TranslateHub - Translation Manager Module
Handles all operations related to translation files
"""

import json
import os
import shutil
from typing import Dict, List, Union

class TranslationManager :
    """Manages translation files and operations"""

    def __init__ ( self, root_dir: Union[ str, None ] = None ) :
        """Initialize the translation manager with a root directory"""

        self.root_dir = root_dir
        self.lngs = set()
        self.ns = set()
        self._load_structure()


    def set_root_dir ( self, root_dir: str ) -> bool :
        """Set the root directory and reload the structure"""

        if not os.path.isdir( root_dir ) :
            return False

        self.root_dir = root_dir
        self._load_structure()
        return True


    def _load_structure ( self ) -> None :
        """Load the existing lngs and nss from the root directory"""

        if not self.root_dir or not os.path.isdir( self.root_dir ) :
            self.lngs = set()
            self.ns = set()
            return

        # Get all language directories
        self.lngs = {
            d for d in os.listdir( self.root_dir )
            if os.path.isdir( os.path.join( self.root_dir, d ) )
        }

        # Get all unique nss across all lngs
        self.ns = set()
        for lang in self.lngs :
            lang_dir = os.path.join( self.root_dir, lang )
            for file in os.listdir( lang_dir ) :
                if file.endswith( '.json' ) :
                    self.ns.add( file )


    def _write_file ( self, lang: str, ns: str, data: Union[ object, None ] = None ) -> bool :
        """Write data to a specific language and ns file"""

        path = os.path.join( self.root_dir or '', lang, ns )
        try :
            with open( path, 'w', encoding= 'utf-8' ) as f :
                json.dump( data or {}, f, ensure_ascii= False, indent= 2 )
                f.write( '\n\n' )
            return True
        except OSError :
            return False


    def get_lngs ( self ) -> List[ str ] :
        """Get all available lngs"""
        return sorted( list( self.lngs ) )


    def get_nss ( self ) -> List[ str ] :
        """Get all available nss"""
        return sorted( list( self.ns ) )


    def create_language ( self, lang_code: str ) -> bool :
        """Create a new language with all existing nss"""

        if not self.root_dir or lang_code in self.lngs :
            return False

        # Create language directory
        lang_dir = os.path.join( self.root_dir, lang_code )
        os.makedirs( lang_dir, exist_ok= True )

        # Create all ns files with empty translations
        # For each ns, copy keys from an existing language
        for ns in self.ns :
            if self.lngs :

                # Use the first language as a template
                template_lang = next( iter( self.lngs ) )
                template_file = os.path.join( self.root_dir, template_lang, ns )
                if os.path.exists( template_file ) :
                    with open( template_file, 'r', encoding= 'utf-8' ) as f :

                        # Create empty translations with the same keys
                        # If template file is invalid, create empty file
                        try :
                            empty_data = { k: "" for k in json.load( f ).keys() }
                            self._write_file( lang_code, ns, empty_data )
                        except json.JSONDecodeError :
                            self._write_file( lang_code, ns )

            # If no lngs exist yet, create empty file
            else :
                with open( os.path.join( lang_dir, ns ), 'w', encoding= 'utf-8' ) as f :
                    json.dump( {}, f, ensure_ascii= False, indent= 2 )

        self.lngs.add( lang_code )
        return True


    def create_ns ( self, ns: str ) -> bool :
        """Create a new ns in all lngs"""

        if not ns.endswith( '.json' ) :
            ns = f"{ns}.json"

        if not self.root_dir or ns in self.ns :
            return False

        # Create ns file in all lngs
        for lang in self.lngs :
            self._write_file( lang, ns )

        self.ns.add( ns )
        return True


    def delete_language ( self, lang_code: str ) -> bool :
        """Delete a language and all its ns files"""

        if not self.root_dir or lang_code not in self.lngs :
            return False

        lang_dir = os.path.join( self.root_dir, lang_code )
        try :
            shutil.rmtree( lang_dir )
            self.lngs.remove( lang_code )
            return True
        except shutil.Error :
            return False


    def delete_ns ( self, ns: str ) -> bool :
        """Delete a ns from all lngs"""

        if not self.root_dir or ns not in self.ns :
            return False

        success = True
        for lang in self.lngs :
            file_path = os.path.join( self.root_dir, lang, ns )
            try :
                if os.path.exists( file_path ) :
                    os.remove( file_path )
            except OSError :
                success = False

        if success :
            self.ns.remove( ns )

        return success


    def rename_language ( self, old_code: str, new_code: str ) -> bool :
        """Rename a language folder"""

        if not self.root_dir or old_code not in self.lngs or new_code in self.lngs :
            return False

        old_path = os.path.join( self.root_dir, old_code )
        new_path = os.path.join( self.root_dir, new_code )
        try :
            os.rename( old_path, new_path )
            self.lngs.remove( old_code )
            self.lngs.add( new_code )
            return True
        except OSError :
            return False


    def rename_ns ( self, old_name: str, new_name: str ) -> bool :
        """Rename a ns in all lngs"""

        if not self.root_dir or old_name not in self.ns or new_name in self.ns :
            return False

        if not new_name.endswith( '.json' ) :
            new_name = f"{new_name}.json"

        success = True
        for lang in self.lngs :
            old_path = os.path.join( self.root_dir, lang, old_name )
            new_path = os.path.join( self.root_dir, lang, new_name )
            try :
                if os.path.exists( old_path ) :
                    os.rename( old_path, new_path )
            except OSError :
                success = False

        if success :
            self.ns.remove( old_name )
            self.ns.add( new_name )

        return success


    def get_translations ( self, lang: str, ns: str ) -> Dict :
        """Get translations for a specific language and ns"""

        if not self.root_dir or lang not in self.lngs or ns not in self.ns :
            return {}

        file_path = os.path.join( self.root_dir, lang, ns )
        if not os.path.exists( file_path ) :
            return {}

        try :
            with open( file_path, 'r', encoding= 'utf-8' ) as f :
                return json.load( f )
        except json.JSONDecodeError :
            return {}


    def save_translations ( self, lang: str, ns: str, data: Dict ) -> bool :
        """Save translations for a specific language and ns"""

        if not self.root_dir or lang not in self.lngs or ns not in self.ns :
            return False

        # Sort keys alphabetically
        sorted_data = { k: data[ k ] for k in sorted( data.keys() ) }

        # Save translations
        return self._write_file( lang, ns, sorted_data )


    def add_translation_key ( self, ns: str, key: str, default: str = "" ) -> bool :
        """Add a new translation key to a namespace in all languages"""

        if not self.root_dir or ns not in self.ns :
            return False

        success = True
        for lang in self.lngs :
            data = self.get_translations ( lang, ns )
            if key not in data :
                data[ key ] = default
                if not self.save_translations( lang, ns, data ) :
                    success = False

        return success


    def delete_translation_key ( self, ns: str, key: str ) -> bool :
        """Delete a translation key from a namespace in all languages"""

        if not self.root_dir or ns not in self.ns :
            return False

        success = True
        for lang in self.lngs :
            data = self.get_translations( lang, ns )
            if key in data :
                del data[ key ]
                if not self.save_translations( lang, ns, data ) :
                    success = False

        return success


    def rename_translation_key ( self, ns: str, old_key: str, new_key: str ) -> bool :
        """Rename a translation key in a namespace across all languages"""

        if not self.root_dir or ns not in self.ns :
            return False

        # Check if new key already exists in any language
        for lang in self.lngs :
            data = self.get_translations( lang, ns )
            if new_key in data :
                return False  # Don't overwrite existing keys

        success = True
        for lang in self.lngs :
            data = self.get_translations( lang, ns )
            if old_key in data :
                data[ new_key ] = data[ old_key ]
                del data[ old_key ]
                if not self.save_translations( lang, ns, data ) :
                    success = False

        return success
