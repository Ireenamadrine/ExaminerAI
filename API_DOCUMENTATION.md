# ExaminerAI API Documentation

## Overview
ExaminerAI uses a lightweight HTTP bridge (`bridge/server.py`) running on port 8001 to communicate between the Android app and the Python backend. The bridge validates input, applies safety gates, and delegates to the core intelligence engine.

---

## Base URL & Network Configuration

### Emulator
- **Base URL**: `http://10.0.2.2:8001`
- **Note**: `10.0.2.2` is the special Android emulator alias for the host machine's localhost

### Physical Device (Same Network)
- **Base URL**: `http://<HOST_IP>:8001`
- **Replace `<HOST_IP>`** with your Python host's IP address (e.g., `192.168.1.100`)
- **Enable bridging**: Ensure the device and host are on the same WiFi network

### Development Mode
- **Host**: `127.0.0.1` or `localhost`
- **Port**: `8001`
- **Default Python startup**: `python bridge/server.py` (runs on `127.0.0.1:8001`)

---

## HTTP Headers

All requests must include:
```
Content-Type: application/json
Content-Length: <calculated_by_client>
```

**Optional Headers** (for future authentication):
```
Authorization: Bearer <token>  (if enabled)
X-Client-Version: 1.0         (optional)
```

---

## Rate Limiting

- **Limit**: 30 requests per minute per client IP
- **Status Code**: `HTTP 429` (Too Many Requests)
- **Error Response**:
```json
{
  "error": "Too many requests"
}
```

---

## Core Endpoints

### 1. `/process` - Core Intelligence Endpoint

**Method**: `POST`

**Purpose**: Submit a user interaction (question, answer, feedback) to the learning engine and receive the next action/message.

#### Request Schema

```json
{
  "topic": "string (max 200 chars)",
  "user_input": "string (max 4000 chars)",
  "confidence": "number",
  "weakness": "number",
  "last_action": "string (previous action taken)",
  "user_feedback": "string (user's feedback on last response)",
  "mode": "string (optional, default: 'tutor') - 'tutor' or 'quiz' or 'exam'",
  "license_valid": "boolean (optional, default: false) - required for 'exam' mode"
}
```

#### Request Examples

##### Example 1: Asking a Question
```json
{
  "topic": "thermodynamics",
  "user_input": "What is the first law of thermodynamics?",
  "confidence": 0.55,
  "weakness": 0.45,
  "last_action": "ask_clarification",
  "user_feedback": "ask",
  "mode": "quiz",
  "license_valid": true
}
```

##### Example 2: Sending Feedback After Answer
```json
{
  "topic": "thermodynamics",
  "user_input": "Energy cannot be created or destroyed, only transformed.",
  "confidence": 0.65,
  "weakness": 0.35,
  "last_action": "explain",
  "user_feedback": "answered",
  "mode": "tutor",
  "license_valid": false
}
```

##### Example 3: Request Clarification
```json
{
  "topic": "quantum_mechanics",
  "user_input": "I don't understand wave-particle duality",
  "confidence": 0.30,
  "weakness": 0.70,
  "last_action": "refuse",
  "user_feedback": "unclear",
  "mode": "quiz",
  "license_valid": true
}
```

#### Response Schema (Success: 200 OK)

```json
{
  "action": "string - the action determined by learning engine",
  "message": "string - the response message to display to user",
  "status": "string - 'ok' on success",
  "profile": "string - current learning profile name",
  "mode": "string - the mode used for processing"
}
```

#### Response Examples

##### Example 1: Ask Clarification Response
```json
{
  "action": "ask_clarification",
  "message": "Which part of thermodynamics is confusing you?",
  "status": "ok",
  "profile": "strict_examiner",
  "mode": "quiz"
}
```

##### Example 2: Step-by-Step Explanation Response
```json
{
  "action": "explain_step_by_step",
  "message": "Step 1: Review the topic basics and identify what is unclear.\nStep 2: Energy is conserved in all processes.\nStep 3: Work and heat are forms of energy transfer.",
  "status": "ok",
  "profile": "calm_tutor",
  "mode": "tutor"
}
```

