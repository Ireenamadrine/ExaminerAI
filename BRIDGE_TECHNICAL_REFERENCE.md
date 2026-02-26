# Android-Python Bridge: Technical Reference

## Quick Start

### 1. Start the Python Bridge Server
```bash
cd c:\Users\harpr\examinerai
python bridge/server.py
# Output: Bridge server running on http://127.0.0.1:8001
```

### 2. Send Request from Android App (Emulator)
The app automatically uses `http://10.0.2.2:8001` for emulator testing.

### 3. Send Request from Android App (Physical Device)
Update `EngineClient.kt` BASE_URL:
```kotlin
private const val BASE_URL = "http://192.168.1.100:8001"  // Replace with your host IP
```

---

## Real-World Request Examples

### Scenario 1: Student Asking a Question
**Android User Action**: Types "What is thermodynamics?" in Ask tab

**HTTP Request**:
```json
POST /process HTTP/1.1
Host: 10.0.2.2:8001
Content-Type: application/json
Content-Length: 245

{
  "topic": "thermodynamics",
  "user_input": "What is thermodynamics?",
  "confidence": 0.50,
  "weakness": 0.60,
  "last_action": "ask_clarification",
  "user_feedback": "ask",
  "mode": "quiz",
  "license_valid": false
}
```

**Processing Pipeline**:
```
1. bridge/server.py _handle_process()
   ↓ Validates JSON, rate limits, fields
2. core_intelligence/engine.py core_step()
   - build_state(topic, 0.50, 0.60, "ask_clarification")
   - choose_action(state) → returns "explain" (or other based on Q-learning)
   - cognitive_control("explain", 0.50, 0.60, profile)
   - calculate_reward(feedback="ask", action="explain")
   - update_q(state, action, reward, next_state)
3. tutor/executor.py tutor_execute("explain", "thermodynamics", query)
   ↓ Returns: "Thermodynamics is..."
4. core_intelligence/phrasing.py phrase()
   ↓ Final formatted response
5. Return HTTP 200 with result
```

**HTTP Response** (200 OK):
```json
{
  "action": "explain",
  "message": "Thermodynamics is the branch of physics that deals with heat, temperature, and energy transfer. It has four fundamental laws...",
  "status": "ok",
  "profile": "calm_tutor",
  "mode": "quiz"
}
```

**Android Display**:
- QuizScreen shows message in response area
- Stores interaction in Room database:
  - `topic`: "thermodynamics"
  - `action`: "explain"
  - `reward`: 0.6 (calculated)
- Updates stats (total interactions, average reward, best reward)

---

### Scenario 2: Student Submitting an Answer
**Android User Action**: Types answer in Evaluation tab

**HTTP Request**:
```json
POST /process HTTP/1.1
Host: 10.0.2.2:8001
Content-Type: application/json
Content-Length: 292

{
  "topic": "thermodynamics",
  "user_input": "Energy cannot be created or destroyed, only transformed from one form to another.",
  "confidence": 0.70,
  "weakness": 0.40,
  "last_action": "explain",
  "user_feedback": "answered",
  "mode": "quiz",
  "license_valid": true
}
```

**Processing**:
- confidence increased from 0.50 → 0.70 (user learning)
- weakness decreased from 0.60 → 0.40 (improving strength)
- last_action is what we took ("explain")
- user_feedback is their response ("answered" = correct)

**Response** (200 OK):
```json
{
  "action": "ask_clarification",
  "message": "Which part of thermodynamics would you like to explore deeper - the laws, heat transfer, or entropy?",
  "status": "ok",
  "profile": "strict_examiner",
  "mode": "quiz"
}
```

**Android**: 
- Clears evaluation text
- Shows follow-up question
- Logs interaction with `reward: 0.75` (user answered correctly)

---

### Scenario 3: Web Content Extraction
**Android User Action**: Clicks "Browse Web" for thermodynamics

**HTTP Request**:
```json
POST /web-check HTTP/1.1
Host: 10.0.2.2:8001
Content-Type: application/json
Content-Length: 68

{
  "url": "https://en.wikipedia.org/wiki/Thermodynamics"
}
```

**Backend Processing** (bridge/server.py `_handle_web_check`):
1. Check `control_panel/state.json` web_access setting
2. Fetch HTML from URL
3. Extract main text via web_check/extractor.py
4. Return cleaned text

