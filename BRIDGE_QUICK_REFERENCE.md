# ExaminerAI Bridge API: Quick Reference

## ðŸ“ Base URLs

| Client | URL |
|--------|-----|
| **Android Emulator** | `http://10.0.2.2:8001` |
| **Android Device** | `http://192.168.1.100:8001` (replace IP) |
| **Python Dev** | `http://localhost:8001` |
| **Docker/Production** | `https://api.example.com` (custom) |

---

## ðŸš€ Quick Start

### Start Python Bridge
```bash
cd c:\Users\harpr\examinerai
python bridge/server.py
# Output: Bridge server running on http://127.0.0.1:8001
```

### Test with cURL
```bash
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{
    "topic":"physics",
    "user_input":"What is energy?",
    "confidence":0.5,
    "weakness":0.5,
    "last_action":"ask_clarification",
    "user_feedback":"ask",
    "license_valid":true
  }'
```

---

## ðŸ“¡ Endpoints

### POST /process
**Core learning engine**
- Takes user input + learning state
- Returns action + response message
- Used for: Ask, Evaluate, Study questions

**Required Fields**:
```json
{
  "topic": "string (max 200)",
  "user_input": "string (max 4000)",
  "confidence": "number",
  "weakness": "number",
  "last_action": "string",
  "user_feedback": "string"
}
```

**Optional Fields**:
```json
{
  "mode": "tutor|quiz|exam",
  "license_valid": true|false
}
```

**Success Response** (200):
```json
{
  "action": "explain|ask_clarification|be_concise|...",
  "message": "response text",
  "status": "ok",
  "profile": "calm_tutor|strict_examiner",
  "mode": "tutor|quiz|exam"
}
```

**Error Responses**:
```
400 - Invalid JSON / Missing fields / Bad types
402 - Exam mode requires license
413 - Input too long (>4000 chars)
429 - Too many requests (>30/min)
500 - Server error
```

---

### POST /web-check
**Fetch and extract text from URLs**
- Requires `web_access: true` in settings
- Used for: Browse Web in Study Tools

**Request**:
```json
{
  "url": "https://wikipedia.org/..."
}
```

**Success Response** (200):
```json
{
  "url": "...",
  "text": "extracted content",
  "status": "ok"
}
```

**Errors**:
```
400 - Missing url field
403 - Web access disabled or URL blocked
502 - Fetch failed
```

---

## ðŸŽ¯ Actions Reference

| Action | When Used | Example Output |
|--------|-----------|-----------------|
| `explain` | Medium-low confidence | "Energy is the capacity to do work..." |
| `explain_step_by_step` | Low confidence + high weakness | "Step 1: ... Step 2: ... Step 3: ..." |
| `ask_clarification` | Need more context | "Which part of physics is confusing?" |
| `be_concise` | High confidence, quick answer | "Energy cannot be destroyed." |
| `refuse` | Very low confidence (<0.2) | "I don't have verified info on this." |
| `stay_silent` | User mastery | "You seem comfortable. Let's move on." |

---

## ðŸ“Š Learning Parameters

### Confidence (0.0-1.0)
- **0.0-0.2**: "Very low - doesn't understand"
- **0.2-0.5**: "Low - has gaps"
- **0.5-0.7**: "Medium - partial understanding"
- **0.7-1.0**: "High - confident"

### Weakness (0.0-1.0)
- **0.0-0.3**: "Strong - knows well"
- **0.3-0.6**: "Moderate weakness"
- **0.6-1.0**: "Critical - needs focus"

---

## ðŸ” Headers & Auth

**All requests require**:
```
Content-Type: application/json
Content-Length: [auto-calculated]
```

**Rate Limiting**:
- **Limit**: 30 requests/minute per client IP
- **Violation**: Returns HTTP 429
- **Window**: 60 seconds

**License Validation**:
```json
{
  "mode": "exam",
  "license_valid": true  // â† Required for exam mode
}
```