##### Example 3: Concise Explanation Response
```json
{
  "action": "be_concise",
  "message": "Energy cannot be created or destroyed, only transformed.",
  "status": "ok",
  "profile": "strict_examiner",
  "mode": "quiz"
}
```

#### Error Responses

##### 400 Bad Request - Invalid JSON
```json
{
  "error": "Invalid JSON"
}
```

##### 400 Bad Request - Missing Fields
```json
{
  "error": "Missing fields"
}
```

##### 400 Bad Request - Invalid Numeric Fields
```json
{
  "error": "Confidence/weakness must be numbers"
}
```

##### 413 Payload Too Large
```json
{
  "error": "Input too long"
}
```

##### 402 Payment Required - Exam Mode License
```json
{
  "error": "Exam mode requires activation"
}
```

##### 500 Internal Server Error (unhandled backend exception)
```json
{
  "error": "Backend processing error (format may vary)"
}
```

---

### 2. `/web-check` - Web Content Extraction Endpoint

**Method**: `POST`

**Purpose**: Fetch and extract main text from a web URL. Requires web access enabled in settings.

#### Request Schema

```json
{
  "url": "string - valid HTTP/HTTPS URL"
}
```

#### Request Example

```json
{
  "url": "https://en.wikipedia.org/wiki/Thermodynamics"
}
```

#### Response Schema (Success: 200 OK)

```json
{
  "url": "string - the URL that was fetched",
  "text": "string - extracted main text content",
  "status": "string - 'ok' on success"
}
```

#### Response Example

```json
{
  "url": "https://en.wikipedia.org/wiki/Thermodynamics",
  "text": "Thermodynamics is a branch of physics and chemistry... [extracted text]",
  "status": "ok"
}
```

#### Error Responses

##### 403 Forbidden - Web Access Disabled
```json
{
  "error": "Web access disabled"
}
```

##### 400 Bad Request - Missing URL
```json
{
  "error": "Missing url"
}
```

##### 403 Forbidden - URL Not Allowed
```json
{
  "error": "URL blocked by allowlist"
}
```

##### 502 Bad Gateway - Fetch Failed
```json
{
  "error": "Fetch failed: [detailed error message]"
}
```

---

## Available Actions

The engine can return these actions (matching `core_intelligence/q_learning.py`):

| Action | Use Case | Output Example |
|--------|----------|-----------------|
| `explain` | Full detailed explanation | "Energy cannot be created or destroyed..." |
| `explain_step_by_step` | Structured step-by-step breakdown | "Step 1: ... Step 2: ..." |
| `ask_clarification` | Ask user which part is unclear | "Which part of thermodynamics is confusing you?" |
| `refuse` | Indicate lack of verified information | "I do not have enough verified information..." |
| `be_concise` | Short, direct answer | "Energy is conserved." |
| `stay_silent` | Encourage independent thinking | "You seem comfortable with this topic. Let's move on." |

---

## Learning State Parameters

### Confidence (0.0-1.0)
- **0.0-0.2**: Very low - user doesn't understand
- **0.2-0.5**: Low - user has gaps
- **0.5-0.7**: Medium - user has partial understanding
- **0.7-1.0**: High - user is confident

### Weakness (0.0-1.0)
- **0.0-0.3**: Strong area - user knows well
- **0.3-0.6**: Moderate weakness
- **0.6-1.0**: Critical weakness - focus area

---

## Android Implementation (Java/Kotlin)

### EngineClient.kt
```kotlin
object EngineClient {
    private const val BASE_URL = "http://10.0.2.2:8001"

    fun send(request: JSONObject): JSONObject {
        val url = URL("$BASE_URL/process")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true
        conn.connectTimeout = 4000
        conn.readTimeout = 6000

        OutputStreamWriter(conn.outputStream).use { it.write(request.toString()) }

        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val responseText = BufferedReader(InputStreamReader(stream)).use { it.readText() }
        return if (code in 200..299) {
            JSONObject(responseText)
        } else {
            JSONObject()
                .put("status", "error")
                .put("action", "review")
                .put("message", responseText.ifBlank { "Backend returned HTTP $code" })
                .put("http_code", code)
        }
    }
}
```

