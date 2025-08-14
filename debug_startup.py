#!/usr/bin/env python
"""
Debug startup script for Windows executable crash diagnosis
"""

import sys
import os
import traceback
import time
from pathlib import Path

def write_log(msg):
    """Write to debug log file"""
    log_file = Path("baal_debug.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

def main():
    try:
        write_log("=" * 50)
        write_log("Starting Baal Pet Debug")
        write_log(f"Python: {sys.version}")
        write_log(f"Platform: {sys.platform}")
        write_log(f"Executable: {sys.executable}")
        write_log(f"Working Dir: {os.getcwd()}")
        write_log(f"Script Dir: {os.path.dirname(os.path.abspath(__file__))}")
        write_log(f"sys.path: {sys.path}")
        
        # Check for frozen executable
        if getattr(sys, 'frozen', False):
            write_log(f"Running as frozen executable")
            write_log(f"Bundle dir: {sys._MEIPASS}")
        
        # Try importing critical modules one by one
        write_log("Testing imports...")
        
        try:
            import PyQt6
            write_log(f"✓ PyQt6 imported: {PyQt6.__file__}")
        except Exception as e:
            write_log(f"✗ PyQt6 import failed: {e}")
            
        try:
            from PyQt6 import QtCore
            write_log(f"✓ QtCore imported")
        except Exception as e:
            write_log(f"✗ QtCore import failed: {e}")
            
        try:
            from PyQt6 import QtGui
            write_log(f"✓ QtGui imported")
        except Exception as e:
            write_log(f"✗ QtGui import failed: {e}")
            
        try:
            from PyQt6 import QtWidgets
            write_log(f"✓ QtWidgets imported")
        except Exception as e:
            write_log(f"✗ QtWidgets import failed: {e}")
            
        try:
            from PyQt6.QtWidgets import QApplication
            write_log(f"✓ QApplication imported")
        except Exception as e:
            write_log(f"✗ QApplication import failed: {e}")
            
        # Try creating QApplication
        try:
            write_log("Creating QApplication...")
            app = QApplication(sys.argv)
            write_log(f"✓ QApplication created successfully")
            
            # Check platform plugin
            write_log(f"Platform: {app.platformName()}")
            
            app.quit()
        except Exception as e:
            write_log(f"✗ QApplication creation failed: {e}")
            write_log(traceback.format_exc())
            
        # Try importing baal modules
        try:
            write_log("Importing baal modules...")
            from baal.desktop_pet.core.logger_config import init_logging
            write_log(f"✓ logger_config imported")
        except Exception as e:
            write_log(f"✗ logger_config import failed: {e}")
            
        try:
            from baal.desktop_pet import main
            write_log(f"✓ main module imported")
        except Exception as e:
            write_log(f"✗ main module import failed: {e}")
            write_log(traceback.format_exc())
            
        # If all imports succeed, try running the app
        write_log("All basic imports successful, attempting to run main...")
        from run_desktop_pet import main as run_main
        run_main()
        
    except Exception as e:
        write_log(f"Fatal error: {e}")
        write_log(traceback.format_exc())
        
        # Keep console open
        print(f"Error logged to baal_debug.log")
        print(f"Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()