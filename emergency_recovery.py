#!/usr/bin/env python3
"""
Emergency Source Code Recovery from DEX Files
Extracts compiled classes and provides decompilation instructions
"""
import os
import zipfile
import struct
from pathlib import Path
import subprocess
import sys

def analyze_dex_file(dex_path):
    """Analyze DEX file structure to extract class names"""
    try:
        with open(dex_path, 'rb') as f:
            # DEX magic bytes
            magic = f.read(8)
            if magic[:4] != b'dex\n':
                return []
            
            # Read file size and string IDs
            f.seek(0x20)  # String IDs start offset
            string_ids_off = struct.unpack('<I', f.read(4))[0]
            string_ids_size = struct.unpack('<I', f.read(4))[0]
            
            # Type IDs offset and size
            type_ids_off = struct.unpack('<I', f.read(4))[0]
            type_ids_size = struct.unpack('<I', f.read(4))[0]
            
            print(f"  Strings: {string_ids_size}, Types: {type_ids_size}")
            return True
    except Exception as e:
        print(f"  Error analyzing: {e}")
        return False

def setup_recovery():
    """Setup tools for source recovery"""
    print("🆘 EMERGENCY SOURCE CODE RECOVERY")
    print("=" * 70)
    print()
    
    # Check for DEX files
    dex_dir = Path("apk-extracted")
    if dex_dir.exists():
        dex_files = list(dex_dir.glob("classes*.dex"))
        print(f"✓ Found {len(dex_files)} DEX files:")
        for dex in sorted(dex_files)[:3]:
            print(f"  - {dex.name}", end=" ")
            analyze_dex_file(dex)
        if len(dex_files) > 3:
            print(f"  ... and {len(dex_files)-3} more")
    
    print()
    print("🔧 RECOVERY OPTIONS (Choose One):")
    print()
    print("Option 1: JADX (Best - GUI + CLI)")
    print("  Download: https://github.com/skylot/jadx/releases")
    print("  Install, then:")
    print("    jadx apk-extracted/classes.dex")
    print("    (Repeat for all DEX files)")
    print()
    print("Option 2: APKLab (VSCode Extension - EASIEST)")
    print("  1. Open VSCode")
    print("  2. Install: APKLab extension")
    print("  3. Right-click apk-extracted/classes.dex")
    print("  4. Decompile automatically")
    print()
    print("Option 3: Online Decompilers")
    print("  1. Go to: https://www.javadecompilers.com/")
    print("  2. Upload: apk-extracted/classes.dex")
    print("  3. Download Java source")
    print()
    print("Option 4: Command Line (Procyon)")
    print("  procyon -o src-recovered apk-extracted/classes.dex")
    print()
    print("=" * 70)
    print()
    print("⚠️  IMMEDIATE ACTION REQUIRED:")
    print("    Your source files were replaced with minimal stubs")
    print("    Use one of the above options to restore properly")
    print()

if __name__ == "__main__":
    setup_recovery()
