# User-Friendly Improvements Research Notes (Local-First)

Date: 2026-02-22
Scope: ExaminerAI Android app, fully local/offline use.

## High-Impact Improvements

1. Keep all primary tap targets at least 48dp.
- Why: reduces miss-taps and improves accessibility.
- Current status: header action buttons adjusted to 48dp in `android-app/app/src/main/java/com/example/examinerai/QuizScreen.kt`.

2. Use stronger text-input validation and helper states for Ask/Evaluation.
- Why: users need immediate feedback when they send empty or low-context prompts.
- Action: add inline supporting/error text and character guidance in `QuizScreen.kt` for Ask and Evaluation text fields.

3. Keep file upload on Storage Access Framework (SAF) with persistent URI permission.
- Why: this is Android’s supported way for long-term file access from device storage.
- Current status: already implemented in `UploadScreen.kt` via `OpenDocument` + `takePersistableUriPermission`.

4. Add adaptive navigation for larger screens.
- Why: improves UX on tablets/Chromebooks and avoids stretched phone UI.
- Action: add adaptive navigation patterns in Compose for compact/medium/expanded widths.

5. Tighten release quality gates before every Play upload.
- Why: reduces crashes/ANRs and policy risk.
- Action: run pre-launch reports and monitor Android vitals for crash/ANR regressions.

## Suggested UX Backlog (Next Sprint)

- Add explicit "Indexed locally" and source format chip in each library card.
- Add upload progress + parse summary (pages/lines/terms extracted).
- Add one-tap output actions from generated response (Save as PDF, Save as PPT outline, Copy answer key).
- Add first-run flow: choose Strict or Lenient mode with examples.
- Add "Boundary Health" panel to show exactly which sources are locked for current answer.

## References

- Android accessibility and touch target guidance:
  - https://support.google.com/accessibility/android/answer/7101858
- Compose text input guidance:
  - https://developer.android.com/develop/ui/compose/text/user-input
- Adaptive navigation in Compose:
  - https://developer.android.com/develop/ui/compose/layouts/adaptive/build-adaptive-navigation
- Storage Access Framework:
  - https://developer.android.com/training/data-storage/shared/documents-files
- Android vitals:
  - https://developer.android.com/topic/performance/vitals
- Google Play pre-launch reports:
  - https://support.google.com/googleplay/android-developer/answer/9844487
