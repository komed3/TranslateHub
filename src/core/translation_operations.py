"""
TranslateHub - Translation Operations Module
Handles operations on translation data
"""

from typing import Dict, List, Set, Tuple

from .file_operations import FileOperations


class TranslationOperations :
    """Handles translation data operations"""

    def __init__ ( self, file_ops: FileOperations ) :
        self.file_ops = file_ops


    def operate_on_files (
        self, languages: List[ str ], namespaces: List[ str ],
        operation, include_schema: bool = True, **kwargs
    ) :
        """
        Generic operation that works on both normal and schema files
        Args:
            languages: List of languages to operate on
            namespaces: List of namespaces to operate on
            operation: Function to call for each file
            include_schema: Whether to include schema files
            **kwargs: Additional arguments for the operation
        """
        results = {}

        # Process regular language files
        for lang in languages :
            if lang == self.file_ops.schema_dir_name :
                continue

            lang_results = {}
            for ns in namespaces :
                result = operation( lang, ns, **kwargs )
                if result is not None :
                    lang_results[ ns ] = result

            if lang_results :
                results[ lang ] = lang_results

        # Process schema files if requested
        if include_schema :
            schema_results = {}
            for ns in namespaces :
                result = operation( self.file_ops.schema_dir_name, ns, **kwargs )
                if result is not None :
                    schema_results[ ns ] = result

            if schema_results :
                results[ self.file_ops.schema_dir_name ] = schema_results

        return results


    def get_translations ( self, lang: str, ns: str ) -> Dict :
        """Get translations for a specific language and namespace"""

        file_path = self.file_ops.get_file_path( lang, ns )
        return self.file_ops.read_json_file( file_path )


    def save_translations (
        self, lang: str, ns: str, data: Dict,
        compress: bool = False
    ) -> bool :
        """Save translations for a specific language and namespace"""

        # Sort keys alphabetically
        sorted_data = { k: data[ k ] for k in sorted( data.keys() ) }
        file_path = self.file_ops.get_file_path( lang, ns )

        return self.file_ops.write_json_file( file_path, sorted_data, compress )


    def synchronize_keys_for_namespace ( self, ns: str, languages: Set[ str ] ) -> int :
        """Synchronize keys for a specific namespace across all languages"""

        # Collect all keys from all languages and schema
        all_keys = set()

        # Get keys from schema
        schema_data = self.get_translations( self.file_ops.schema_dir_name, ns )
        all_keys.update( schema_data.keys() )

        # Get keys from all languages
        for lang in languages :
            if lang == self.file_ops.schema_dir_name :
                continue

            data = self.get_translations( lang, ns )
            all_keys.update( data.keys() )

        # Update all files with missing keys
        changes = 0
        for lang in languages :
            data = self.get_translations( lang, ns )
            original_count = len( data )

            # Add missing keys
            for key in all_keys :
                if key not in data :
                    data[ key ] = ""
                    changes += 1

            # Save if changes were made
            if len( data ) != original_count :
                self.save_translations( lang, ns, data )

        return changes


    def update_key_in_all_files (
        self, ns: str, languages: Set[ str ],
        key_operation, **kwargs
    ) -> bool :
        """
        Apply a key operation to all files for a namespace
        Args:
            ns: Namespace to update
            languages: Set of languages to update
            key_operation: Function that modifies the data dict
            **kwargs: Additional arguments for the operation
        """

        success = True

        for lang in languages :
            data = self.get_translations( lang, ns )
            if key_operation( data, **kwargs ) :
                if not self.save_translations( lang, ns, data ) :
                    success = False

        return success


    def search_in_translations (
        self, lang: str, ns: str, query: str,
        case_sensitive: bool = False
    ) -> Dict[ str, str ] :
        """Search for translations in a specific file"""

        data = self.get_translations( lang, ns )
        matches = {}

        for key, value in data.items() :
            if case_sensitive :
                if query in key or query in value :
                    matches[ key ] = value
            else :
                if query.lower() in key.lower() or (
                    value and query.lower() in value.lower()
                ) :
                    matches[ key ] = value

        return matches


    def calculate_progress( self, lang: str, ns: str ) -> Tuple[ int, int ] :
        """Calculate translation progress for a language/namespace"""

        data = self.get_translations( lang, ns )
        total = len( data )
        done = sum( 1 for v in data.values() if v.strip() )

        return done, total
