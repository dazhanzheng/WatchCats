#!/usr/bin/env python
"""
Fix path encoding issues for Windows build
"""

import os
import shutil
from pathlib import Path

def fix_resource_paths():
    """Copy resources to ASCII-only paths for Windows compatibility"""
    
    # Map of problematic paths to safe paths
    path_mappings = {
        '动作表情拆分': 'emotion_assets'
    }
    
    for src, dst in path_mappings.items():
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            print(f"Copying {src} to {dst}...")
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
            print(f"✓ Copied successfully")
        else:
            print(f"✗ Source path {src} not found")
    
    # Update spec file to use new paths
    spec_file = Path('baal_windows.spec')
    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        for src, dst in path_mappings.items():
            content = content.replace(f"'{src}", f"'{dst}")
            content = content.replace(f'"{src}', f'"{dst}')
        spec_file.write_text(content, encoding='utf-8')
        print("✓ Updated spec file with safe paths")
    
    return True

if __name__ == "__main__":
    fix_resource_paths()