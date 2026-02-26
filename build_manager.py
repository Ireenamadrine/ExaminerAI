#!/usr/bin/env python3
"""
ExaminerAI Build & Deployment Script
Comprehensive build automation for APK, AAB, and testing
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class BuildManager:
    """Manage builds for ExaminerAI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.android_dir = self.project_root / "android-app"
        self.build_output_dir = self.android_dir / "app" / "build" / "outputs"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def info(self, message: str):
        """Print info message"""
        print(f"\n📱 {message}")
        
    def success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
        
    def error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
        
    def run_command(self, command: str, cwd: Path = None) -> bool:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=False
            )
            return result.returncode == 0
        except Exception as e:
            self.error(f"Command failed: {e}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        self.info("Checking prerequisites...")
        
        prerequisites = [
            ("Java", "java -version"),
            ("Gradle", "gradle -version"),
            ("Python", "python --version"),
            ("Git", "git --version")
        ]
        
        all_ok = True
        for name, cmd in prerequisites:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.success(f"{name} ✓")
                else:
                    self.error(f"{name} ✗ - Not found or error")
                    all_ok = False
            except Exception as e:
                self.error(f"{name} ✗ - {e}")
                all_ok = False
        
        return all_ok
    
    def setup_environment(self) -> bool:
        """Setup build environment"""
        self.info("Setting up build environment...")
        
        # Check Android SDK
        sdk_root = os.environ.get("ANDROID_SDK_ROOT")
        if not sdk_root:
            self.error("ANDROID_SDK_ROOT not set")
            return False
        
        self.success("Android SDK configured")
        return True
    
    def build_apk_debug(self) -> bool:
        """Build debug APK"""
        self.info("Building Debug APK...")
        
        if not self.run_command("./gradlew assembleDebug", cwd=self.android_dir):
            self.error("Debug APK build failed")
            return False
        
        apk_path = self.android_dir / "app/build/outputs/apk/debug/app-debug.apk"
        if apk_path.exists():
            self.success(f"Debug APK created: {apk_path}")
            return True
        else:
            self.error("Debug APK not found")
            return False
    
    def build_apk_release(self) -> bool:
        """Build release APK"""
        self.info("Building Release APK...")
        
        if not self.run_command("./gradlew clean", cwd=self.android_dir):
            self.error("Clean failed")
            return False
        
        if not self.run_command("./gradlew assembleRelease", cwd=self.android_dir):
            self.error("Release APK build failed")
            return False
        
        apk_path = self.android_dir / "app/build/outputs/apk/release/app-release.apk"
        if apk_path.exists():
            self.success(f"Release APK created: {apk_path}")
            self._copy_to_releases(apk_path, f"app-release-{self.timestamp}.apk")
            return True
        else:
            self.error("Release APK not found")
            return False
    
    def build_aab(self) -> bool:
        """Build Android App Bundle (AAB) for Play Store"""
        self.info("Building Android App Bundle (AAB)...")
        
        if not self.run_command("./gradlew clean", cwd=self.android_dir):
            self.error("Clean failed")
            return False
        
        if not self.run_command("./gradlew bundleRelease", cwd=self.android_dir):
            self.error("AAB build failed")
            return False
        
        aab_path = self.android_dir / "app/build/outputs/bundle/release/app-release.aab"
        if aab_path.exists():
            self.success(f"AAB created: {aab_path}")
            self._copy_to_releases(aab_path, f"app-release-{self.timestamp}.aab")
            return True
        else:
            self.error("AAB not found")
            return False
    
    def _copy_to_releases(self, source: Path, filename: str):
        """Copy build output to releases directory"""
        releases_dir = self.project_root / "releases"
        releases_dir.mkdir(exist_ok=True)
        
        dest = releases_dir / filename
        import shutil
        shutil.copy2(source, dest)
        self.success(f"Build copied to {dest}")
    
    def run_lint(self) -> bool:
        """Run Kotlin lint checks"""
        self.info("Running Kotlin Lint...")
        
        if not self.run_command("./gradlew lint", cwd=self.android_dir):
            self.error("Lint check failed")
            return False
        
        self.success("Lint check passed")
        return True
    
    def run_tests(self) -> bool:
        """Run unit tests"""
        self.info("Running unit tests...")
        
        if not self.run_command("./gradlew test", cwd=self.android_dir):
            self.error("Tests failed")
            return False
        
        self.success("All tests passed")
        return True
    
    def generate_build_report(self) -> bool:
        """Generate build report"""
        self.info("Generating build report...")
        
        report = {
            "timestamp": self.timestamp,
            "project": "ExaminerAI",
            "builds_completed": [],
            "artifacts": []
        }
        
        # Check for build artifacts
        for apk in self.build_output_dir.glob("**/app-*.apk"):
            report["artifacts"].append({
                "type": "APK",
                "path": str(apk),
                "size_mb": apk.stat().st_size / (1024 * 1024)
            })
        
        for aab in self.build_output_dir.glob("**/app-*.aab"):
            report["artifacts"].append({
                "type": "AAB",
                "path": str(aab),
                "size_mb": aab.stat().st_size / (1024 * 1024)
            })
        
        report_path = self.project_root / f"build-report-{self.timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.success(f"Build report saved to {report_path}")
        return True
    
    def install_on_device(self, apk_path: str = None) -> bool:
        """Install APK on connected device"""
        self.info("Installing APK on device...")
        
        if not apk_path:
            apk_path = self.android_dir / "app/build/outputs/apk/debug/app-debug.apk"
        
        if not Path(apk_path).exists():
            self.error(f"APK not found at {apk_path}")
            return False
        
        if not self.run_command(f"adb install -r {apk_path}"):
            self.error("Installation failed")
            return False
        
        self.success("APK installed successfully")
        return True
    
    def run_on_device(self) -> bool:
        """Run app on connected device"""
        self.info("Running app on device...")
        
        cmd = "adb shell am start -n com.example.examinerai/.MainActivity"
        if not self.run_command(cmd):
            self.error("Failed to start app")
            return False
        
        self.success("App started on device")
        return True
    
    def build_all(self, skip_tests: bool = False) -> bool:
        """Build everything (APK, AAB)"""
        self.info("Starting complete build process...")
        self.info(f"Timestamp: {self.timestamp}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.error("Prerequisites check failed")
            return False
        
        # Setup environment
        if not self.setup_environment():
            self.error("Environment setup failed")
            return False
        
        # Optional: Run tests
        if not skip_tests:
            if not self.run_tests():
                self.error("Tests failed - continuing anyway")
        
        # Run lint
        if not self.run_lint():
            self.error("Lint check failed - continuing anyway")
        
        # Build APK (debug)
        if not self.build_apk_debug():
            self.error("Debug APK build failed")
            return False
        
        # Build APK (release)
        if not self.build_apk_release():
            self.error("Release APK build failed")
            return False
        
        # Build AAB
        if not self.build_aab():
            self.error("AAB build failed")
            return False
        
        # Generate report
        if not self.generate_build_report():
            self.error("Report generation failed")
            return False
        
        self.success("Complete build process finished!")
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ExaminerAI Build & Deployment Tool"
    )
    parser.add_argument(
        "--apk-debug",
        action="store_true",
        help="Build debug APK"
    )
    parser.add_argument(
        "--apk-release",
        action="store_true",
        help="Build release APK"
    )
    parser.add_argument(
        "--aab",
        action="store_true",
        help="Build AAB for Play Store"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build everything (APK debug, APK release, AAB)"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install debug APK on device"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run app on device"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run unit tests"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run lint checks"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip tests when building"
    )
    
    args = parser.parse_args()
    
    manager = BuildManager()
    
    # If no args provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Execute requested operations
    try:
        if args.all:
            manager.build_all(skip_tests=args.skip_tests)
        
        if args.apk_debug:
            manager.build_apk_debug()
        
        if args.apk_release:
            manager.build_apk_release()
        
        if args.aab:
            manager.build_aab()
        
        if args.test:
            manager.run_tests()
        
        if args.lint:
            manager.run_lint()
        
        if args.install:
            manager.install_on_device()
        
        if args.run:
            manager.run_on_device()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Build failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
