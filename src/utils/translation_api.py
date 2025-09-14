"""
TranslateHub - Translation API Utility
Handles communication with translation APIs
"""

from typing import Dict, Optional, Tuple

import json
import requests
from requests.utils import requote_uri


class TranslationAPI :
    """Handles communication with translation APIs"""

    def __init__ (
        self, enabled: bool = False, api_url: str = "", api_key: str = "",
        api_pattern: str = "",
    ) :
        """
        Initialize translation API
        Args:
            enabled: Whether the API is enabled
            api_url: Base API URL
            api_key: API key
            api_pattern: API pattern with placeholders
        """

        self.enabled = enabled
        self.api_url = api_url
        self.api_key = api_key
        self.api_pattern = api_pattern


    def is_configured ( self ) -> bool :
        """Check if the API is properly configured"""

        return self.enabled and bool( self.api_url ) and bool( self.api_pattern )


    def translate (
        self, text: str, source_lang: str, target_lang: str
    ) -> Tuple[ bool, str, Optional[ str ] ] :
        """
        Translate text using the configured API
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        Returns:
            Tuple[ bool, str, Optional[ str ] ]:
                Success flag, translated text or original text, and error message if any
        """

        if not self.is_configured() :
            return False, text, "Translation API not configured"

        # Clean up language codes (remove region if present)
        source_lang_clean = source_lang.split( "-" )[ 0 ]
        target_lang_clean = target_lang.split( "-" )[ 0 ]

        try :
            # Replace placeholders in pattern
            url = self.api_pattern.replace( "{text}", requote_uri( text ) )
            url = url.replace( "{source}", source_lang_clean )
            url = url.replace( "{target}", target_lang_clean )
            url = url.replace( "{key}", self.api_key )

            # Make request
            headers = { "Content-Type": "application/json", "Accept": "application/json" }

            if self.api_key and "{key}" not in self.api_pattern :
                headers[ "Authorization" ] = f"Bearer {self.api_key}"

            response = requests.get( url, headers= headers, timeout= 10 )
            response.raise_for_status()

            # Parse response - this is generic and might need adjustment for specific APIs
            data: Dict = response.json()

            # Try to find translated text in response
            # This is a generic approach that works with many translation APIs
            # but might need to be adjusted for specific APIs
            translated_text = None

            # Google Translate API format
            if "data" in data and "translations" in data[ "data" ] :
                translated_text = data[ "data" ][ "translations" ][ 0 ][ "translatedText" ]
            # Microsoft Translator API format
            elif isinstance( data, list ) and len( data ) > 0 and "translations" in data[ 0 ] :
                translated_text = data[ 0 ][ "translations" ][ 0 ][ "text" ]
            # DeepL API format
            elif "translations" in data :
                translated_text = data[ "translations" ][ 0 ][ "text" ]
            # LibreTranslate API format
            elif "translatedText" in data :
                translated_text = data[ "translatedText" ]
            # Generic fallback - look for common keys
            else :
                for key in [ "translated", "translation", "text", "result", "output" ] :
                    if key in data :
                        translated_text = data[ key ]
                        break

            if translated_text :
                return True, translated_text, None

            return False, text, "Could not find translated text in API response"

        except requests.RequestException as e :
            return False, text, f"API request failed: {str( e )}"
        except json.JSONDecodeError :
            return False, text, "Invalid JSON response from API"
        except Exception as e :  # pylint: disable=broad-exception-caught
            return False, text, f"Translation failed: {str( e )}"


    def update_config(
        self, enabled: bool, api_url: str, api_key: str,
        api_pattern: str
    ) -> None :
        """
        Update API configuration
        Args:
            enabled: Whether the API is enabled
            api_url: Base API URL
            api_key: API key
            api_pattern: API pattern with placeholders
        """

        self.enabled = enabled
        self.api_url = api_url
        self.api_key = api_key
        self.api_pattern = api_pattern
