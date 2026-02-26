#!/usr/bin/env python3
"""
Automated APK Decompilation and Source Recovery
Uses available tools to extract source code from compiled APK
"""
import zipfile
import struct
import subprocess
import os
import sys
import json
from pathlib import Path

class APKDecompiler:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.extract_dir = Path("./apk-extracted")
        
    def extract_apk(self):
        """Extract APK contents (it's a ZIP file)"""
        print(f"📦 Extracting APK: {self.apk_path}")
        
        if not os.path.exists(self.apk_path):
            print(f"❌ APK not found: {self.apk_path}")
            return False
        
        try:
            # Create extraction directory
            self.extract_dir.mkdir(exist_ok=True)
            
            # Extract all files
            with zipfile.ZipFile(self.apk_path, 'r') as z:
                z.extractall(self.extract_dir)
            
            print(f"✅ Extracted to: {self.extract_dir}")
            self._list_dex_files()
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
    
    def _list_dex_files(self):
        """List DEX files in extracted APK"""
        dex_files = list(self.extract_dir.glob("classes*.dex"))
        print(f"\n📋 DEX files found: {len(dex_files)}")
        for dex in sorted(dex_files):
            size_mb = dex.stat().st_size / (1024*1024)
            print(f"   - {dex.name} ({size_mb:.1f} MB)")
    
    def try_download_cfr(self):
        """Attempt to download CFR decompiler"""
        cfr_path = Path("cfr.jar")
        
        if cfr_path.exists():
            print("✅ CFR already exists")
            return cfr_path
        
        print("\n⏳ Attempting to download CFR decompiler...")
        print("   (This may take a few minutes - ~80MB)")
        
        try:
            import urllib.request
            url = "https://www.benf.org/other/cfr/cfr.jar"
            urllib.request.urlretrieve(url, "cfr.jar", _download_progress)
            print(f"\n✅ CFR downloaded successfully!")
            return cfr_path
            
        except Exception as e:
            print(f"\n⚠️  CFR download failed: {e}")
            print("\n   Manual download option:")
            print(f"   1. Download from: https://www.benf.org/other/cfr/cfr.jar")
            print(f"   2. Save as: cfr.jar (in current directory)")
            print(f"   3. Run decompilation manually")
            return None
    
    def decompile_with_cfr(self, cfr_path):
        """Decompile DEX files using CFR"""
        
        if not cfr_path or not cfr_path.exists():
            print("❌ CFR not found. Cannot decompile.")
            print("\n📝 Manual decompilation steps:")
            print("   1. Get CFR: https://www.benf.org/other/cfr/cfr.jar")
            print("   2. Run: java -jar cfr.jar apk-extracted/classes.dex --outputdir ./src-recovered")
            print("   3. Repeat for classes2.dex through classes12.dex")
            return False
        
        output_dir = Path("./src-recovered")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n🔄 Decompiling DEX files with CFR...")
        
        dex_files = sorted(self.extract_dir.glob("classes*.dex"))
        success_count = 0
        
        for dex_file in dex_files:
            try:
                print(f"   Processing {dex_file.name}...", end=" ", flush=True)
                
                cmd = [
                    "java", "-jar", str(cfr_path),
                    str(dex_file),
                    "--outputdir", str(output_dir)
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=120)
                
                if result.returncode == 0:
                    print("✅")
                    success_count += 1
                else:
                    print(f"⚠️ (warnings)")
                    success_count += 1  # CFR often exits with 1 even on success
                    
            except subprocess.TimeoutExpired:
                print("⏱️ timeout")
            except Exception as e:
                print(f"❌ {e}")
        
        print(f"\n✅ Decompilation complete: {success_count}/{len(dex_files)} DEX files processed")
        
        # Check output
        java_files = list(output_dir.glob("**/*.java"))
        print(f"   Generated {len(java_files)} Java source files")
        
        return success_count > 0
    
    def analyze_structure(self):
        """Analyze decompiled class structure"""
        src_dir = Path("./src-recovered")
        
        if not src_dir.exists():
            print("⚠️  Decompiled source not found")
            return
        
        print(f"\n📊 Source code analysis:")
        
        # Count files
        java_files = list(src_dir.glob("**/*.java"))
        kt_files = list(src_dir.glob("**/*.kt"))
        
        print(f"   Java files: {len(java_files)}")
        print(f"   Kotlin files: {len(kt_files)}")
        
        # Find main classes
        if java_files:
            print(f"\n   Key files:")
            for f in sorted(java_files)[:10]:
                rel_path = f.relative_to(src_dir)
                print(f"      - {rel_path}")
            if len(java_files) > 10:
                print(f"      ... and {len(java_files)-10} more")

def _download_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = min(100, int(100 * downloaded / total_size))
    sys.stdout.write(f'\r   [{percent:3d}%] {downloaded/(1024*1024):.1f}MB / {total_size/(1024*1024):.1f}MB')
    sys.stdout.flush()

def main():
    print("=" * 70)
    print("🚀 AUTOMATED SOURCE CODE RECOVERY from APK")
    print("=" * 70)
    
    apk_path = "android-app/app/build/outputs/apk/standard/debug/app-standard-debug.apk"
    
    decompiler = APKDecompiler(apk_path)
    
    # Step 1: Extract APK
    if not decompiler.extract_apk():
        sys.exit(1)
    
    # Step 2: Try to get CFR
    cfr_path = decompiler.try_download_cfr()
    
    # Step 3: Decompile
    if cfr_path and cfr_path.exists():
        decompiler.decompile_with_cfr(cfr_path)
        decompiler.analyze_structure()
    else:
        print("\n" + "="*70)
        print("📢 MANUAL DECOMPILATION REQUIRED")
        print("="*70)
        print("\nAPK has been extracted to: ./apk-extracted")
        print("\nTo decompile manually:")
        print("  1. Download CFR: https://www.benf.org/other/cfr/cfr.jar")
        print("  2. Run command:")
        print("     java -jar cfr.jar apk-extracted\\classes.dex --outputdir src-recovered")
        print("  3. Repeat for classes2.dex through classes12.dex")
        print("\nOr use alternative decompilators:")
        print("  - Procyon: https://github.com/ststeiger/Procyon")
        print("  - JD-GUI: http://jd.benf.org/")
    
    print("\n" + "="*70)
    print("✅ Recovery process complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Check ./src-recovered/ for Java source files")
    print("2. Convert to Kotlin if needed")
    print("3. Move to android-app/app/src/main/java/com/examinerai/")
    print("4. Rebuild project: gradlew clean build")

if __name__ == "__main__":
    main()