### Usage in QuizScreen.kt
```kotlin
private suspend fun processDeskRequest(
    context: Context,
    userInput: String,
    lastAction: String,
    feedback: String
): JSONObject {
    val req = JSONObject()
        .put("topic", "thermodynamics")
        .put("user_input", userInput)
        .put("confidence", 0.55)
        .put("weakness", 0.45)
        .put("last_action", lastAction)
        .put("user_feedback", feedback)
        .put("mode", "quiz")
        .put("license_valid", true)
    
    return try {
        EngineClient.send(req).apply { put("_source", "backend") }
    } catch (e: Exception) {
        // Fallback to local PythonService if backend unavailable
        PythonService.getInstance(context).processWithEngine(
            topic = "thermodynamics",
            confidence = 0.55,
            weakness = 0.45,
            lastAction = lastAction,
            userFeedback = feedback,
            profileName = "strict_examiner"
        ).apply { put("_source", "local") }
    }
}
```

### Network Error Handling
```kotlin
// Timeout scenarios
conn.connectTimeout = 4000  // 4 seconds to connect
conn.readTimeout = 6000     // 6 seconds to read response

// HTTP error codes handled
if (code in 200..299) {
    // Success - parse response
} else {
    // Fallback to local processing
    return localFallback(...)
}
```

---

## Python Backend (bridge/server.py)

### Starting the Bridge
```bash
# Basic startup (localhost only)
python bridge/server.py

# Accessible from network
python -c "from bridge.server import run; run(host='0.0.0.0', port=8001)"
```

### Core Processing Flow
```python
1. Receive HTTP POST request on /process
2. Validate JSON and required fields
3. Check rate limiting per client IP
4. Validate numeric types (confidence, weakness must be parseable numbers)
5. Enforce license requirement for exam mode
6. Call core_step() from core_intelligence.engine
7. Execute action via tutor.executor.tutor_execute()
8. Apply phrasing filters via core_intelligence.phrasing
9. Return formatted JSON response
```

### Example: Processing Request
```python
def _handle_process(self):
    payload = self._read_json()
    
    # Validate
    required = ["topic", "user_input", "confidence", "weakness", 
                "last_action", "user_feedback"]
    if not all(key in payload for key in required):
        self._write_json(400, {"error": "Missing fields"})
        return
    
    # Process through engine
    action = core_step(
        topic=payload["topic"],
        confidence=float(payload["confidence"]),
        weakness=float(payload["weakness"]),
        last_action=payload["last_action"],
        user_feedback=payload["user_feedback"],
    )
    
    # Execute and phrase
    response_text = tutor_execute(action, payload["topic"], payload["user_input"])
    response_text = phrase(response_text)
    
    # Return
    self._write_json(200, {
        "action": action,
        "message": response_text,
        "status": "ok",
        "profile": get_current_profile_name(),
        "mode": payload.get("mode", "tutor"),
    })
```

---

## Request/Response Flow Diagram