---

## ðŸ› ï¸ Android Code Snippets

### EngineClient.kt (Network Client)
```kotlin
object EngineClient {
    private const val BASE_URL = "http://10.0.2.2:8001"  // Emulator
    // private const val BASE_URL = "http://192.168.1.100:8001"  // Device
    
    fun send(request: JSONObject): JSONObject {
        val url = URL("$BASE_URL/process")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.connectTimeout = 4000
        conn.readTimeout = 6000
        
        OutputStreamWriter(conn.outputStream).use { it.write(request.toString()) }
        
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val responseText = BufferedReader(InputStreamReader(stream)).readText()
        
        return if (code in 200..299) {
            JSONObject(responseText)
        } else {
            JSONObject().put("status", "error").put("message", "HTTP $code")
        }
    }
}
```

### Building Request (QuizScreen.kt)
```kotlin
val request = JSONObject()
    .put("topic", "thermodynamics")
    .put("user_input", userInput)
    .put("confidence", 0.55)
    .put("weakness", 0.45)
    .put("last_action", lastAction)
    .put("user_feedback", feedback)
    .put("mode", "quiz")
    .put("license_valid", true)

val response = EngineClient.send(request)
val action = response.optString("action")
val message = response.optString("message")
```

### Error Handling
```kotlin
try {
    return EngineClient.send(request)
} catch (e: Exception) {
    return PythonService.getInstance(context).processWithEngine(...)
}
```

### Store in Database
```kotlin
AppDatabase.get(context).interactionDao().insert(
    InteractionEntity(
        topic = "thermodynamics",
        action = action,
        reward = reward
    )
)
```

---

## ðŸ§ª Testing Checklist

### Before Deployment

- [ ] Bridge server starts without errors
- [ ] Can connect from emulator: `adb shell curl http://10.0.2.2:8001/process`
- [ ] Can connect from device: `adb shell curl http://192.168.1.x:8001/process`
- [ ] Request with required fields returns 200
- [ ] Request with missing fields returns 400
- [ ] 31st request in 1 minute returns 429
- [ ] Exam mode without license returns 402
- [ ] Response can be parsed as JSON
- [ ] Action is one of the 6 valid actions
- [ ] Message field is non-empty
- [ ] Database stores interactions correctly

### Manual Tests

```bash
# Test 1: Valid request
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","user_input":"test?","confidence":0.5,"weakness":0.5,"last_action":"ask","user_feedback":"ask"}'
# Expected: 200, action present

# Test 2: Missing field
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","user_input":"test?"}'
# Expected: 400, "Missing fields"

# Test 3: Invalid JSON
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d 'invalid json'
# Expected: 400, "Invalid JSON"

# Test 4: Too long input
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","user_input":"'"$(python -c 'print("x"*5000)')"'","confidence":0.5,"weakness":0.5,"last_action":"ask","user_feedback":"ask"}'
# Expected: 413, "Input too long"

# Test 5: Exam without license
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","user_input":"test?","confidence":0.5,"weakness":0.5,"last_action":"ask","user_feedback":"ask","mode":"exam","license_valid":false}'
# Expected: 402, "Exam mode requires activation"
```

---

## âš¡ Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Network roundtrip | <50ms | 20-50ms |
| Engine processing | <200ms | 50-200ms |
| Total latency | <300ms | 100-300ms |
| DB insert | <20ms | 5-20ms |
| Queries all interactions | <50ms | 10-50ms |

---

## ðŸš¨ Common Issues & Fixes

### Issue: "Connection refused"
**Cause**: Bridge not running
```bash
# Solution: Start bridge
python bridge/server.py
```

### Issue: "Connection timeout: 10.0.2.2"
**Cause**: Bridge not running, wrong port, or host firewall blocks access
```bash
# Emulator case (usually works with localhost bind):
python bridge/server.py

# Device-on-WiFi case (must expose on LAN):
python -c "from bridge.server import run; run(host='0.0.0.0', port=8001)"
``` 

