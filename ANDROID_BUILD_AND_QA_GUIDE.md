# Android Build and QA Guide (Local-Only)

## 1. Required Files

These files must exist for local upload logic + release builds:

- `android-app/app/build.gradle`
- `android-app/gradle.properties`
- `android-app/build-release-apk.ps1`
- `android-app/build-release-aab.ps1`
- `android-app/check-build-and-updates.ps1`
- `android-app/app/src/main/java/com/example/examinerai/UploadScreen.kt`
- `android-app/app/src/main/java/com/example/examinerai/LocalSourceRepository.kt`
- `android-app/app/src/main/java/com/example/examinerai/LocalStudyEngine.kt`
- `android-app/app/src/main/java/com/example/examinerai/LocalExportService.kt`
- `android-app/app/src/main/java/com/example/examinerai/QuizScreen.kt`
- `android-app/app/src/main/java/com/example/examinerai/ConversationMessageEntity.kt`
- `android-app/app/src/main/java/com/example/examinerai/ConversationMessageDao.kt`
- `android-app/app/src/main/java/com/example/examinerai/WeaknessEntity.kt`
- `android-app/app/src/main/java/com/example/examinerai/WeaknessDao.kt`
- `android-app/app/src/main/java/com/example/examinerai/GeneratedOutputEntity.kt`
- `android-app/app/src/main/java/com/example/examinerai/GeneratedOutputDao.kt`

## 2. Generate Signed APK and AAB

```powershell
cd C:\Users\harpr\examinerai\android-app
.\build-release-apk.ps1 -SkipVersionBump
.\build-release-aab.ps1 -SkipVersionBump
```

Output paths:

- APK: `android-app/app/build/outputs/apk/standard/release/app-standard-release.apk`
- AAB: `android-app/app/build/outputs/bundle/standardRelease/app-standard-release.aab`

## 3. Check Code Updated or Not

Run:

```powershell
cd C:\Users\harpr\examinerai\android-app
.\check-build-and-updates.ps1
```

What it gives:

- current `versionCode` and `versionName`
- timestamp of key Kotlin files
- SHA256 hash of generated APK/AAB (if present)

If you use Git in future:

```powershell
git status
git diff -- app/src/main/java/com/example/examinerai/LocalStudyEngine.kt
```

## 4. Full Build + Verification in One Command

```powershell
cd C:\Users\harpr\examinerai\android-app
.\check-build-and-updates.ps1 -BuildReleaseApk -BuildReleaseAab
```

## 5. Efficiency and Correctness Test Matrix

After install, test all of these from one uploaded PDF and one TXT:

1. Upload works and opens quiz screen.
2. Ask tab: `Explain`, `Summarize`, `Perfect English`.
3. Questions tab: `Practice Paper`, `Answer Key`, `Marking Scheme`.
4. Study Tools tab: PPT export + PDF export.
5. Evaluation tab: score + keyword trace appears.
6. Progress tab: weak areas and strategic plan update.
7. Ask tab: previous chat turns persist after app restart for the same topic.
8. Evaluation tab: repeated missing keywords reduce score via RLVR penalties.
9. Outputs tab: question/study outputs appear separately from chat.
10. Outputs tab: export any output as PDF and Word-compatible RTF.

## 6. Basic Runtime Logs

If device connected:

```powershell
adb logcat | Select-String "UploadScreen|LocalSourceRepo|LocalStudyEngine"
```

Use this when upload/format/export does not behave as expected.
