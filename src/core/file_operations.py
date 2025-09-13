"""
TranslateHub - File Operations Module
Handles low-level file operations for translation files
"""

from typing import Dict, Optional, Set, Tuple

import json
import os


class FileOperations :
    """Handles file operations for translation files"""

    def __init__ (
        self, root_dir: Optional[ str ] = None,
        schema_dir_name: str = "_schema"
    ) :
        self.root_dir = root_dir
        self.schema_dir_name = schema_dir_name


    def read_json_file ( self, file_path: str ) -> Dict :
        """Read JSON data from file"""

        if not os.path.exists( file_path ) :
            return {}

        try :
            with open( file_path, "r", encoding= "utf-8" ) as f :
                return json.load( f )
        except json.JSONDecodeError :
            return {}


    def write_json_file (
        self, file_path: str, data: Dict,
        compress: bool = False
    ) -> bool :
        """Write JSON data to file"""

        try :
            os.makedirs( os.path.dirname( file_path ), exist_ok= True )
            with open( file_path, "w", encoding= "utf-8" ) as f :
                json.dump(data, f, ensure_ascii= False, indent= None if compress else 2 )
                if not compress :
                    f.write( "\n\n" )
            return True
        except OSError :
            return False


    def get_file_path ( self, lang: str, ns: str ) -> str :
        """Get file path for language and namespace"""

        return os.path.join( self.root_dir or "", lang, ns )


    def file_exists ( self, lang: str, ns: str ) -> bool :
        """Check if file exists"""

        return os.path.exists( self.get_file_path( lang, ns ) )


    def delete_file ( self, lang: str, ns: str ) -> bool :
        """Delete a file"""

        file_path = self.get_file_path( lang, ns )

        try :
            if os.path.exists( file_path ) :
                os.remove( file_path )
            return True
        except OSError :
            return False


    def rename_file ( self, lang: str, old_ns: str, new_ns: str ) -> bool :
        """Rename a file"""

        old_path = self.get_file_path( lang, old_ns )
        new_path = self.get_file_path( lang, new_ns )

        try :
            if os.path.exists( old_path ) :
                os.rename( old_path, new_path )
            return True
        except OSError :
            return False


    def scan_directory_structure ( self ) -> Tuple[ Set[ str ], Set[ str ] ] :
        """Scan directory structure and return languages and namespaces"""

        if not self.root_dir or not os.path.isdir( self.root_dir ) :
            return set(), set()

        # Get all language directories
        languages = {
            d for d in os.listdir( self.root_dir )
            if os.path.isdir( os.path.join( self.root_dir, d ) )
        }

        # Get all unique namespaces across all languages
        namespaces = set()
        for lang in languages :
            if lang == self.schema_dir_name :
                continue

            lang_dir = os.path.join( self.root_dir, lang )
            for file in os.listdir( lang_dir ) :
                if file.endswith( ".json" ) :
                    namespaces.add( file )

        return languages, namespaces
