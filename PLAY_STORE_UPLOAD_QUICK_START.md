# Play Store Upload Quick Start

## Files Ready for Upload

```
APK (Direct Install):
c:\Users\harpr\examinerai\android-app\app\build\outputs\apk\standard\release\app-standard-release.apk
Size: 34.9 MB

AAB (Recommended for Play Store):
c:\Users\harpr\examinerai\android-app\app\build\outputs\bundle\standardRelease\app-standard-release.aab
Size: 31.2 MB
```

---

## 5-Minute Play Store Upload

### 1. Go to Google Play Console
https://play.google.com/console

### 2. Create App or Select Existing
- App name: **ExaminerAI**
- Package ID: **com.example.examinerai**
- App category: **Education**

### 3. Upload Your Build
Left sidebar → **Release → Production** → **Create new release**

**Click "Upload": Select your AAB file**
```
app-standard-release.aab (31.2 MB)
```

### 4. Fill Release Details
```
Release name: v1.1
Notes to testers:
[Paste from RELEASE_BUILD_SUMMARY.md section "Release Notes"]
```

### 5. Complete Store Listing
- **Title:** ExaminerAI - AI Learning Assistant
- **Short description (80 chars max):**
  ```
  AI-powered tutoring platform with ChatGPT-style chat 
  and quality analysis.
  ```
- **Full description:**
  ```
  ExaminerAI is an intelligent tutoring platform powered by advanced AI.
  
  🎓 Features:
  • ChatGPT-style chat interface with streaming responses
  • Real-time AI thinking process visualization
  • Quality metrics for response evaluation
  • PDF and Word document export
  • Dark mode support
  • Multimodal learning (text, audio, images)
  • Role-based personalization
  • Gamification and progress tracking
  • Chat history and offline learning
  
  Perfect for:
  ✏️ Students preparing for exams
  📚 Studying complex topics
  💼 Professionals learning new skills
  🎯 Interactive homework help
  
  All powered by local and cloud AI models.
  ```

### 6. Add Screenshots
- Screen size: 6.7" (1440×3200 or similar)
- Language: English
- Add 2-5 screenshots showing:
  1. Chat interface
  2. Quality metrics
  3. Dark mode
  4. Export feature
  5. Settings/themes

### 7. Content Rating
Complete IARC questionnaire:
- Category: **Education**
- Content: **Learning material, no mature content**

### 8. Review and Submit
✅ Check all fields  
✅ Accept Play Store policies  
✅ Click **Review release**  
✅ Click **Start rollout to Production**

**Wait 1-5 hours for review...**

---

## Version Management for Future Releases

Each time you build:
1. Your version code must increase
2. Generate new APK/AAB
3. Upload the AAB file
4. App will be automatically available to users

### Auto-version Bump
```bash
cd android-app
.\build-release-aab.ps1    # Bumps version + builds
```

---

## Key Play Store Requirements

✅ Icon: 512×512 PNG  
✅ Keystore signature: Done (v2 scheme)  
✅ Package name matches: com.example.examinerai  
✅ Min SDK 26+: Yes  
✅ Target SDK 34: Yes  
✅ Content rating: Required  
✅ Privacy policy: Recommended  

---

## After Going Live

Monitor:
```
Google Play Console → Dashboard
├── Users/Installs
├── Crash reports
├── Ratings & Reviews
├── Performance metrics
└── Revenue (if monetized)
```

Check logs regularly to catch errors early!

---

## Troubleshooting Play Store Issues

**"Incompatible with all devices"**
→ Check min/target SDK in build.gradle

**"Content policy violation"**
→ Review app permissions and description

**"Too many similar apps"**
→ Unique selling points: Showcase AI chat + quality metrics

**"Installation fails on some devices"**
→ Test on API 26+ devices; check architecture support

---

## Support Resources

- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [App Signing Requirements](https://developer.android.com/studio/publish/app-signing)
- [Play Store Policy Center](https://play.google.com/intl/en/about/developer-content-policy/)

**You're all set! Good luck! 🚀**
