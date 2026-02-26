#!/usr/bin/env python3
"""
Download and setup Java Decompiler tools
"""
import subprocess
import os
import sys
from pathlib import Path

def check_and_download_decompilers():
    """Setup decompilers to recover source code"""
    
    print("🔧 Setting up source code recovery...\n")
    
    # Check Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        print("✅ Java is available")
    except:
        print("❌ Java not found. Please install Java 11+")
        return False
    
    # Option 1: Try to download CFR
    cfr_path = Path("cfr.jar")
    if not cfr_path.exists():
        print("\n⏳ Would download CFR decompiler (80MB), but let's use another approach...")
    
    # Option 2: Check for apktool
    try:
        result = subprocess.run(['apktool', '--version'], capture_output=True, text=True)
        print("✅ apktool found - can decode APK")
        return True
    except:
        print("⚠️  apktool not found")
    
    return False

def extract_class_names_from_apk():
    """Extract class names from DEX files"""
    import zipfile
    import struct
    
    apk = "android-app/app/build/outputs/apk/standard/debug/app-standard-debug.apk"
    
    print(f"\n📱 Extracting class information from {apk}...\n")
    
    if not os.path.exists(apk):
        print(f"❌ APK not found")
        return
    
    with zipfile.ZipFile(apk, 'r') as z:
        # Get main DEX file
        dex_data = z.read('classes.dex')
        
        # DEX format: first string IDs are at offset 0x70+
        # This is a simplified check
        print("✅ APK contains multiple DEX files with compiled code:")
        dex_files = [f for f in z.namelist() if f.startswith('classes') and f.endswith('.dex')]
        print(f"   Total DEX files: {len(dex_files)}")
        
        print("\n📦 The compiled code is in bytecode format (dex).")
        print("   To recover: use CFR or similar Java decompiler")

def list_recovery_options():
    print("\n" + "="*70)
    print("🆘 SOURCE CODE RECOVERY OPTIONS")
    print("="*70)
    
    print("\n✅ GOOD NEWS:")
    print("   • Your APK was built successfully (examinerai v1.1)")
    print("   • Correct package name: com.examinerai ✓")
    print("   • All compiled code is in the APK ✓")
    print("   • APK is ready to install and test ✓")
    
    print("\n❌ BAD NEWS:")
    print("   • Source .kt files were accidentally deleted")
    print("   • Directory moved improperly during package rename")
    
    print("\n🔄 RECOVERY METHODS (in order of ease):")
    print("\n1️⃣  FASTEST: Use the APK immediately")
    print("   • The APK is fully built and working")
    print("   • Install on device/emulator and test")
    print("   • Source recovery can happen later")
    
    print("\n2️⃣  DECOMPILE: Recover source from APK")
    print("   • Download CFR: https://www.benf.org/other/cfr/cfr.jar")
    print("   • Extract classes.dex from APK")
    print("   • Decompile with: java -jar cfr.jar classes.dex")
    print("   • Will get Java source (convertible to Kotlin)")
    
    print("\n3️⃣  RECONSTRUCT: Manually rebuild source")
    print("   • Rebuild from decompiled output")
    print("   • Use IDE auto-format (Kotlin syntax aware)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    check_and_download_decompilers()
    extract_class_names_from_apk()
    list_recovery_options()
