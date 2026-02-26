#!/usr/bin/env python3
"""
Use online APK decompiler APIs to recover source code
"""
import os
import requests
import json
from pathlib import Path
import time

def decompile_with_uptodown():
    """Use UpToDown online decompiler API"""
    dex_file = Path("apk-extracted/classes.dex")
    
    if not dex_file.exists():
        print("❌ classes.dex not found")
        return False
    
    print("⏳ Uploading to online decompiler...")
    print("   (This may take a few minutes)")
    
    try:
        # Try using a free online decompiler
        url = "https://www.javadecompilers.com/upload"
        
        with open(dex_file, 'rb') as f:
            files = {'dex': f}
            response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            print("✅ Upload successful")
            print("📥 Downloading decompiled source...")
            # Save the result
            with open('recovered_source.zip', 'wb') as f:
                f.write(response.content)
            print("✅ Source downloaded to recovered_source.zip")
            return True
        else:
            print(f"⚠️  Upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def fallback_instructions():
    """Provide manual recovery instructions"""
    print("\n" + "=" * 70)
    print("🆘 MANUAL RECOVERY INSTRUCTIONS")
    print("=" * 70)
    print()
    print("Method 1: Use Online Decompiler (EASIEST)")
    print("  1. Go to: https://www.javadecompilers.com/")
    print("  2. Upload: apk-extracted/classes.dex")
    print("  3. Wait for decompilation")
    print("  4. Download Java source files")
    print("  5. Extract and move to android-app/app/src/main/java/com/examinerai/")
    print()
    print("Method 2: Use APKLab VSCode Extension")
    print("  1. Open VSCode")
    print("  2. Extensions → Install APKLab")
    print("  3. Right-click apk-extracted/classes.dex")
    print("  4. Select 'Decompile DEX'")
    print("  5. Auto-extracts Java source")
    print()
    print("Method    3: Download Working JADX")
    print("  1. Get: https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip")
    print("  2. Extract ZIP properly")
    print("  3. Run: jadx.exe -d src-recovered-full apk-extracted/classes.dex")
    print()
    print("=" * 70)
    print()
    print("⏱️  Estimated time: 30-60 minutes per DEX file")
    print()

if __name__ == "__main__":
    print("🚀 ONLINE DECOMPILATION")
    print("=" * 70)
    print()
    
    # Try online decompiler
    if decompile_with_uptodown():
        print("\n✅ Online decompilation successful!")
    else:
        print("\n⚠️  Online decompilation unavailable")
        fallback_instructions()
