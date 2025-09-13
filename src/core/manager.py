"""
TranslateHub - Translation Manager Module
Handles all operations related to translation files
"""


from typing import Dict, List, Tuple, Optional

import json
import os
import shutil
import zipfile


class TranslationManager :
    """Manages translation files and operations"""

    def __init__ (
        self, root_dir: Optional[ str ] = None,
        schema_dir_name: str = "_schema"
    ) :
        """
        Initialize the translation manager with a root directory
        Args:
            root_dir: Root directory for translations
            schema_dir_name: Name of the schema directory
        """

        self.root_dir = root_dir
        self.schema_dir_name = schema_dir_name
        self.languages = set()
        self.namespaces = set()
        self.modified_translations = set()

        self._load_structure()


    def set_root_dir ( self, root_dir: str ) -> bool :
        """
        Set the root directory and reload the structure
        Args:
            root_dir: New root directory path
        Returns:
            bool: True if successful, False otherwise
        """

        if not os.path.isdir( root_dir ) :
            return False

        self.root_dir = root_dir

        self._load_structure()
        self._ensure_schema_directory()
        return True


    def set_schema_dir_name ( self, schema_dir_name: str ) -> bool :
        """
        Set the schema directory name
        Args:
            schema_dir_name: New schema directory name
        """

        old_name = self.schema_dir_name
        self.schema_dir_name = schema_dir_name

        # Rename the schema directory if it exists
        if self.root_dir and os.path.isdir(
            os.path.join( self.root_dir, old_name )
        ) :

            try :
                os.rename(
                    os.path.join( self.root_dir, old_name ),
                    os.path.join( self.root_dir, schema_dir_name )
                )
                return True
            except OSError :
                # If rename fails, revert to old name
                self.schema_dir_name = old_name

        return False


    def _ensure_schema_directory ( self ) -> None :
        """Ensure the schema directory exists and is synchronized"""

        if not self.root_dir :
            return

        schema_dir = os.path.join( self.root_dir, self.schema_dir_name )

        # Create schema directory if it doesn't exist
        if not os.path.isdir( schema_dir ) :
            os.makedirs( schema_dir, exist_ok= True )

        # Synchronize schema with existing namespaces
        self._synchronize_schema()


    def _synchronize_schema ( self ) -> None :
        """Synchronize schema directory with all namespaces and keys"""

        if not self.root_dir :
            return

        # Collect all keys from all languages for each namespace
        for ns in self.namespaces :
            all_keys = set()

            # Get keys from all languages
            for lang in self.languages :
                if lang == self.schema_dir_name :
                    continue

                data = self.get_translations( lang, ns )
                all_keys.update( data.keys() )

            # Create or update schema file with empty values
            if all_keys :
                schema_data = { key: "" for key in sorted( all_keys ) }
                self._write_file( self.schema_dir_name, ns, schema_data )


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
            if lang == self.schema_dir_name :
                continue

            lang_dir = os.path.join( self.root_dir, lang )
            for file in os.listdir( lang_dir ) :
                if file.endswith( ".json" ) :
                    self.namespaces.add( file )


    def _write_file (
        self, lang: str, ns: str, data: Optional[ Dict ] = None,
        compress: bool = False
    ) -> bool :
        """
        Write data to a specific language and namespace file
        Args:
            lang: Language code
            ns: Namespace name
            data: Data to write
            compress: Whether to compress the JSON output
        Returns:
            bool: True if successful, False otherwise
        """

        path = os.path.join( self.root_dir or "", lang, ns )

        try :
            with open( path, "w", encoding= "utf-8" ) as f :
                indent = None if compress else 2
                json.dump( data or {}, f, ensure_ascii= False, indent= indent )
                if not compress :
                    f.write( "\n\n" )
            return True
        except OSError :
            return False


    def get_languages ( self ) -> List[ str ] :
        """
        Get all available languages
        Returns:
            List[ str ]: Sorted list of language codes
        """

        # Filter out schema directory
        filtered_languages = [
            lang for lang in self.languages
            if lang != self.schema_dir_name
        ]

        return sorted( filtered_languages )


    def get_namespaces ( self ) -> List[ str ] :
        """
        Get all available namespaces
        Returns:
            List[ str ]: Sorted list of namespaces
        """

        return sorted( list( self.namespaces ) )


    def create_language ( self, lang_code: str ) -> bool :
        """
        Create a new language with all existing namespaces
        Args:
            lang_code: Language code to create
        Returns:
            bool: True if successful, False otherwise
        """

        if not self.root_dir or lang_code in self.languages or lang_code == self.schema_dir_name :
            return False

        # Create language directory
        lang_dir = os.path.join( self.root_dir, lang_code )
        os.makedirs( lang_dir, exist_ok= True )

        # Create all namespace files with empty translations
        for ns in self.namespaces :

            # Use schema as template if available
            schema_file = os.path.join( self.root_dir, self.schema_dir_name, ns )
            if os.path.exists( schema_file ) :

                try :
                    with open( schema_file, "r", encoding= "utf-8" ) as f :
                        # Create empty translations with the same keys
                        empty_data = { k: "" for k in json.load( f ).keys() }
                        self._write_file( lang_code, ns, empty_data )
                except json.JSONDecodeError :
                    self._write_file( lang_code, ns )

            # If no schema exists, use another language as template
            elif self.languages :

                # Use the first language as a template
                template_langs = [
                    l for l in self.languages
                    if l != self.schema_dir_name
                ]

                if template_langs :
                    template_lang = template_langs[ 0 ]
                    template_file = os.path.join( self.root_dir, template_lang, ns )
                    if os.path.exists( template_file ) :

                        with open( template_file, "r", encoding= "utf-8") as f :
                            try :
                                empty_data = { k: "" for k in json.load( f ).keys() }
                                self._write_file( lang_code, ns, empty_data )
                            except json.JSONDecodeError :
                                self._write_file( lang_code, ns )

                    else :
                        self._write_file( lang_code, ns, {} )
                else :
                    self._write_file( lang_code, ns, {} )

            # If no languages exist yet, create empty file
            else :
                self._write_file( lang_code, ns, {} )

        self.languages.add( lang_code )
        return True


    def create_namespace ( self, ns: str ) -> bool :
        """
        Create a new namespace in all languages
        Args:
            ns: Namespace name to create
        Returns:
            bool: True if successful, False otherwise
        """

        if not ns.endswith( ".json" ) :
            ns = f"{ns}.json"

        if not self.root_dir or ns in self.namespaces :
            return False

        # Create namespace file in all languages
        for lang in self.languages :
            self._write_file( lang, ns, {} )

        # Also create in schema directory
        self._write_file( self.schema_dir_name, ns, {} )

        self.namespaces.add( ns )
        return True


    def delete_language ( self, lang_code: str ) -> bool :
        """
        Delete a language and all its namespace files
        Args:
            lang_code: Language code to delete
        Returns:
            bool: True if successful, False otherwise
        """

        if (
            not self.root_dir or lang_code not in self.languages
            or lang_code == self.schema_dir_name
        ) :
            return False

        lang_dir = os.path.join( self.root_dir, lang_code )

        try :
            shutil.rmtree( lang_dir )
            self.languages.remove( lang_code )
            return True
        except shutil.Error :
            return False


    def delete_namespace( self, ns: str ) -> bool :
        """
        Delete a namespace from all languages
        Args:
            ns: Namespace to delete
        Returns:
            bool: True if successful, False otherwise
        """

        if not self.root_dir or ns not in self.namespaces :
            return False

        success = True
        for lang in self.languages :
            file_path = os.path.join( self.root_dir, lang, ns )
            try :
                if os.path.exists( file_path ) :
                    os.remove( file_path )
            except OSError :
                success = False

        # Also delete from schema directory
        schema_file_path = os.path.join( self.root_dir, self.schema_dir_name, ns )
        try :
            if os.path.exists( schema_file_path ) :
                os.remove( schema_file_path )
        except OSError :
            success = False

        if success :
            self.namespaces.remove( ns )

        return success


    def rename_language ( self, old_code: str, new_code: str ) -> bool :
        """
        Rename a language folder
        Args:
            old_code: Current language code
            new_code: New language code
        Returns:
            bool: True if successful, False otherwise
        """

        if (
            not self.root_dir or 
            old_code not in self.languages or 
            new_code in self.languages or
            old_code == self.schema_dir_name or
            new_code == self.schema_dir_name
        ) :
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
        """
        Rename a namespace in all languages
        Args:
            old_name: Current namespace name
            new_name: New namespace name
        Returns:
            bool: True if successful, False otherwise
        """

        if (
            not self.root_dir or old_name not in self.namespaces
            or new_name in self.namespaces
        ) :
            return False

        if not new_name.endswith( ".json" ) :
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

        # Also rename in schema directory
        schema_old_path = os.path.join( self.root_dir, self.schema_dir_name, old_name )
        schema_new_path = os.path.join( self.root_dir, self.schema_dir_name, new_name )

        try :
            if os.path.exists( schema_old_path ) :
                os.rename( schema_old_path, schema_new_path )
        except OSError :
            success = False

        if success :
            self.namespaces.remove( old_name )
            self.namespaces.add( new_name )

        return success


    def get_translations ( self, lang: str, ns: str ) -> Dict :
        """
        Get translations for a specific language and namespace
        Args:
            lang: Language code
            ns: Namespace name
        Returns:
            Dict: Dictionary of translations
        """

        if not self.root_dir or (
            lang not in self.languages and lang != self.schema_dir_name
        ) or ns not in self.namespaces :
            return {}

        file_path = os.path.join( self.root_dir, lang, ns )

        if not os.path.exists( file_path ) :
            return {}

        try :
            with open( file_path, "r", encoding= "utf-8" ) as f :
                return json.load( f )
        except json.JSONDecodeError :
            return {}


    def save_translations (
        self, lang: str, ns: str, data: Dict,
        compress: bool = False
    ) -> bool :
        """
        Save translations for a specific language and namespace
        Args:
            lang: Language code
            ns: Namespace name
            data: Translation data to save
            compress: Whether to compress the JSON output
        Returns:
            bool: True if successful, False otherwise
        """

        if not self.root_dir or (
            lang not in self.languages and lang != self.schema_dir_name
        ) or ns not in self.namespaces :
            return False

        # Sort keys alphabetically
        sorted_data = { k: data[ k ] for k in sorted( data.keys() ) }

        # Save translations
        result = self._write_file( lang, ns, sorted_data, compress )

        # Update schema if needed
        if lang != self.schema_dir_name and result :
            self._update_schema_for_namespace( ns )

        return result


    def _update_schema_for_namespace( self, ns: str ) -> None :
        """
        Update schema for a specific namespace
        Args:
            ns: Namespace to update
        """

        if not self.root_dir :
            return

        # Collect all keys from all languages for this namespace
        all_keys = set()
        for lang in self.languages :
            if lang == self.schema_dir_name :
                continue

            data = self.get_translations( lang, ns )
            all_keys.update( data.keys() )

        # Update schema file
        if all_keys :
            schema_data = self.get_translations( self.schema_dir_name, ns )
            updated = False

            # Add any missing keys
            for key in all_keys :
                if key not in schema_data :
                    schema_data[ key ] = ""
                    updated = True

            # Save if updated
            if updated :
                self._write_file( self.schema_dir_name, ns, schema_data )


    def add_translation_key( self, ns: str, key: str, default: str = "" ) -> bool :
        """
        Add a new translation key to a namespace in all languages
        Args:
            ns: Namespace name
            key: Translation key
            default: Default value
        Returns:
            bool: True if successful, False otherwise
        """

        if not self.root_dir or ns not in self.namespaces :
            return False

        success = True
        for lang in self.languages :
            if lang == self.schema_dir_name :
                continue

            data = self.get_translations( lang, ns )
            if key not in data :
                data[ key ] = default
                if not self.save_translations( lang, ns, data ) :
                    success = False

        # Add to schema as well
        schema_data = self.get_translations( self.schema_dir_name, ns )
        if key not in schema_data :
            schema_data[ key ] = ""
            self._write_file( self.schema_dir_name, ns, schema_data )

        return success


    def delete_translation_key ( self, ns: str, key: str ) -> bool :
        """
        Delete a translation key from a namespace in all languages
        Args:
            ns: Namespace name
            key: Translation key to delete
        Returns:
            bool: True if successful, False otherwise
        """

        if not self.root_dir or ns not in self.namespaces :
            return False

        success = True
        for lang in self.languages :
            data = self.get_translations( lang, ns )
            if key in data :
                del data[ key ]
                if not self.save_translations( lang, ns, data ) :
                    success = False

        return success


    def rename_translation_key ( self, ns: str, old_key: str, new_key: str ) -> bool :
        """
        Rename a translation key in a namespace across all languages
        Args:
            ns: Namespace name
            old_key: Current key name
            new_key: New key name
        Returns:
            bool: True if successful, False otherwise
        """

        if not self.root_dir or ns not in self.namespaces :
            return False

        # Check if new key already exists in any language
        for lang in self.languages :
            if lang == self.schema_dir_name :
                continue

            data = self.get_translations( lang, ns )
            if new_key in data :
                return False  # Don't overwrite existing keys

        success = True
        for lang in self.languages :
            data = self.get_translations( lang, ns )
            if old_key in data :
                data[ new_key ] = data[ old_key ]
                del data[ old_key ]
                if not self.save_translations( lang, ns, data ) :
                    success = False

        # Update schema as well
        schema_data = self.get_translations( self.schema_dir_name, ns )
        if old_key in schema_data :
            schema_data[ new_key ] = schema_data[ old_key ]
            del schema_data[ old_key ]
            self._write_file( self.schema_dir_name, ns, schema_data )

        return success


    def synchronize_keys ( self ) -> Dict[ str, int ] :
        """
        Synchronize translation keys across all languages and namespaces
        Returns:
            Dict[ str, int ]: Dictionary with namespaces as keys and number of changes as values
        """

        if not self.root_dir :
            return {}

        # For each namespace, collect all keys from all languages
        changes = {}
        for ns in self.namespaces :
            all_keys = set()

            # First check schema directory for keys
            schema_data = self.get_translations( self.schema_dir_name, ns )
            all_keys.update( schema_data.keys() )

            # Then check all languages
            for lang in self.languages :
                if lang == self.schema_dir_name :
                    continue

                data = self.get_translations( lang, ns )
                all_keys.update( data.keys() )

            # Ensure all languages have all keys
            ns_changes = 0
            for lang in self.languages :
                if lang == self.schema_dir_name :
                    continue

                data = self.get_translations( lang, ns )
                orig_count = len( data )

                # Add missing keys
                for key in all_keys :
                    if key not in data :
                        data[ key ] = ""
                        ns_changes += 1

                # Save if changes were made
                if len( data ) != orig_count :
                    self.save_translations( lang, ns, data )

            # Update schema with all keys
            schema_data = self.get_translations( self.schema_dir_name, ns )
            schema_updated = False

            for key in all_keys :
                if key not in schema_data :
                    schema_data[ key ] = ""
                    schema_updated = True

            if schema_updated :
                self._write_file( self.schema_dir_name, ns, schema_data )

            if ns_changes > 0 :
                changes[ ns ] = ns_changes

        return changes


    def mark_as_modified ( self, lang: str, ns: str, key: str ) -> None :
        """
        Mark a translation as modified
        Args:
            lang: Language code
            ns: Namespace name
            key: Translation key
        """

        self.modified_translations.add( ( lang, ns, key ) )


    def is_modified ( self, lang: str, ns: str, key: str ) -> bool :
        """
        Check if a translation is modified
        Args:
            lang: Language code
            ns: Namespace name
            key: Translation key
        Returns:
            bool: True if modified, False otherwise
        """

        return ( lang, ns, key ) in self.modified_translations


    def clear_modified( self ) -> None :
        """Clear the modified translations set"""

        self.modified_translations.clear()


    def get_language_progress( self, lang: str ) -> Tuple[ int, int ] :
        """
        Get overall translation progress for a language
        Args:
            lang: Language code
        Returns:
            Tuple[ int, int ]: Tuple of (translated_count, total_count)
        """

        if not self.root_dir or lang not in self.languages or lang == self.schema_dir_name :
            return ( 0, 0 )

        total_keys = 0
        done_keys = 0

        for ns in self.namespaces :
            data = self.get_translations( lang, ns )
            total_keys += len( data )
            done_keys += sum( 1 for v in data.values() if v.strip() )

        return ( done_keys, total_keys )


    def get_namespace_progress ( self, ns: str ) -> Dict[ str, Tuple[ int, int ] ] :
        """
        Get translation progress for a namespace across all languages
        Args:
            ns: Namespace name
        Returns:
            Dict[ str, Tuple[ int, int ] ]:
                Dictionary with languages as keys and progress tuples as values
        """

        if not self.root_dir or ns not in self.namespaces :
            return {}

        progress = {}
        for lang in self.languages :
            if lang == self.schema_dir_name :
                continue

            data = self.get_translations( lang, ns )
            total = len( data )
            done = sum( 1 for v in data.values() if v.strip() )
            progress[ lang ] = ( done, total )

        return progress


    def get_all_progress ( self ) -> Dict[ str, Dict[ str, Tuple[ int, int ] ] ] :
        """
        Get detailed progress statistics for all languages and namespaces
        Returns:
            Dict[ str, Dict[ str, Tuple[ int, int ] ] ]:
                Nested dictionary with languages and namespaces as keys
                and tuples of (translated_count, total_count) as values
        """

        if not self.root_dir :
            return {}

        progress = {}
        for lang in self.languages :
            if lang == self.schema_dir_name :
                continue

            lang_progress = {}
            for ns in self.namespaces :
                data = self.get_translations( lang, ns )
                total = len( data )
                done = sum( 1 for v in data.values() if v.strip() )
                lang_progress[ ns ] = ( done, total )
            progress[ lang ] = lang_progress

        return progress


    def search( self, q: str, cs: bool = False ) -> Dict[ str, Dict[ str, Dict[ str, str ] ] ] :
        """
        Search for translations containing the query string
        Args:
            q: Search query
            cs: Case sensitive search
        Returns:
            Dict[ str, Dict[ str, Dict[ str, str ] ] ]:
                Nested dictionary with languages, namespaces, and keys as keys
                and the matching translation values
        """

        if not self.root_dir or not q :
            return {}

        results = {}
        for lang in self.languages :
            if lang == self.schema_dir_name :
                continue

            lang_results = {}
            for ns in self.namespaces :
                data = self.get_translations( lang, ns )
                matches = {}

                for key, value in data.items() :
                    if cs :
                        if q in key or q in value :
                            matches[ key ] = value
                    else :
                        if q.lower() in key.lower() or ( value and q.lower() in value.lower() ) :
                            matches[ key ] = value

                if matches :
                    lang_results[ ns ] = matches

            if lang_results :
                results[ lang ] = lang_results

        return results


    def export_translations (
        self, languages: List[ str ], namespaces: List[ str ],
        include_schema: bool = False, output_path: Optional[ str ] = None
    ) -> Optional[ str ] :
        """
        Export selected languages and namespaces to a zip file
        Args:
            languages: List of language codes to export
            namespaces: List of namespaces to export
            include_schema: Whether to include schema directory
            output_path: Path to save the zip file (if None, a temporary file is created)
        Returns:
            str: Path to the created zip file
        """

        if not self.root_dir :
            return None

        if not output_path :
            output_path = os.path.join( self.root_dir, "export.zip" )

        with zipfile.ZipFile( output_path, "w", zipfile.ZIP_DEFLATED ) as zipf :
            # Export selected languages
            for lang in languages :
                if lang not in self.languages or lang == self.schema_dir_name :
                    continue

                for ns in namespaces :
                    if ns not in self.namespaces :
                        continue

                    file_path = os.path.join( self.root_dir, lang, ns )
                    if os.path.exists( file_path ) :
                        zipf.write( file_path, os.path.join( lang, ns ) )

            # Export schema if requested
            if include_schema :
                schema_dir = os.path.join( self.root_dir, self.schema_dir_name )
                if os.path.isdir( schema_dir ) :
                    for ns in namespaces :
                        schema_file = os.path.join( schema_dir, ns )
                        if os.path.exists( schema_file ) :
                            zipf.write( schema_file, os.path.join( self.schema_dir_name, ns ) )

        return output_path
