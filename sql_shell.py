"""
DineDesk SQLite Interactive Launcher
"""
import os
import sys

backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

from sql_shell import main

if __name__ == "__main__":
    main()
