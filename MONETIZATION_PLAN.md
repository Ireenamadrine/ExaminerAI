# Monetization Gates (Exam Mode)

Concept:
- License flag stored locally (Keystore-bound token or purchase receipt hash).
- Engine enforces before running exam-mode actions.

Pseudo (Python reference):
```
def ensure_exam_access(license_valid: bool):
    if not license_valid:
        return False, "Exam mode requires activation."
    return True, None
```

Integration points:
- CLI/bridge: reject `mode=exam` when license missing.
- Android: validate Play Billing purchase, cache token, pass `license_valid` to engine.
- No LLM/UI override.

Products:
- Monthly exam pass (e.g., $2.99/month).
- Lifetime unlock.

Compliance:
- Keep exam constraints ethical: strict timing, silence mode, deeper RLVR history.