**Response** (200 OK):
```json
{
  "url": "https://en.wikipedia.org/wiki/Thermodynamics",
  "text": "Thermodynamics is a branch of classical physics concerned with heat and temperature and their relation to energy and work. The behavior of these quantities is governed by the four laws of thermodynamics, irrespective of the composition or specific properties of the matter or radiation considered...",
  "status": "ok"
}
```

**Error Response** (403 Forbidden - web access disabled):
```json
{
  "error": "Web access disabled"
}
```

---

## Action-to-Response Mapping

### Action: `explain`
- **Trigger**: User has medium-low confidence, needs full answer
- **Execution**: `tutor_execute("explain", topic, content)`
- **Output**: Full detailed explanation
- **Example Response**: "Thermodynamics is the branch of physics that deals with heat, temperature, and energy transfer..."

### Action: `explain_step_by_step`
- **Trigger**: User is struggling (low confidence, high weakness)
- **Execution**: Breaks content into 5 steps
- **Output**: "Step 1: ... Step 2: ... Step 3: ..."
- **Code Example**:
```python
def step_by_step_explanation(content):
    steps = [step.strip() for step in content.split(".") if step.strip()]
    return "\n".join(f"Step {index + 1}: {step}" for index, step in enumerate(steps[:5]))
```

### Action: `ask_clarification`
- **Trigger**: Ambiguous query or unclear what user needs
- **Execution**: `f"Which part of {topic} is confusing you?"`
- **Output**: Question asking for clarification
- **Example**: "Which part of thermodynamics is confusing you?"

### Action: `be_concise`
- **Trigger**: User has high confidence, needs quick answer
- **Execution**: First sentence only
- **Output**: Single-sentence direct answer
- **Example**: "Energy cannot be created or destroyed, only transformed."

### Action: `refuse`
- **Trigger**: User has very low confidence (<0.2) and action is "explain"
- **Execution**: Safety guard prevents wrong explanations
- **Output**: "I do not have enough verified information..."
- **Policy**: `core_intelligence/policy.py policy_guard()`

### Action: `stay_silent`
- **Trigger**: User demonstrates mastery, continue independently
- **Execution**: Encouragement message
- **Output**: "You seem comfortable with this topic. Let's move on."

---

## State Management

### State JSON (control_panel/state.json)
```json
{
  "profile": "calm_tutor",      // or "strict_examiner"
  "web_access": false,           // Allow /web-check requests
  "llm_enabled": false           // Future LLM integration
}
```

### Database Storage (After Each Interaction)
```kotlin
// Room Database (Android)
InteractionEntity(
  topic = "thermodynamics",
  action = "explain",
  reward = 0.6,
  timestamp = System.currentTimeMillis()
)
```

### Q-Learning Database (Python)
```sql
-- data/intelligence.db
CREATE TABLE q_table (
  state TEXT NOT NULL,
  action TEXT NOT NULL,
  q_value REAL,
  PRIMARY KEY (state, action)
);
```

**Actions in Q-Learning**:
```python
ACTIONS = [
    "explain",
    "explain_step_by_step",
    "ask_clarification",
    "refuse",
    "be_concise",
    "stay_silent",
]
```

**Q-Learning Parameters**:
- `ALPHA = 0.3` - Learning rate (how much new experience influences decisions)
- `GAMMA = 0.8` - Future reward discount (weight future rewards)
- `EPSILON = 0.2` - Exploration rate (20% random action selection)

---

## Learning Profiles

### Profile 1: calm_tutor
- More explanation → higher verbosity
- Gentle feedback
- Used for learning mode

### Profile 2: strict_examiner
- Action: ask_clarification early
- Be concise when appropriate
- Used for exam/quiz mode

**Profile Loading**:
```python
# architecture/profiles.py
profile = get_profile(profile_name)  # Returns profile config
profile = get_current_profile()      # Returns currently active profile
```

---

