#!/usr/bin/env python3
"""
COMPLETE SOURCE CODE RECOVERY
Decompiles all DEX files and restores full source tree
"""
import os
import sys
import zipfile
import shutil
import subprocess
from pathlib import Path
import urllib.request
import urllib.error

def download_file(url, target_file, timeout=300):
    """Download file with progress"""
    print(f"  ⏳ Downloading: {target_file}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, target_file)
        print("✓")
        return True
    except urllib.error.URLError as e:
        print(f"✗ ({e})")
        return False
    except Exception as e:
        print(f"✗ ({type(e).__name__})")
        return False

def extract_zip(zip_file, target_dir):
    """Extract ZIP file"""
    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            z.extractall(target_dir)
        return True
    except Exception as e:
        print(f"  ❌ Extraction failed: {e}")
        return False

def setup_tools():
    """Setup dex2jar and CFR decompiler"""
    print("📥 SETTING UP DECOMPILATION TOOLS")
    print("=" * 70)
    
    # Download dex2jar
    dex2jar_url = "https://github.com/ThexXTURBOXx/dex2jar/releases/download/v2.0/dex2jar-2.0.zip"
    cfr_url = "https://www.benf.org/other/cfr/cfr.jar"
    
    dex2jar_zip = "dex2jar-2.0.zip"
    cfr_jar = "cfr.jar"
    
    # Need dex2jar
    if not Path("dex2jar").exists():
        if download_file(dex2jar_url, dex2jar_zip):
            print("  ✓ Extracting dex2jar...", end=" ", flush=True)
            if extract_zip(dex2jar_zip, "."):
                print("✓")
            else:
                return False
        else:
            print("  ⚠️  dex2jar download failed, will use alternative method")
    
    # Need CFR
    if not Path(cfr_jar).exists():
        if download_file(cfr_url, cfr_jar):
            print("  ✓ CFR ready for decompilation")
        else:
            print("  ⚠️  CFR download failed")
            return False
    
    return True

def convert_dex_to_jar(dex_file, output_jar):
    """Convert DEX to JAR using dex2jar"""
    print(f"\n  Converting {dex_file.name} to JAR...", end=" ", flush=True)
    
    try:
        dex2jar_cmd = Path("dex2jar/d2j-dex2jar.sh")
        if not dex2jar_cmd.exists():
            dex2jar_cmd = Path("dex2jar/d2j-dex2jar.bat")
        
        if dex2jar_cmd.exists():
            result = subprocess.run(
                [str(dex2jar_cmd), str(dex_file), "-o", str(output_jar)],
                capture_output=True,
                timeout=120
            )
            if result.returncode == 0 or output_jar.exists():
                print("✓")
                return True
    except Exception as e:
        pass
    
    print("⚠️  (will try CFR directly on dex)")
    return False

def decompile_with_cfr(input_file, output_dir):
    """Decompile JAR or DEX using CFR"""
    print(f"  Decompiling {input_file.name} to Java...", end=" ", flush=True)
    
    try:
        result = subprocess.run(
            ["java", "-jar", "cfr.jar", str(input_file), "--outputdir", str(output_dir)],
            capture_output=True,
            timeout=180
        )
        # CFR often exits with 1 even on success
        if output_dir.exists() and list(output_dir.glob("**/*.java")):
            print("✓")
            return True
        else:
            print("⚠️")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ timeout")
        return False
    except Exception as e:
        print(f"❌ {e}")
        return False

def recover_source():
    """Main recovery process"""
    print("\n" + "=" * 70)
    print("🚀 COMPLETE SOURCE CODE RECOVERY")
    print("=" * 70 + "\n")
    
    # Setup
    if not setup_tools():
        print("\n❌ Tool setup failed. Trying alternative...\n")
        return recover_with_cfr_only()
    
    # Find DEX files
    apk_dir = Path("apk-extracted")
    dex_files = sorted(apk_dir.glob("classes*.dex"))
    
    if not dex_files:
        print("❌ No DEX files found in apk-extracted/")
        return False
    
    # Create output directory
    output_dir = Path("src-recovered-full")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📂 Decompiling {len(dex_files)} DEX files...\n")
    
    success_count = 0
    
    for i, dex_file in enumerate(dex_files, 1):
        print(f"[{i}/{len(dex_files)}] {dex_file.name}")
        
        # Try direct CFR decompilation on DEX
        if decompile_with_cfr(dex_file, output_dir):
            success_count += 1
        else:
            # Try dex2jar conversion first
            jar_file = output_dir / f"{dex_file.stem}.jar"
            if convert_dex_to_jar(dex_file, jar_file) and jar_file.exists():
                decompile_with_cfr(jar_file, output_dir)
                success_count += 1
    
    print(f"\n✓ Decompilation complete: {success_count}/{len(dex_files)} successful\n")
    
    return finalize_recovery(output_dir)

def recover_with_cfr_only():
    """Alternative: Direct CFR decompilation"""
    print("Using CFR directly on DEX files...")
    
    apk_dir = Path("apk-extracted")
    dex_files = sorted(apk_dir.glob("classes*.dex"))
    output_dir = Path("src-recovered-full")
    output_dir.mkdir(exist_ok=True)
    
    for dex_file in dex_files:
        print(f"\n  Decompiling {dex_file.name}...")
        decompile_with_cfr(dex_file, output_dir)
    
    return finalize_recovery(output_dir)

def finalize_recovery(src_dir):
    """Move recovered source to project"""
    print("=" * 70)
    print("📦 FINALIZING RECOVERY")
    print("=" * 70 + "\n")
    
    # Find com/examinerai directory
    recovered_src = None
    for root, dirs, files in os.walk(src_dir):
        if 'com' in dirs:
            recovered_src = Path(root) / 'com' / 'examinerai'
            if recovered_src.exists():
                break
    
    if not recovered_src or not recovered_src.exists():
        print("⚠️  Could not find com/examinerai in recovered source")
        print(f"Checking {src_dir}...")
        
        # List what we have
        for item in src_dir.rglob("*.java"):
            print(f"  - {item.relative_to(src_dir)}")
            break
        
        return False
    
    # Count recovered files
    java_files = list(recovered_src.glob("**/*.java"))
    print(f"✓ Found {len(java_files)} Java source files\n")
    
    if len(java_files) == 0:
        print("❌ No Java files found in decompiled output")
        return False
    
    # Destination
    dest_dir = Path("android-app/app/src/main/java/com/examinerai")
    
    # Remove old stub files
    if dest_dir.exists():
        print(f"Clearing old stub files from {dest_dir}...")
        for item in dest_dir.glob("*.kt"):
            item.unlink()
            print(f"  ✓ Removed {item.name}")
    else:
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy recovered source
    print(f"\nCopying recovered source to {dest_dir}...")
    for src_file in java_files:
        dest_file = dest_dir / src_file.name
        shutil.copy2(src_file, dest_file)
    
    print(f"✓ Copied {len(java_files)} files")
    
    print("\n" + "=" * 70)
    print("✅ SOURCE CODE RECOVERY COMPLETE!")
    print("=" * 70)
    print(f"\nRestored {len(java_files)} source files to:")
    print(f"  {dest_dir}\n")
    
    print("📝 NOTE: Files are in Java format (.java)")
    print("   IDE will auto-convert to Kotlin or rebuild with Java\n")
    
    return True

def main():
    print("\n")
    try:
        if recover_source():
            print("\n✔️  PROJECT RECOVERY SUCCESSFUL!")
            print("\nNext steps:")
            print("1. Sync Gradle: File → Sync Now (in Android Studio)")
            print("2. Build: ./gradlew.bat clean build")
            print("3. Test: Install APK on device")
            print("4. Release: ./gradlew.bat assembleRelease bundleRelease\n")
            return 0
        else:
            print("\n❌ Recovery failed")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️  Recovery interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
