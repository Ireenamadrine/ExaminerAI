# ============================================================================
# ExaminerAI Build Instructions - Quick Reference
# ============================================================================

## Prerequisites

1. **Android Studio 2024.1+**
   - Download: https://developer.android.com/studio
   - Install with Android SDK 34

2. **Java 17+**
   ```bash
   java -version  # Should show Java 17 or higher
   ```

3. **Python 3.10+**
   ```bash
   python --version  # Should show 3.10 or higher
   ```

4. **Ollama (Optional, but Recommended for LLM)**
   - Download: https://ollama.ai
   - Install: Run installer
   - Start: `ollama serve`

5. **Environment Variables**
   - Set `ANDROID_SDK_ROOT` if not already set

---

## Building APK and AAB Files

### Option 1: Using Gradle (Recommended)

```bash
# Navigate to project root
cd c:\Users\harpr\examinerai

# Navigate to Android app directory
cd android-app

# Clean build
./gradlew clean

# Build Debug APK (for testing)
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk

# Build Release APK (for sideloading)
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/app-release.apk

# Build App Bundle for Play Store
./gradlew bundleRelease
# Output: app/build/outputs/bundle/release/app-release.aab
```

### Option 2: Using PowerShell Scripts (Windows)

```powershell
# From the android-app directory
cd android-app

# Build Release APK
.\build-release-apk.ps1 -SkipVersionBump

# Build Release AAB
.\build-release-aab.ps1 -SkipVersionBump
```

### Option 3: Using Python Build Manager (Cross-Platform)

```bash
# From project root
python build_manager.py --all

# Or individual builds:
python build_manager.py --apk-debug
python build_manager.py --apk-release
python build_manager.py --aab
```

---

## Build Output Locations

| Build Type | Debug APK | Release APK | AAB |
|-----------|-----------|-------------|-----|
| Location | `android-app/app/build/outputs/apk/debug/` | `android-app/app/build/outputs/apk/release/` | `android-app/app/build/outputs/bundle/release/` |
| Size | ~50-80 MB | ~40-60 MB | ~20-40 MB |
| Use Case | Local testing | Sideloading | Play Store |

---

## Installation and Testing

### Install on Connected Device/Emulator

```bash
# Install debug APK
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Install release APK
adb install -r app/build/outputs/apk/release/app-release.apk

# Run app
adb shell am start -n com.example.examinerai/.MainActivity

# Check logs
adb logcat | grep examinerai
```

### View Connected Devices

```bash
adb devices
# Output:
# emulator-5554           device
# 192.168.1.100:5555      device
```

---

## Troubleshooting Common Build Issues

### Issue: "Build Failed" with Gradle Error

**Solution:**
```bash
# Clear gradle cache
./gradlew clean

# Update gradle
./gradlew wrapper --gradle-version=8.2.1

# Try building again
./gradlew assembleRelease --info
```

### Issue: "No SDK located" Error

**Solution:**
```bash
# Set ANDROID_SDK_ROOT environment variable
# Windows (PowerShell):
$env:ANDROID_SDK_ROOT = "C:\Users\YourUsername\AppData\Local\Android\Sdk"

# Linux/Mac:
export ANDROID_SDK_ROOT=~/Android/Sdk

# Verify
echo $env:ANDROID_SDK_ROOT
```

### Issue: "Insufficient Memory" During Build

**Solution:**
```bash
# Increase JVM memory
./gradlew assembleRelease -Dorg.gradle.jvmargs="-Xmx4g -Xms2g"

# Or add to gradle.properties:
# org.gradle.jvmargs=-Xmx4g -Xms2g
```

### Issue: "Keystore Not Found" When Building Release

**Solution:**
```bash
# Create keystore if missing
# Windows:
keytool -genkey -v -keystore examinerai.jks `
  -keyalg RSA -keysize 2048 `
  -validity 10000 -alias examinerai

# Set password in gradle.properties
cat app/gradle.properties | grep SIGN_
```

---

## Signing Configuration

The app is configured to use a keystore for signing. Update `gradle.properties`:

```properties
# Keystore location and credentials
SIGN_STORE_FILE=examinerai.jks
SIGN_STORE_PASSWORD=your_secure_password
SIGN_KEY_ALIAS=examinerai
SIGN_KEY_PASSWORD=your_key_password
```

---

## Release Checklist

Before releasing to Play Store:

- [ ] Updated `versionCode` and `versionName` in build.gradle
- [ ] Added release notes for this version
- [ ] Tested app on multiple Android versions (26, 30, 34)
- [ ] Tested all features (student, teacher, examiner roles)
- [ ] Verified network connectivity (Ollama backend)
- [ ] Checked app permissions in manifest
- [ ] Verified signing configuration
- [ ] Generated signed AAB (for Play Store)
- [ ] Created screenshots and store listing
- [ ] Completed privacy policy and terms of service
- [ ] Set appropriate content rating

---

## Play Store Upload

1. **Build signed AAB:**
   ```bash
   ./gradlew clean bundleRelease
   ```

2. **Sign APKs from Bundle:**
   - Use bundletool to generate APKs:
   ```bash
   bundletool build-apks \
     --bundle=app-release.aab \
     --output=app-release.apks \
     --ks=examinerai.jks \
     --ks-pass=pass:your_password \
     --ks-key-alias=examinerai \
     --key-pass=pass:your_key_password
   ```

3. **Upload to Play Console:**
   - Go to play.google.com/console
   - Select your app
   - Upload AAB in "Release" > "Production"
   - Fill in release notes
   - Submit for review

4. **Monitor:**
   - Check Play Console dashboard
   - Monitor crash reports
   - Read user reviews
   - Update with bug fixes

---

## Environment Setup for CI/CD

For automated builds (GitHub Actions, GitLab CI, etc.):

```yaml
# GitHub Actions example
name: Build APK and AAB

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Build APK
        run: |
          cd android-app
          ./gradlew assembleRelease
      
      - name: Build AAB
        run: |
          cd android-app
          ./gradlew bundleRelease
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: builds
          path: |
            android-app/app/build/outputs/apk/release/
            android-app/app/build/outputs/bundle/release/
```

---

## Performance Optimization

### Reduce APK Size

```gradle
// In build.gradle
android {
    bundle {
        language.enableSplit = true
        density.enableSplit = true
        abi.enableSplit = true
    }
}
```

### Enable Shrinking and Obfuscation

```gradle
buildTypes {
    release {
        minifyEnabled true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
}
```

---

## Version Management

Update version in `android-app/app/build.gradle`:

```gradle
android {
    defaultConfig {
        versionCode 10  // Increment for each release
        versionName "1.1"  // Semantic versioning
    }
}
```

---

**For detailed information on specific features, see [COMPLETE_ENHANCEMENT_GUIDE.md](COMPLETE_ENHANCEMENT_GUIDE.md)**
