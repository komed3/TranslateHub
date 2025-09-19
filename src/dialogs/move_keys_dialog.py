"""
TransalteHub - Move Keys Dialog
Dialog to move translation keys between namespaces
"""

from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QComboBox, QDialog, QGroupBox, QHBoxLayout, QListWidget, QListWidgetItem,
    QRadioButton, QVBoxLayout, QWidget
)

from ..helpers import ok_close, ui_label

class MoveKeysDialog ( QDialog ) :
    """Dialog to move translation keys between namespaces"""

    def __init__ (
        self, parent: Optional[ QWidget ], keys: List[ str ], namespaces: List[ str ],
        current_ns: str, preselect_keys: Optional[ List[ str ] ] = None
    ) :
        """
        Initialize move keys dialog
        Args:
            parent: Parent widget
            keys: List of keys available to move
            namespaces: List of available namespaces
            current_ns: Current namespace of the keys
            preselect_keys: Keys to preselect in the list
        """

        super().__init__( parent )
        self.setWindowTitle( "Move Translation Keys" )
        self.resize( 500, 400 )
        self.selected_keys = []
        self.target_ns = None
        self.conflict_strategy = "skip"

        layout = QVBoxLayout()

        # Key selection
        key_group = QGroupBox( "Select keys to move" )
        key_layout = QVBoxLayout()
        self.key_list = QListWidget()
        self.key_list.setSelectionMode( QListWidget.SelectionMode.MultiSelection )

        for k in keys :
            item = QListWidgetItem( k )
            self.key_list.addItem( item )
            if preselect_keys and k in preselect_keys :
                item.setSelected( True )

        key_layout.addWidget( self.key_list )
        key_group.setLayout( key_layout )

        layout.addWidget( key_group )

        # Target namespace
        ns_group = QGroupBox( "Target Namespace" )
        ns_layout = QHBoxLayout()
        self.ns_combo = QComboBox()

        for ns in namespaces :
            if ns != current_ns :
                self.ns_combo.addItem( ns )

        ns_layout.addWidget( ui_label( "Move to:" ) )
        ns_layout.addWidget( self.ns_combo )
        ns_group.setLayout( ns_layout )

        layout.addWidget( ns_group )

        # Conflict strategy
        conflict_group = QGroupBox( "On duplicate key" )
        conflict_layout = QHBoxLayout()
        self.rb_skip = QRadioButton( "Skip" )
        self.rb_replace = QRadioButton( "Replace" )
        self.rb_keep = QRadioButton( "Keep both (prefix with source ns)" )
        self.rb_skip.setChecked( True )
        conflict_layout.addWidget( self.rb_skip )
        conflict_layout.addWidget( self.rb_replace )
        conflict_layout.addWidget( self.rb_keep )
        conflict_group.setLayout( conflict_layout )

        layout.addWidget( conflict_group )

        # Buttons
        layout.addWidget( ok_close( self.accept, self.reject ) )

        self.setLayout( layout )


    def get_result ( self ) -> Tuple[ List[ str ], str, str ] :
        """Get selected keys, target namespace and conflict strategy"""

        keys = [ item.text() for item in self.key_list.selectedItems() ]
        ns = self.ns_combo.currentText()

        if self.rb_replace.isChecked() :
            strategy = "replace"
        elif self.rb_keep.isChecked() :
            strategy = "keep_both"
        else :
            strategy = "skip"

        return keys, ns, strategy