## Network Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT MACHINE                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Python Backend (Windows/Mac/Linux)                      │  │
│  │                                                          │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ bridge/server.py                                    │ │  │
│  │  │ - HTTPServer on 127.0.0.1:8001                     │ │  │
│  │  │ - HTTP POST /process                               │ │  │
│  │  │ - HTTP POST /web-check                             │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │         ↓ (delegates to)                                  │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ core_intelligence/                                 │ │  │
│  │  │ - engine.py (core_step)                            │ │  │
│  │  │ - q_learning.py (choose_action)                    │ │  │
│  │  │ - rewards.py (calculate_reward)                    │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │         ↓ (executes via)                                  │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ tutor/executor.py                                  │ │  │
│  │  │ - tutor_execute(action)                            │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                           ↑↓ HTTP
            ┌──────────────────────────────────────┐
            │  ANDROID DEVICE / EMULATOR           │
            │                                      │
            │  ┌──────────────────────────────────┐│
            │  │ QuizScreen.kt                    ││
            │  │                                  ││
            │  │ 1. User input (Ask, Evaluate)   ││
            │  │ 2. Build JSONObject request     ││
            │  │ 3. Call EngineClient.send()    ││
            │  │ 4. Parse response               ││
            │  │ 5. Display message              ││
            │  │ 6. Store in Room DB             ││
            │  └──────────────────────────────────┘│
            │                                      │
            │  ┌──────────────────────────────────┐│
            │  │ EngineClient.kt                  ││
            │  │                                  ││
            │  │ Emulator:                        ││
            │  │ BASE_URL = http://10.0.2.2:8001 ││
            │  │                                  ││
            │  │ Device:                          ││
            │  │ BASE_URL = http://192.168.1.x:8001 ││
            │  │                                  ││
            │  │ POST /process                    ││
            │  │ Timeout: 4s connect, 6s read     ││
            │  │ Fallback to PythonService        ││
            │  └──────────────────────────────────┘│
            │                                      │
            │  ┌──────────────────────────────────┐│
            │  │ Room Database (SQLCipher)        ││
            │  │ - InteractionEntity              ││
            │  │ - topic, action, reward          ││
            │  └──────────────────────────────────┘│
            └──────────────────────────────────────┘
```

---

## Connection Modes

### Mode 1: Emulator + Local Bridge
```
Android Emulator (same machine)
    ↓
http://10.0.2.2:8001
    ↓
Python Server (localhost:8001)
```
**Start bridge**:
```bash
python bridge/server.py
```

### Mode 2: Physical Device + Network Bridge
```
Android Device (on WiFi)
    ↓
http://192.168.1.100:8001  (Replace with your IP)
    ↓
Python Server (with firewall open on port 8001)
```
**Start bridge (network accessible)**:
```bash
# Option 1: Use 0.0.0.0 for all interfaces
python -c "from bridge.server import run; run(host='0.0.0.0', port=8001)"

# Option 2: Specify host IP
python -c "from bridge.server import run; run(host='192.168.1.100', port=8001)"
```

### Mode 3: Fallback to Local
If network request fails:
```kotlin
return try {
    EngineClient.send(req)  // Try network
} catch (e: Exception) {
    PythonService.getInstance(context).processWithEngine(...)  // Fallback to local
}
```

---

## Request Lifecycle with Timing

```
T0: Android sends POST /process
    Content: JSON with topic, user_input, confidence, weakness, etc.
    
T0-4ms: Connect timeout (connection attempted)
T4-6000ms: Wait for response
    
T_n: Bridge receives request
    └─ _rate_limited(client_ip)? (instant)
    └─ _read_json() - parse (instant)
    └─ Validate required fields (instant)
    └─ core_step() - engine processing (~50-200ms)
    └─ tutor_execute() - action execution (~10-50ms)
    └─ phrase() - output formatting (~10-20ms)
    └─ _write_json() - response serialization (instant)
    
T_response: Android receives HTTP 200 + JSON payload
    └─ Parse response (~3-10ms)
    └─ Update UI (instant)
    └─ Store in database (5-20ms)
    
Total Latency: ~100-300ms typical (network delay included)
```

---

## Error Recovery Strategies

### Strategy 1: Automatic Retry
```kotlin
fun sendWithRetry(request: JSONObject, maxRetries: Int = 2): JSONObject {
    repeat(maxRetries) { attempt ->
        try {
            return EngineClient.send(request)
        } catch (e: Exception) {
            if (attempt == maxRetries - 1) throw e
            Thread.sleep(500)  // Wait before retry
        }
    }
    throw Exception("Max retries exceeded")
}
```

### Strategy 2: Graceful Degradation
```kotlin
val result = try {
    EngineClient.send(request)  // Try network
} catch (e: Exception) {
    PythonService.getInstance(context).processWithEngine(...)  // Local fallback
}
val source = result.optString("_source", "unknown")
status = if (source == "backend") "Connected" else "Offline mode"
```

### Strategy 3: Queue & Sync
```kotlin
// If offline, queue the request
if (networkUnavailable) {
    AppDatabase.get(context).pendingRequestDao().insert(request)
    showMessage("Saved for later sync")
}

