"""
TranslateHub - Structure Manager Module
Handles language and namespace structure operations
"""


from typing import Set

import os
import shutil

from .file_operations import FileOperations
from .translation_operations import TranslationOperations


class StructureManager :
    """Manages the structure of languages and namespaces"""

    def __init__ ( self, file_ops: FileOperations, trans_ops: TranslationOperations ) :
        self.file_ops = file_ops
        self.trans_ops = trans_ops
        self.languages: Set[ str ] = set()
        self.namespaces: Set[ str ] = set()


    def load_structure ( self ) :
        """Load the existing structure from the file system"""

        self.languages, self.namespaces = self.file_ops.scan_directory_structure()


    def ensure_schema_directory ( self ) :
        """Ensure schema directory exists and is synchronized"""

        if not self.file_ops.root_dir :
            return

        schema_dir = os.path.join( self.file_ops.root_dir, self.file_ops.schema_dir_name )
        if not os.path.isdir( schema_dir ) :
            os.makedirs( schema_dir, exist_ok= True )

        self.synchronize_schema()


    def synchronize_schema ( self ) :
        """Synchronize schema directory with all namespaces and keys"""

        for ns in self.namespaces :
            self.trans_ops.synchronize_keys_for_namespace(
                ns, { self.file_ops.schema_dir_name }
            )


    def create_language ( self, lang_code: str ) -> bool :
        """Create a new language with all existing namespaces"""

        if (
            not self.file_ops.root_dir
            or lang_code in self.languages
            or lang_code == self.file_ops.schema_dir_name
        ) :
            return False

        # Create language directory
        lang_dir = os.path.join( self.file_ops.root_dir, lang_code )
        os.makedirs( lang_dir, exist_ok= True )

        # Create all namespace files
        for ns in self.namespaces :
            template_data = self._get_template_data( ns )
            empty_data = { k: "" for k in template_data.keys() }
            self.trans_ops.save_translations( lang_code, ns, empty_data )

        self.languages.add( lang_code )
        return True


    def create_namespace ( self, ns: str ) -> bool :
        """Create a new namespace in all languages"""

        if not ns.endswith( ".json" ) :
            ns = f"{ns}.json"

        if not self.file_ops.root_dir or ns in self.namespaces :
            return False

        # Create namespace file in all languages (including schema)
        for lang in self.languages :
            self.trans_ops.save_translations( lang, ns, {} )

        # Also create in schema directory
        self.trans_ops.save_translations( self.file_ops.schema_dir_name, ns, {} )

        self.namespaces.add( ns )
        return True


    def delete_language ( self, lang_code: str ) -> bool :
        """Delete a language and all its files"""

        if (
            not self.file_ops.root_dir
            or lang_code not in self.languages
            or lang_code == self.file_ops.schema_dir_name
        ) :
            return False

        lang_dir = os.path.join( self.file_ops.root_dir, lang_code )

        try :
            shutil.rmtree( lang_dir )
            self.languages.remove( lang_code )
            return True
        except shutil.Error :
            return False


    def delete_namespace ( self, ns: str ) -> bool :
        """Delete a namespace from all languages"""

        if not self.file_ops.root_dir or ns not in self.namespaces :
            return False

        success = True
        for lang in list( self.languages ) + [ self.file_ops.schema_dir_name ] :
            if not self.file_ops.delete_file( lang, ns ) :
                success = False

        if success :
            self.namespaces.remove( ns )

        return success


    def rename_language ( self, old_code: str, new_code: str ) -> bool :
        """Rename a language folder"""

        if (
            not self.file_ops.root_dir
            or old_code not in self.languages
            or new_code in self.languages
            or old_code == self.file_ops.schema_dir_name
            or new_code == self.file_ops.schema_dir_name
        ) :
            return False

        old_path = os.path.join( self.file_ops.root_dir, old_code )
        new_path = os.path.join( self.file_ops.root_dir, new_code )

        try :
            os.rename( old_path, new_path )
            self.languages.remove( old_code )
            self.languages.add( new_code )
            return True
        except OSError :
            return False


    def rename_namespace ( self, old_name: str, new_name: str ) -> bool :
        """Rename a namespace in all languages"""

        if (
            not self.file_ops.root_dir
            or old_name not in self.namespaces
            or new_name in self.namespaces
        ) :
            return False

        if not new_name.endswith( ".json" ) :
            new_name = f"{new_name}.json"

        success = True
        for lang in list( self.languages ) + [ self.file_ops.schema_dir_name ] :
            if not self.file_ops.rename_file( lang, old_name, new_name ) :
                success = False

        if success :
            self.namespaces.remove( old_name )
            self.namespaces.add( new_name )

        return success


    def _get_template_data ( self, ns: str ) -> dict :
        """Get template data for a namespace (from schema or existing language)"""

        # Try schema first
        schema_data = self.trans_ops.get_translations( self.file_ops.schema_dir_name, ns )
        if schema_data :
            return schema_data

        # Try existing languages
        for lang in self.languages :
            if lang == self.file_ops.schema_dir_name :
                continue
            data = self.trans_ops.get_translations( lang, ns )
            if data :
                return data

        return {}
