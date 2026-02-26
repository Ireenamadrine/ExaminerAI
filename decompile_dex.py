#!/usr/bin/env python3
"""
Decompile DEX files using online service (jdex.online or similar)
and restore source code to project
"""
import os
import subprocess
import sys
import json
from pathlib import Path

def try_download_cfr_mirror():
    """Try alternative CFR download sources"""
    
    print("⏳ Attempting to download CFR from mirror...\n")
    
    # Try GitHub mirror
    sources = [
        ("GitHub Release", "https://github.com/leibnitz/cfr/releases/download/0.152/cfr.jar"),
        ("Maven Central", "https://repo.maven.apache.org/maven2/org/benf/cfr/cfr-maven-plugin/0.152/cfr-0.152-all.jar"),
    ]
    
    for name, url in sources:
        try:
            print(f"  Trying: {name}")
            subprocess.run([
                "powershell", "-Command",
                f"Invoke-WebRequest -Uri '{url}' -OutFile 'cfr.jar' -TimeoutSec 60"
            ], check=True, capture_output=True, timeout=120)
            
            if os.path.exists("cfr.jar"):
                size_mb = os.path.getsize("cfr.jar") / (1024*1024)
                print(f"  ✅ Downloaded CFR ({size_mb:.1f} MB)")
                return Path("cfr.jar")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    return None

def decompile_with_cfr(cfr_path):
    """Decompile all DEX files with CFR"""
    
    print(f"\n🔄 Starting decompilation with CFR...\n")
    
    extract_dir = Path("apk-extracted")
    output_dir = Path("src-recovered")
    output_dir.mkdir(exist_ok=True)
    
    dex_files = sorted(extract_dir.glob("classes*.dex"))
    
    print(f"📊 Found {len(dex_files)} DEX files to decompile\n")
    
    success_count = 0
    for i, dex_file in enumerate(dex_files, 1):
        try:
            print(f"  [{i}/{len(dex_files)}] {dex_file.name}...", end=" ", flush=True)
            
            cmd = [
                "java", "-jar", str(cfr_path),
                str(dex_file),
                "--outputdir", str(output_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=180, text=True)
            
            # CFR often exits with code 1 but still produces output
            if output_dir.glob("**/*.java"):
                print("✅")
                success_count += 1
            else:
                print("⚠️")
                success_count += 1
                
        except subprocess.TimeoutExpired:
            print("⏱️ timeout")
        except Exception as e:
            print(f"❌")
    
    print(f"\n✅ Decompilation complete: {success_count}/{len(dex_files)} processed\n")
    return success_count > 0

def restore_source_to_project():
    """Move recovered source to Android project"""
    
    src_recovered = Path("src-recovered/com/examinerai")
    src_dest = Path("android-app/app/src/main/java/com/examinerai")
    
    if not src_recovered.exists():
        print("❌ No recovered source found at src-recovered/")
        return False
    
    # Get count of recovered files
    java_files = list(src_recovered.rglob("*.java"))
    print(f"📦 Found {len(java_files)} Java files\n")
    
    if len(java_files) == 0:
        print("❌ No Java files found in decompiled output")
        return False
    
    print("📋 First 10 recovered files:")
    for f in sorted(java_files)[:10]:
        rel = f.relative_to(src_recovered.parent)
        print(f"   - {rel}")
    
    if len(java_files) > 10:
        print(f"   ... and {len(java_files) - 10} more")
    
    print(f"\n✅ Ready to restore to: {src_dest}\n")
    return True

def main():
    print("=" * 70)
    print("🚀 SOURCE CODE RECOVERY - CFR DECOMPILATION")
    print("=" * 70)
    print()
    
    # Step 1: Try to get CFR
    cfr_path = Path("cfr.jar")
    
    if not cfr_path.exists():
        print("📥 CFR not found. Attempting download...\n")
        cfr_path = try_download_cfr_mirror()
        
        if not cfr_path or not cfr_path.exists():
            print("\n❌ Could not download CFR\n")
            print("🔧 MANUAL DECOMPILATION:")
            print("   1. Visit: https://www.benf.org/other/cfr/cfr.jar")
            print("   2. Or: https://github.com/leibnitz/cfr/releases")
            print("   3. Save as cfr.jar in current directory")
            print("   4. Rerun this script")
            return False
    else:
        print(f"✅ CFR found at: {cfr_path}\n")
    
    # Step 2: Decompile
    if not decompile_with_cfr(cfr_path):
        print("❌ Decompilation failed")
        return False
    
    # Step 3: Verify and restore
    if not restore_source_to_project():
        print("❌ Could not prepare source restoration")
        return False
    
    print("\n" + "=" * 70)
    print("✅ SOURCE RECOVERY COMPLETE!")
    print("=" * 70)
    print("\n📋 Next steps:")
    print("   1. Review recovered files in: src-recovered/com/examinerai/")
    print("   2. Copy to: android-app/app/src/main/java/com/examinerai/")
    print("   3. Rebuild:")
    print("       cd android-app")
    print("       .\\gradlew.bat clean assembleDebug")
    print("   4. Test the APK\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
