#!/usr/bin/env python3
"""
Recover source code from compiled APK by analyzing class structure
"""
import zipfile
import os
import sys
from pathlib import Path

def extract_apk_structure():
    apk_path = "android-app/app/build/outputs/apk/standard/debug/app-standard-debug.apk"
    
    if not os.path.exists(apk_path):
        print(f"❌ APK not found at {apk_path}")
        sys.exit(1)
    
    print(f"📦 Analyzing APK: {apk_path}")
    
    with zipfile.ZipFile(apk_path, 'r') as z:
        # List all files in APK
        print("\n📋 Files in APK:")
        for name in sorted(z.namelist()):
            if name.startswith('classes'):
                print(f"  - {name}")
        
        # Try to extract META-INF for build info
        print("\n🔍 Looking for source references in manifest...")
        if 'AndroidManifest.xml' in z.namelist():
            manifest = z.read('AndroidManifest.xml')
            print(f"  - AndroidManifest.xml found ({len(manifest)} bytes)")
        
        # Extract resources
        resources = [f for f in z.namelist() if f.startswith('resources/') or f.startswith('res/')]
        print(f"\n📁 Resources found: {len(resources)} files")
        
        # Check for debug info
        debug_files = [f for f in z.namelist() if 'debug' in f.lower() or 'source' in f.lower()]
        print(f"  - Debug files: {debug_files}")

def analyze_gradle_build():
    """Look for clues in gradle build outputs"""
    build_log = "android-app/app/build/intermediates"
    if os.path.exists(build_log):
        print(f"\n✓ Build intermediates found")
        for root, dirs, files in os.walk(build_log):
            if 'classes' in root:
                print(f"  📂 {root}: {len(files)} files")
                break

if __name__ == "__main__":
    extract_apk_structure()
    analyze_gradle_build()
    print("\n⚠️  The source code was accidentally deleted.")
    print("📱 The compiled APK is available and ready to use.")
    print("🔧 Options to recover:")
    print("   1. Download Java decompiler (CFR) and decompile classes.dex")
    print("   2. Reconstruct source from known app structure")
    print("   3. Use decompilation service or apktool")
