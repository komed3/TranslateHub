"""
TranslateHub - Main Entry Point
Cross-platform translation management tool for i18n projects
"""

import os
import sys

from src import launch, __version__

# Add src directory to path
sys.path.append( os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), "src" ) )

# Run main application
if __name__ == "__main__" :
    launch()
