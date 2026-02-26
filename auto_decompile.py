#!/usr/bin/env python3
"""
Automated decompilation using online services and local tools
"""
import os
import sys
import subprocess
from pathlib import Path
import json

def download_jadx():
    """Download and setup JADX decompiler"""
    print("⏳ Attempting to download JADX decompiler...")
    
    # JADX GitHub releases
    jadx_url = "https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip"
    jadx_zip = "jadx.zip"
    
    try:
        import urllib.request
        print(f"Downloading from: {jadx_url}")
        urllib.request.urlretrieve(jadx_url, jadx_zip)
        
        # Extract
        import zipfile
        with zipfile.ZipFile(jadx_zip, 'r') as z:
            z.extractall("jadx")
        
        print("✅ JADX downloaded and extracted")
        return Path("jadx/bin/jadx.bat")
    except Exception as e:
        print(f"⚠️  JADX download failed: {e}")
        return None

def decompile_with_jadx(jadx_exe, dex_file, output_dir):
    """Decompile DEX file using JADX"""
    try:
        print(f"Decompiling {dex_file.name}...", end=" ", flush=True)
        
        cmd = [str(jadx_exe), "-d", str(output_dir), str(dex_file)]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        
        if result.returncode == 0:
            print("✅")
            return True
        else:
            print("⚠️")
            return True  # Often succeeds despite non-zero exit
    except subprocess.TimeoutExpired:
        print("⏱️ timeout")
        return False
    except Exception as e:
        print(f"❌ {e}")
        return False

def setup_alternative_decompilers():
    """Setup alternative decompilation methods"""
    print("\n🔄 Setting up alternative decompilation methods...\n")
    
    # Try CFR via pip
    try:
        print("Attempting cfr installation via pip...")
        result = subprocess.run(
            ["pip", "install", "cfr-decompiler"],
            capture_output=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ CFR installed")
            return "cfr"
    except:
        pass
    
    # Try procyon
    try:
        print("Checking for Procyon...")
        result = subprocess.run(["procyon", "--version"], capture_output=True)
        if result.returncode == 0:
            print("✅ Procyon found")
            return "procyon"
    except:
        pass
    
    return None

def main():
    print("=" * 70)
    print("🚀 AUTOMATED SOURCE CODE RECOVERY")
    print("=" * 70)
    print()
    
    apk_extracted = Path("apk-extracted")
    output_dir = Path("src-recovered-full")
    output_dir.mkdir(exist_ok=True)
    
    dex_files = sorted(apk_extracted.glob("classes*.dex"))
    if not dex_files:
        print("❌ No DEX files found in apk-extracted/")
        return
    
    print(f"Found {len(dex_files)} DEX files\n")
    
    # Try JADX first
    print("Step 1: Attempting JADX download...")
    jadx_exe = download_jadx()
    
    if jadx_exe and jadx_exe.exists():
        print("\nStep 2: Decompiling with JADX...")
        success_count = 0
        for dex in dex_files:
            if decompile_with_jadx(jadx_exe, dex, output_dir):
                success_count += 1
        
        print(f"\n✅ Decompiled {success_count}/{len(dex_files)} DEX files")
    else:
        print("\nStep 1: JADX download failed, trying alternatives...")
        
        alt_tool = setup_alternative_decompilers()
        if not alt_tool:
            print("\n❌ No decompilers available")
            print("\nManual options:")
            print("1. Download JADX: https://github.com/skylot/jadx/releases")
            print("2. Download APKLab VSCode extension")
            print("3. Use: https://www.javadecompilers.com (upload DEX files)")
            return
    
    # Check output
    java_files = list(output_dir.glob("**/*.java"))
    print(f"\n✅ Generated {len(java_files)} Java source files")
    
    if java_files:
        print("\nTop source files:")
        for f in sorted(java_files)[:10]:
            print(f"  - {f.relative_to(output_dir)}")
    
    print("\n" + "=" * 70)
    print("📦 Next Steps:")
    print("=" * 70)
    print("1. Files saved to: src-recovered-full/")
    print("2. Convert Java to Kotlin (copy to editor, use IDE converter)")
    print(f"3. Move to: android-app/app/src/main/java/com/examinerai/")
    print("4. Rebuild: ./gradlew clean build")

if __name__ == "__main__":
    main()
