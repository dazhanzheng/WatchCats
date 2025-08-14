#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug launcher to capture crash information
"""

import sys
import os
import traceback
import logging
from datetime import datetime

# Set up logging to file
log_file = f"crash_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("Starting Baal Pet Assistant (Debug Mode)")
    logger.info("=" * 60)
    
    # Log environment info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Executable: {sys.executable}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    try:
        # Try to import and run the main application
        logger.info("\nImporting run_desktop_pet...")
        import run_desktop_pet
        
        logger.info("Starting main application...")
        run_desktop_pet.main()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error(f"Module not found: {e.name if hasattr(e, 'name') else 'unknown'}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
    except Exception as e:
        logger.error(f"Application crashed with error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
    finally:
        logger.info(f"\nLog saved to: {log_file}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()