### Issue: Device returns HTTP 429
**Cause**: Rate limit exceeded (>30 requests/minute)
```
Solution: Wait 60 seconds before retrying
```

### Issue: Empty response
**Cause**: Missing required fields
```bash
# Check all 6 required fields:
topic, user_input, confidence, weakness, last_action, user_feedback
```

### Issue: "Exam mode requires activation"
**Cause**: `license_valid: false` with `mode: exam`
```json
"mode": "exam",
"license_valid": true  // â† Must be true
```

---

## ðŸ”„ Request/Response Flow

```
Android App
    â†“ POST /process + JSONObject
Python Bridge (bridge/server.py)
    â†“ _handle_process()
    â”œâ”€ Validate JSON & rate limit
    â””â”€ Parse request fields
    â†“
Core Intelligence (core_intelligence/engine.py)
    â”œâ”€ build_state()
    â”œâ”€ choose_action()  [Q-learning: 6 actions]
    â”œâ”€ cognitive_control()
    â”œâ”€ calculate_reward()
    â””â”€ log_interaction()
    â†“
Tutor Executor (tutor/executor.py)
    â””â”€ tutor_execute(action)  [Format response]
    â†“
Phrasing (core_intelligence/phrasing.py)
    â””â”€ phrase()  [Apply style]
    â†“ HTTP 200 + JSON
Android App (QuizScreen.kt)
    â”œâ”€ Parse response
    â”œâ”€ Extract action & message
    â””â”€ Store in Room DB
```

---

## ðŸ“‹ Configuration

### Python (bridge/server.py)
```python
def run(host: str = "127.0.0.1", port: int = 8001):
    server = HTTPServer((host, port), BridgeHandler)
    server.serve_forever()

# For network access from devices:
run(host='0.0.0.0', port=8001)

# Or specify IP:
run(host='192.168.1.100', port=8001)
```

### Android (EngineClient.kt)
```kotlin
private const val BASE_URL = "http://10.0.2.2:8001"  // Emulator
// OR
private const val BASE_URL = "http://192.168.1.100:8001"  // Device (change IP)
```

### Python Settings (control_panel/state.json)
```json
{
  "profile": "calm_tutor",  // or "strict_examiner"
  "web_access": false,       // Allow /web-check
  "llm_enabled": false       // Future feature
}
```

---

## ðŸ“š Documentation Files

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[BRIDGE_TECHNICAL_REFERENCE.md](BRIDGE_TECHNICAL_REFERENCE.md)** - Architecture & examples
- **[ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md)** - Android setup & config
- **[BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md)** - This file

---

## ðŸ”— Key Files

| File | Purpose |
|------|---------|
| `bridge/server.py` | HTTP bridge server |
| `core_intelligence/engine.py` | Learning engine (core_step) |
| `core_intelligence/q_learning.py` | Q-learning & actions |
| `tutor/executor.py` | Execute actions into responses |
| `android-app/app/src/main/java/com/example/examinerai/EngineClient.kt` | Android network client |
| `android-app/app/src/main/java/com/example/examinerai/QuizScreen.kt` | Main UI that sends requests |
| `android-app/app/src/main/java/com/example/examinerai/AppDatabase.kt` | Room database |

---

## ðŸ“ž Support

### Check Logs
```bash
# Python bridge logs
python bridge/server.py 2>&1 | tee bridge.log

# Android logs
adb logcat | grep QuizDesk
```

### Test Connectivity
```bash
# From Android
adb shell
curl -v http://10.0.2.2:8001/process

# From Python PC
curl http://localhost:8001/process
```

### Network Debugging
```bash
# Check if bridge is listening
netstat -ano | find ":8001"

# Monitor requests from firewall
# Windows Defender Firewall â†’ Allow an app through
```

---

**Version**: 1.0  
**Last Updated**: 2026-02-22  
**Compatibility**: Android API 28+, Python 3.8+


