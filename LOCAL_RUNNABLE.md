# Local Runnable Checklist

## 1) Start Python bridge

```powershell
.\scripts\run_bridge.ps1
```

Default URL is `http://127.0.0.1:8001`.

For emulator use in app settings:
- `http://10.0.2.2:8001`

For physical phone use your PC LAN IP, e.g.:
- `http://192.168.1.20:8001`

## 2) Run safety smoke checks

```powershell
.\scripts\pre_release_check.ps1
```

This validates:
- Python syntax
- command-dispatch flow (`upload/chat/exam/plan/slides/outputs/download`)
- Android debug compilation

## 3) Build signed release artifacts

```powershell
.\build-release-aab.ps1 -SkipVersionBump
.\build-release-apk.ps1 -SkipVersionBump
```

Outputs:
- `android-app/app/build/outputs/bundle/standardRelease/app-standard-release.aab`
- `android-app/app/build/outputs/apk/standard/release/app-standard-release.apk`

## 4) Configure bridge in app

In app:
- `Settings` -> `Python Bridge`
- Set `Bridge URL`
- Tap `Save URL`
- Tap `Test Bridge`

If bridge is offline, app falls back to local Kotlin engine.

## 5) Configure hybrid AI behavior

In app:
- `Settings` -> `AI Answer Modes`
- Choose one mode:
  - `Strict Local`: uploaded source only
  - `Hybrid Local`: source + optional on-device LLM rewrite
  - `Hybrid Web`: source + browser-approved URL fallback
- Optional:
  - Enable `Show Iteration Trace` to see intent/retrieval/verification in chat
  - Enable `Local LLM` and set a GGUF model path
  - Add browser-approved URLs (one per line) for web fallback
