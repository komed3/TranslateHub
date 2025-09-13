"""
TranslateHub - Options Dialog
Dialog for configuring application options
"""

from typing import Dict, Optional, Union

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QFormLayout, QGroupBox, QLabel, QLineEdit, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget
)

from ..helpers import ok_close


class OptionsDialog ( QDialog ) :
    """Dialog for configuring application options"""

    def __init__ (
        self, parent: Optional[ QWidget ] = None,
        settings: Optional[ QSettings ] = None
    ) :
        """
        Initialize options dialog
        Args:
            parent: Parent widget
            settings: Application settings
        """
 
        super().__init__( parent )
        self.settings = settings
        self.setWindowTitle( "Options" )
        self.resize( 500, 400 )

        self.layout: QVBoxLayout = QVBoxLayout()

        # Tab widget
        self.tab_widget = QTabWidget()

        # General tab
        self.general_tab = QWidget()
        self.general_layout = QVBoxLayout()

        # Auto-save group
        self.auto_save_group = QGroupBox( "Auto-save" )
        auto_save_layout = QFormLayout()

        self.auto_save_cb = QCheckBox( "Enable auto-save" )
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange( 5, 600 )
        self.auto_save_interval.setSuffix( " seconds" )

        auto_save_layout.addRow( self.auto_save_cb )
        auto_save_layout.addRow( "Interval:", self.auto_save_interval )

        self.auto_save_group.setLayout( auto_save_layout )
        self.general_layout.addWidget( self.auto_save_group )

        # JSON options group
        self.json_group = QGroupBox( "JSON Options" )
        json_layout = QFormLayout()

        self.compress_json_cb = QCheckBox( "Compress JSON files" )
        json_layout.addRow( self.compress_json_cb )

        self.json_group.setLayout( json_layout )
        self.general_layout.addWidget( self.json_group )

        # Status bar options
        self.status_group = QGroupBox( "Status Bar" )
        status_layout = QFormLayout()

        self.status_timeout = QSpinBox()
        self.status_timeout.setRange( 1, 60 )
        self.status_timeout.setSuffix( " seconds" )

        status_layout.addRow( "Message timeout:", self.status_timeout )

        self.status_group.setLayout( status_layout )
        self.general_layout.addWidget( self.status_group )

        self.general_layout.addStretch()
        self.general_tab.setLayout( self.general_layout )

        # Schema tab
        self.schema_tab = QWidget()
        self.schema_layout = QVBoxLayout()

        self.schema_group = QGroupBox( "Schema Directory" )
        schema_layout = QFormLayout()

        self.schema_dir_name = QLineEdit()
        schema_layout.addRow( "Directory name:", self.schema_dir_name )

        self.schema_group.setLayout( schema_layout )
        self.schema_layout.addWidget( self.schema_group )
        self.schema_layout.addStretch()
        self.schema_tab.setLayout( self.schema_layout )

        # Translation API tab
        self.api_tab = QWidget()
        self.api_layout = QVBoxLayout()

        self.api_group = QGroupBox( "Translation API" )
        api_layout = QFormLayout()

        self.api_enabled_cb = QCheckBox( "Enable translation API" )
        self.api_url = QLineEdit()
        self.api_key = QLineEdit()
        self.api_pattern = QLineEdit()

        api_layout.addRow( self.api_enabled_cb )
        api_layout.addRow( "API URL:", self.api_url )
        api_layout.addRow( "API Key:", self.api_key )
        api_layout.addRow( "API Pattern:", self.api_pattern )

        self.api_group.setLayout( api_layout )
        self.api_layout.addWidget( self.api_group )

        # API help text
        help_label = QLabel( "<br />".join( [
            "API Pattern should include placeholders:",
            "{text} - Text to translate",
            "{source} - Source language",
            "{target} - Target language",
            "",
            "Example: https://api.example.com/translate?q={text}&source={source}&target={target}&key={key}"
        ] ) )
        self.api_layout.addWidget( help_label )

        self.api_layout.addStretch()
        self.api_tab.setLayout( self.api_layout )

        # Add tabs to tab widget
        self.tab_widget.addTab( self.general_tab, "General" )
        self.tab_widget.addTab( self.schema_tab, "Schema" )
        self.tab_widget.addTab( self.api_tab, "Translation API" )

        self.layout.addWidget( self.tab_widget )

        # Dialog buttons
        self.layout.addWidget( ok_close( self._save_settings, self.reject ) )

        self.setLayout( self.layout )

        # Load settings
        self._load_settings()


    def _load_settings ( self ) -> None :
        """Load settings into dialog"""

        if not self.settings :
            return

        # General settings
        self.auto_save_cb.setChecked( self.settings.value( "auto_save", True, bool ) )
        self.auto_save_interval.setValue( self.settings.value( "auto_save_interval", 30, int ) )
        self.compress_json_cb.setChecked( self.settings.value( "compress_json", False, bool ) )
        self.status_timeout.setValue( self.settings.value( "status_timeout", 5, int ) )

        # Schema settings
        self.schema_dir_name.setText( self.settings.value( "schema_dir_name", "_schema", str ) )

        # API settings
        self.api_enabled_cb.setChecked( self.settings.value( "api_enabled", False, bool ) )
        self.api_url.setText( self.settings.value( "api_url", "", str ) )
        self.api_key.setText( self.settings.value( "api_key", "", str ) )
        self.api_pattern.setText( self.settings.value( "api_pattern", "", str ) )


    def _save_settings ( self ) -> None :
        """Save settings from dialog"""

        if not self.settings :
            return

        # General settings
        self.settings.setValue( "auto_save", self.auto_save_cb.isChecked() )
        self.settings.setValue( "auto_save_interval", self.auto_save_interval.value() )
        self.settings.setValue( "compress_json", self.compress_json_cb.isChecked() )
        self.settings.setValue( "status_timeout", self.status_timeout.value() )

        # Schema settings
        self.settings.setValue( "schema_dir_name", self.schema_dir_name.text() )

        # API settings
        self.settings.setValue( "api_enabled", self.api_enabled_cb.isChecked() )
        self.settings.setValue( "api_url", self.api_url.text() )
        self.settings.setValue( "api_key", self.api_key.text() )
        self.settings.setValue( "api_pattern", self.api_pattern.text() )

        self.accept()


    def get_settings_dict ( self ) -> Dict[ str, Union[ str, int ] ] :
        """Get settings as a dictionary"""

        return {
            "auto_save": self.auto_save_cb.isChecked(),
            "auto_save_interval": self.auto_save_interval.value() * 1000,
            "compress_json": self.compress_json_cb.isChecked(),
            "status_timeout": self.status_timeout.value() * 1000,
            "schema_dir_name": self.schema_dir_name.text(),
            "api_enabled": self.api_enabled_cb.isChecked(),
            "api_url": self.api_url.text(),
            "api_key": self.api_key.text(),
            "api_pattern": self.api_pattern.text(),
        }
