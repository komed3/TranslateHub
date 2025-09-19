"""
TranslateHub - Translation Manager Module
Main class that coordinates all translation operations
"""

from typing import Dict, List, Optional, Set, Tuple

import os
import zipfile

from .file_operations import FileOperations
from .structure_manager import StructureManager
from .translation_operations import TranslationOperations


class TranslationManager :
    """Main translation manager that coordinates all operations"""

    def __init__ (
        self, root_dir: Optional[ str ] = None,
        schema_dir_name: str = "_schema"
    ) :
        self.file_ops = FileOperations( root_dir, schema_dir_name )
        self.trans_ops = TranslationOperations( self.file_ops )
        self.structure_manager = StructureManager( self.file_ops, self.trans_ops )
        self.modified_translations: Set[ Tuple[ str, str, str ] ] = set()

        self._load_structure()


    def set_root_dir ( self, root_dir: str ) -> bool :
        """Set the root directory and reload the structure"""

        if not os.path.isdir( root_dir ) :
            return False

        self.file_ops.root_dir = root_dir
        self._load_structure()
        self.structure_manager.ensure_schema_directory()

        return True


    def set_schema_dir_name ( self, schema_dir_name: str ) -> bool :
        """Set the schema directory name"""

        old_name = self.file_ops.schema_dir_name
        self.file_ops.schema_dir_name = schema_dir_name

        if self.file_ops.root_dir and os.path.isdir(
            os.path.join( self.file_ops.root_dir, old_name )
        ) :
            try :
                os.rename(
                    os.path.join( self.file_ops.root_dir, old_name ),
                    os.path.join( self.file_ops.root_dir, schema_dir_name ),
                )
                return True
            except OSError :
                self.file_ops.schema_dir_name = old_name

        return False


    def _load_structure ( self ) :
        """Load the structure from the file system"""

        self.structure_manager.load_structure()


    def get_languages ( self ) -> List[ str ] :
        """Get all available languages (excluding schema)"""

        return sorted( [
            lang for lang in self.structure_manager.languages
            if lang != self.file_ops.schema_dir_name
        ] )


    def get_namespaces ( self ) -> List[ str ] :
        """Get all available namespaces"""

        return sorted( list( self.structure_manager.namespaces ) )


    def create_language ( self, lang_code: str ) -> bool :
        """Create a new language"""

        return self.structure_manager.create_language( lang_code )


    def create_namespace ( self, ns: str ) -> bool :
        """Create a new namespace"""

        return self.structure_manager.create_namespace( ns )


    def delete_language ( self, lang_code: str ) -> bool :
        """Delete a language"""

        return self.structure_manager.delete_language( lang_code )


    def delete_namespace ( self, ns: str ) -> bool :
        """Delete a namespace"""

        return self.structure_manager.delete_namespace( ns )


    def rename_language ( self, old_code: str, new_code: str ) -> bool :
        """Rename a language"""

        return self.structure_manager.rename_language( old_code, new_code )


    def rename_namespace ( self, old_name: str, new_name: str ) -> bool :
        """Rename a namespace"""

        return self.structure_manager.rename_namespace( old_name, new_name )


    def get_translations ( self, lang: str, ns: str ) -> Dict :
        """Get translations for a specific language and namespace"""

        if (
            not self.file_ops.root_dir
            or (
                lang not in self.structure_manager.languages
                and lang != self.file_ops.schema_dir_name
            )
            or ns not in self.structure_manager.namespaces
        ) :
            return {}

        return self.trans_ops.get_translations( lang, ns )


    def save_translations (
        self, lang: str, ns: str, data: Dict,
        compress: bool = False
    ) -> bool :
        """Save translations for a specific language and namespace"""

        if (
            not self.file_ops.root_dir
            or (
                lang not in self.structure_manager.languages
                and lang != self.file_ops.schema_dir_name
            )
            or ns not in self.structure_manager.namespaces
        ) :
            return False

        result = self.trans_ops.save_translations( lang, ns, data, compress )

        # Update schema if needed
        if lang != self.file_ops.schema_dir_name and result :
            self.trans_ops.synchronize_keys_for_namespace(
                ns, { self.file_ops.schema_dir_name }
            )

        return result


    def add_translation_key ( self, ns: str, key: str, default: str = "" ) -> bool :
        """Add a new translation key to all languages"""

        if not self.file_ops.root_dir or ns not in self.structure_manager.namespaces :
            return False

        def add_key_operation ( data: dict, key: str, default: str ) -> bool :
            if key not in data :
                data[ key ] = default
                return True
            return False

        return self.trans_ops.update_key_in_all_files (
            ns, self.structure_manager.languages, add_key_operation,
            key= key, default= default
        )


    def delete_translation_key ( self, ns: str, key: str ) -> bool :
        """Delete a translation key from all languages"""

        if not self.file_ops.root_dir or ns not in self.structure_manager.namespaces :
            return False

        def delete_key_operation ( data: dict, key: str ) -> bool :
            if key in data :
                del data[ key ]
                return True
            return False

        return self.trans_ops.update_key_in_all_files(
            ns, self.structure_manager.languages, delete_key_operation, key= key
        )


    def rename_translation_key ( self, ns: str, old_key: str, new_key: str ) -> bool :
        """Rename a translation key in all languages"""

        if not self.file_ops.root_dir or ns not in self.structure_manager.namespaces :
            return False

        # Check if new key already exists
        for lang in self.structure_manager.languages :
            if lang == self.file_ops.schema_dir_name :
                continue
            data = self.trans_ops.get_translations( lang, ns )
            if new_key in data :
                return False

        def rename_key_operation( data: dict, old_key: str, new_key: str ) -> bool :
            if old_key in data :
                data[ new_key ] = data[ old_key ]
                del data[ old_key ]
                return True
            return False

        return self.trans_ops.update_key_in_all_files(
            ns, self.structure_manager.languages, rename_key_operation,
            old_key= old_key, new_key= new_key
        )


    def move_translation_keys (
        self, ns_from: str, ns_to: str, keys: List[ str ], conflict_strategy: str = "skip"
    ) -> bool :
        """
        Move translation keys from one namespace to another for all languages and schema.
        Args:
            ns_from: Source namespace
            ns_to: Target namespace
            keys: List of keys to move
            conflict_strategy: "skip", "replace", or "keep_both"
        """
        if (
            not self.file_ops.root_dir
            or ns_from not in self.structure_manager.namespaces
            or ns_to not in self.structure_manager.namespaces
            or ns_from == ns_to
            or not keys
        ) :
            return False

        changed = False
        all_langs = list( self.structure_manager.languages ) + [ self.file_ops.schema_dir_name ]

        for lang in all_langs :
            data_from = self.trans_ops.get_translations( lang, ns_from )
            data_to = self.trans_ops.get_translations( lang, ns_to )
            updated = False

            for key in keys :
                if key not in data_from :
                    continue

                value = data_from[ key ]
                target_key = key
                exists = key in data_to

                if exists :
                    if conflict_strategy == "skip" :
                        continue

                    if conflict_strategy == "replace" :
                        pass  # overwrite
                    elif conflict_strategy == "keep_both" :
                        target_key = f"{ns_from.replace( '.json', '' )}_{key}"
                        if target_key in data_to :
                            # avoid double prefix
                            continue

                data_to[ target_key ] = value
                del data_from[ key ]
                updated = True
                changed = True

            if updated :
                self.trans_ops.save_translations( lang, ns_from, data_from )
                self.trans_ops.save_translations( lang, ns_to, data_to )

        # sync after moving
        self.trans_ops.synchronize_keys_for_namespace( ns_from, set( all_langs ) )
        self.trans_ops.synchronize_keys_for_namespace( ns_to, set( all_langs ) )
        self.structure_manager.synchronize_schema()

        return changed


    def synchronize_keys ( self ) -> Dict[ str, int ] :
        """Synchronize translation keys across all languages and namespaces"""

        if not self.file_ops.root_dir :
            return {}

        changes = {}
        for ns in self.structure_manager.namespaces :
            ns_changes = self.trans_ops.synchronize_keys_for_namespace(
                ns, self.structure_manager.languages
            )
            if ns_changes > 0 :
                changes[ ns ] = ns_changes

        return changes


    def get_language_progress ( self, lang: str ) -> Tuple[ int, int ] :
        """Get overall translation progress for a language"""

        if (
            not self.file_ops.root_dir
            or lang not in self.structure_manager.languages
            or lang == self.file_ops.schema_dir_name
        ) :
            return ( 0, 0 )

        total_keys = 0
        done_keys = 0

        for ns in self.structure_manager.namespaces :
            done, total = self.trans_ops.calculate_progress( lang, ns )
            done_keys += done
            total_keys += total

        return ( done_keys, total_keys )


    def get_namespace_progress ( self, ns: str ) -> Dict[ str, Tuple[ int, int ] ] :
        """Get translation progress for a namespace across all languages"""

        if not self.file_ops.root_dir or ns not in self.structure_manager.namespaces :
            return {}

        progress = {}
        for lang in self.structure_manager.languages :
            if lang == self.file_ops.schema_dir_name :
                continue

            done, total = self.trans_ops.calculate_progress( lang, ns )
            progress[ lang ] = ( done, total )

        return progress


    def get_all_progress ( self ) -> Dict[ str, Dict[ str, Tuple[ int, int ] ] ] :
        """Get detailed progress statistics for all languages and namespaces"""

        if not self.file_ops.root_dir :
            return {}

        progress = {}
        for lang in self.structure_manager.languages :
            if lang == self.file_ops.schema_dir_name :
                continue

            lang_progress = {}
            for ns in self.structure_manager.namespaces :
                done, total = self.trans_ops.calculate_progress( lang, ns )
                lang_progress[ ns ] = ( done, total )
            progress[ lang ] = lang_progress

        return progress


    def search (
        self, query: str, case_sensitive: bool = False
    ) -> Dict[ str, Dict[ str, Dict[ str, str ] ] ] :
        """Search for translations containing the query string"""

        if not self.file_ops.root_dir or not query :
            return {}

        def search_operation ( lang: str, ns: str, query: str, case_sensitive: bool ) :
            matches = self.trans_ops.search_in_translations(
                lang, ns, query, case_sensitive
            )
            return matches if matches else None

        languages = [
            lang for lang in self.structure_manager.languages
            if lang != self.file_ops.schema_dir_name
        ]
        namespaces = list( self.structure_manager.namespaces )

        return self.trans_ops.operate_on_files(
            languages, namespaces, search_operation, include_schema= False,
            query= query, case_sensitive= case_sensitive,
        )


    def export_translations (
        self, languages: List[ str ], namespaces: List[ str ],
        include_schema: bool = False, output_path: Optional[ str ] = None,
    ) -> Optional[ str ] :
        """Export selected languages and namespaces to a zip file"""

        if not self.file_ops.root_dir :
            return None

        if not output_path :
            output_path = os.path.join( self.file_ops.root_dir, "export.zip" )

        with zipfile.ZipFile( output_path, "w", zipfile.ZIP_DEFLATED ) as zipf :
            # Export selected languages
            for lang in languages :
                if (
                    lang not in self.structure_manager.languages
                    or lang == self.file_ops.schema_dir_name
                ) :
                    continue

                for ns in namespaces :
                    if ns not in self.structure_manager.namespaces :
                        continue

                    if self.file_ops.file_exists( lang, ns ) :
                        file_path = self.file_ops.get_file_path( lang, ns )
                        zipf.write( file_path, os.path.join( lang, ns ) )

            # Export schema if requested
            if include_schema :
                for ns in namespaces :
                    if self.file_ops.file_exists( self.file_ops.schema_dir_name, ns ) :
                        file_path = self.file_ops.get_file_path(
                            self.file_ops.schema_dir_name, ns
                        )
                        zipf.write(
                            file_path, os.path.join( self.file_ops.schema_dir_name, ns )
                        )

        return output_path


    def mark_as_modified ( self, lang: str, ns: str, key: str ) -> None :
        """Mark a translation as modified"""

        self.modified_translations.add( ( lang, ns, key ) )


    def is_modified ( self, lang: str, ns: str, key: str ) -> bool :
        """Check if a translation is modified"""

        return ( lang, ns, key ) in self.modified_translations


    def clear_modified ( self ) -> None :
        """Clear the modified translations set"""

        self.modified_translations.clear()