```
┌──────────────┐
│ Android App  │
│ (QuizScreen) │
└──────┬───────┘
       │ JSONObject request
       │ (topic, user_input, confidence, weakness, last_action, user_feedback)
       │
       ▼
       HTTP POST /process
       Base: http://10.0.2.2:8001
       │
       ├─ Content-Type: application/json
       └─ 4000ms timeout
       │
       ▼
┌──────────────────────────┐
│  Python Bridge Server    │
│  (bridge/server.py)      │
│                          │
│  1. Validate JSON        │
│  2. Rate limit (30/min)  │
│  3. Field validation     │
│  4. License check (exam) │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  Core Intelligence       │
│  (core_intelligence/)    │
│                          │
│  core_step():            │
│  - build_state()         │
│  - choose_action()       │
│  - cognitive_control()   │
│  - calculate_reward()    │
│  - update_q()            │
│  - log_interaction()     │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  Tutor Executor          │
│  (tutor/executor.py)     │
│                          │
│  tutor_execute(action):  │
│  - Format response text  │
│  - Apply action logic    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  Phrasing Filter         │
│  (core_intelligence/)    │
│                          │
│  phrase():               │
│  - Apply style rules     │
│  - Format output         │
└──────┬───────────────────┘
       │
       ▼
       HTTP 200 OK
       {
         "action": "...",
         "message": "...",
         "status": "ok",
         "profile": "...",
         "mode": "..."
       }
       │
       ▼
┌──────────────┐
│ Android App  │
│ Store result │
│ Display UI   │
└──────────────┘
```

---

## Troubleshooting

### Connection Issues

**Problem**: `Connection refused` on emulator
```
Solution: Ensure bridge server is running on host machine
$ python bridge/server.py
# Should print: "Bridge server running on http://127.0.0.1:8001"
```

**Problem**: `Connection timeout` on physical device
```
Solution: 
1. Get host machine IP: ipconfig (Windows) / ifconfig (Mac/Linux)
2. Update BASE_URL in EngineClient.kt: http://<HOST_IP>:8001
3. Ensure firewall allows port 8001
4. Verify device and host are on same WiFi network
```

### Response Issues

**Problem**: Backend returns 429 Too Many Requests
```
Solution: Wait 60 seconds, rate limit is 30 requests/minute per IP
```

**Problem**: 402 Exam mode without license
```
Solution: Set "license_valid": true in request JSON
```

**Problem**: Empty response from engine
```
Solution: Check that all required fields are present and valid
- confidence and weakness must be numeric
- user_input should not be blank
- topic should not exceed 200 characters
```

---

## Testing API Endpoints

### Using cURL
```bash
# Test /process endpoint
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "thermodynamics",
    "user_input": "What is energy conservation?",
    "confidence": 0.55,
    "weakness": 0.45,
    "last_action": "ask_clarification",
    "user_feedback": "ask",
    "mode": "quiz",
    "license_valid": true
  }'

# Test /web-check endpoint
curl -X POST http://localhost:8001/web-check \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/page"
  }'
```

### Using Python requests
```python
import requests
import json

url = "http://localhost:8001/process"
payload = {
    "topic": "thermodynamics",
    "user_input": "What is energy conservation?",
    "confidence": 0.55,
    "weakness": 0.45,
    "last_action": "ask_clarification",
    "user_feedback": "ask",
    "mode": "quiz",
    "license_valid": True
}

response = requests.post(url, json=payload, timeout=6)
print(response.json())
```

---

## Security Considerations

1. **Rate Limiting**: 30 requests/minute per IP prevents abuse
2. **License Validation**: Exam mode requires `license_valid: true`
3. **Input Validation**: 
   - Max topic length: 200 chars
   - Max user_input: 4000 chars
   - Numeric type check for confidence/weakness
4. **Web Access Control**: `/web-check` respects `web_access` setting in control_panel/state.json
5. **Error Safety**: Errors return generic messages to prevent information leakage

---

## Configuration

### Bridge Settings
- **Host**: Configurable (default: 127.0.0.1, change to 0.0.0.0 for network access)
- **Port**: 8001 (hardcoded)
- **Rate Limit**: 30 requests/minute
- **Timeout**: 4000ms connect, 6000ms read

### Application Settings (control_panel/state.json)
```json
{
  "profile": "calm_tutor|strict_examiner",
  "web_access": true|false,
  "llm_enabled": true|false
}
```

---

## Version History

- **v1.0** (Current): Initial HTTP bridge with /process and /web-check endpoints
  - Rate limiting per IP
  - License validation
  - JSON request/response
  - Error handling with specific HTTP codes