// Later, when online
for (pending in pendingRequests) {
    try {
        val response = EngineClient.send(pending)
        pendingRequestDao().delete(pending)
    } catch (e: Exception) {
        // Stay queued
    }
}
```

---

## Performance Metrics

### Typical Response Times (Emulator)
- Network roundtrip: ~20-50ms
- Engine processing: ~50-200ms
- Total: ~100-300ms

### Typical Response Times (Device on same network)
- Network roundtrip: ~50-150ms
- Engine processing: ~50-200ms
- Total: ~150-400ms

### Rate Limiting Impact
- Limit: 30 requests/minute = 1 request/2 seconds
- Burst: Can do 1 request immediately, then throttled

### Database Impact
- Room DB insert: ~5-20ms per interaction
- Query all interactions: ~10-50ms

---

## JSON Validation Examples

### Valid Request
```json
{
  "topic": "photosynthesis",
  "user_input": "What are the light reactions?",
  "confidence": 0.65,
  "weakness": 0.35,
  "last_action": "explain",
  "user_feedback": "ask",
  "mode": "tutor",
  "license_valid": false
}
```

### Invalid: Missing field
```json
{
  "topic": "photosynthesis",
  "user_input": "What are the light reactions?",
  "confidence": 0.65,
  // Missing: weakness, last_action, user_feedback
  "mode": "tutor"
}
// Response: 400 {"error": "Missing fields"}
```

### Invalid: Bad numeric
```json
{
  "topic": "photosynthesis",
  "user_input": "What are the light reactions?",
  "confidence": "0.65",  // Should be number, not string
  "weakness": 0.35,
  "last_action": "explain",
  "user_feedback": "ask"
}
// Response: 400 {"error": "Confidence/weakness must be numbers"}
```

### Invalid: Input too long
```json
{
  "topic": "photosynthesis",
  "user_input": "[4000+ character string]",  // Exceeds 4000 char limit
  "confidence": 0.65,
  "weakness": 0.35,
  "last_action": "explain",
  "user_feedback": "ask"
}
// Response: 413 {"error": "Input too long"}
```

### Invalid: Exam mode without license
```json
{
  "topic": "photosynthesis",
  "user_input": "What are the light reactions?",
  "confidence": 0.65,
  "weakness": 0.35,
  "last_action": "explain",
  "user_feedback": "ask",
  "mode": "exam",
  "license_valid": false  // Must be true for exam mode
}
// Response: 402 {"error": "Exam mode requires activation"}
```

---

## Advanced: Direct Python Testing

```python
#!/usr/bin/env python3
"""Test bridge directly without Android app"""

import json
import requests

BASE_URL = "http://localhost:8001"

def test_process():
    payload = {
        "topic": "thermodynamics",
        "user_input": "What is entropy?",
        "confidence": 0.60,
        "weakness": 0.40,
        "last_action": "ask_clarification",
        "user_feedback": "ask",
        "mode": "quiz",
        "license_valid": True,
    }
    
    response = requests.post(f"{BASE_URL}/process", json=payload, timeout=6)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_web_check():
    payload = {
        "url": "https://en.wikipedia.org/wiki/Entropy"
    }
    
    response = requests.post(f"{BASE_URL}/web-check", json=payload, timeout=6)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"URL: {data['url']}")
        print(f"Text (first 200 chars): {data['text'][:200]}...")
    else:
        print(f"Error: {response.json()}")

def test_rate_limiting():
    """Test rate limiting by sending 31 requests"""
    payload = {
        "topic": "test",
        "user_input": "test",
        "confidence": 0.5,
        "weakness": 0.5,
        "last_action": "ask_clarification",
        "user_feedback": "ask",
    }
    
    for i in range(35):
        response = requests.post(f"{BASE_URL}/process", json=payload, timeout=6)
        print(f"Request {i+1}: HTTP {response.status_code}")
        if response.status_code == 429:
            print("Rate limit exceeded (expected)")
            break

if __name__ == "__main__":
    print("=== Test /process endpoint ===")
    test_process()
    print("\n=== Test /web-check endpoint ===")
    test_web_check()
    print("\n=== Test rate limiting ===")
    test_rate_limiting()
```

Run this with:
```bash
pip install requests
python test_bridge.py
```
