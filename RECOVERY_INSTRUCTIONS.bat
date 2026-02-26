@echo off
REM This script helps recover your source code

echo.
echo ============================================================
echo  MANUAL SOURCE CODE RECOVERY TOOL
echo ============================================================
echo.
echo Your actual code is in these DEX files:
echo.

dir apk-extracted\classes*.dex

echo.
echo ============================================================
echo  OPTION 1: Use Online Decompiler (BEST - 5 minutes)
echo ============================================================
echo.
echo 1. Open browser: https://www.javadecompilers.com/
echo 2. Click "Upload File"
echo 3. Select: apk-extracted\classes.dex
echo 4. Wait for decompilation (2-5 min)
echo 5. Download the ZIP with Java files
echo 6. Extract and copy to: android-app\app\src\main\java\com\examinerai\
echo 7. Run: gradlew clean build
echo.
echo ============================================================
echo  OPTION 2: Use If You Have dex2jar + CFR
echo ============================================================
echo.
echo cd apk-extracted
echo dex2jar classes.dex
echo java -jar cfr.jar classes-dex2jar.jar --outputdir ..\src-recovered
echo.
echo Then copy recovered files to android-app\app\src\main\java\com\examinerai\
echo.
echo ============================================================
echo.
