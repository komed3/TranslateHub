#!/usr/bin/env python3

"""
TranslateHub - Cross-platform Translation Management Tool
Main launcher script
"""


import os
import sys
from src.main import main


# Add src directory to path
src_dir = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), "src" )
sys.path.append( src_dir )

# Run main application
if __name__ == "__main__" :
    main()
