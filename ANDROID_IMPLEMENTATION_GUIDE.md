# Android Implementation Guide: Connecting to Python Bridge

## File Locations
```
android-app/app/src/main/java/com/example/examinerai/
├── EngineClient.kt        ← Network calls to Python bridge
├── PythonService.kt       ← Local fallback when offline
├── QuizScreen.kt          ← Main UI that sends requests
├── InteractionEntity.kt   ← Database schema
├── InteractionDao.kt      ← Database access
├── AppDatabase.kt         ← Room database setup
└── LicenseStore.kt        ← License validation
```

---

## Configuration by Deployment Scenario

### Scenario A: Development (Emulator on Same Machine)

**Step 1: Update EngineClient.kt**
```kotlin
object EngineClient {
    private const val BASE_URL = "http://10.0.2.2:8001"  // ✅ Default for emulator
    
    fun send(request: JSONObject): JSONObject {
        val url = URL("$BASE_URL/process")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.connectTimeout = 4000  // 4 seconds
        conn.readTimeout = 6000     // 6 seconds
        
        OutputStreamWriter(conn.outputStream).use { 
            it.write(request.toString()) 
        }
        
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val responseText = BufferedReader(InputStreamReader(stream)).use { 
            it.readText() 
        }
        
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

**Step 2: Start Python Bridge**
```bash
# On your development machine
cd c:\Users\harpr\examinerai
python bridge/server.py
# Output: Bridge server running on http://127.0.0.1:8001
```

**Step 3: Launch Android Emulator**
- Android Studio → Device Manager → Launch Emulator
- Build and run the ExaminerAI app
- App will connect to `10.0.2.2:8001` (emulator magic alias for host)

**Testing**:
- In QuizScreen, type a question and click Ask
- Should see response from Python engine
- Check QuizScreen logcat: `adb logcat | grep QuizDesk`

---

### Scenario B: Physical Device on Local Network

**Step 1: Find Your Python Host IP**

Windows:
```batch
ipconfig
# Look for "IPv4 Address" under your WiFi adapter, e.g., 192.168.1.100
```

Mac/Linux:
```bash
ifconfig
# Look for inet address on your WiFi interface
```

**Step 2: Update EngineClient.kt**
```kotlin
object EngineClient {
    private const val BASE_URL = "http://192.168.1.100:8001"  // ✅ Replace with your IP
    
    // ... rest of code same
}
```

**Step 3: Start Python Bridge (Network Accessible)**
```bash
# Option A: Auto-detect and bind to all interfaces
python -c "from bridge.server import run; run(host='0.0.0.0', port=8001)"

# Option B: Bind to specific IP
python -c "from bridge.server import run; run(host='192.168.1.100', port=8001)"

# Option C: Manually edit run() call in bridge/server.py
# Find line: server = HTTPServer((host, port), BridgeHandler)
# Change to: server = HTTPServer(('0.0.0.0', 8001), BridgeHandler)
```

**Step 4: Configure Firewall (Windows)**
```
Windows Defender Firewall → Allow an app through firewall
→ Click "Allow another app"
→ Browse to: python.exe (your Python interpreter)
→ Check "Private" (for home/work networks)
```

**Step 5: Verify Network Access**

Windows (from Python machine):
```batch
netstat -ano | find ":8001"
# Should show: LISTENING
```

From Android device:
```bash
# Connect to device via adb
adb shell

# From device shell, test connectivity
curl http://192.168.1.100:8001/process
# If this times out, firewall is blocking or bridge not running
```

**Step 6: Build and Run App**
```bash
# Update build config if needed
cd android-app
./gradlew installDebug

# Or use Android Studio IDE
```

**Manual Testing from Device**:
```bash
adb shell
# On device:
curl -X POST http://192.168.1.100:8001/process \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","user_input":"test?","confidence":0.5,"weakness":0.5,"last_action":"ask","user_feedback":"ask"}'
```

---

### Scenario C: Multiple Devices

**Problem**: Different devices need different IP addresses

**Solution: Environment Configuration**
```kotlin
// EngineClient.kt - Add environment detection
object EngineClient {
    private val BASE_URL = when {
        System.getenv("BRIDGE_URL") != null -> 
            System.getenv("BRIDGE_URL")  // From build config
        Build.MANUFACTURER == "Android Emulator" -> 
            "http://10.0.2.2:8001"  // Emulator
        else -> 
            "http://192.168.1.100:8001"  // Physical device (fallback)
    }
    
    fun send(request: JSONObject): JSONObject {
        // ... same implementation
    }
}
```

**Or use BuildConfig variants**:

`build.gradle` (Module: app):
```gradle
productFlavors {
    emulator {
        buildConfigField "String", "BRIDGE_URL", '"http://10.0.2.2:8001"'
    }
    device {
        buildConfigField "String", "BRIDGE_URL", '"http://192.168.1.100:8001"'
    }
}
```

Then in `EngineClient.kt`:
```kotlin
private const val BASE_URL = BuildConfig.BRIDGE_URL
```

Build for specific flavor:
```bash
./gradlew installEmulatorDebug    # Uses emulator URL
./gradlew installDeviceDebug      # Uses device URL
```

---

## Request Flow in QuizScreen

### 1. User Input (Ask Tab)
```kotlin
// File: QuizScreen.kt, fun submit()

fun submit(input: String, feedback: String, clearEval: Boolean) {
    if (busy) return
    if (input.isBlank()) {
        status = "Please enter text first."
        return
    }
    
    busy = true
    status = "Processing..."
    scope.launch(Dispatchers.IO) {  // Run on background thread
        try {
            // Build request
            val result = processDeskRequest(context, input, lastAction, feedback)
            
            // Extract fields
            val action = result.optString("action", "review")
            val message = result.optString("message", "No response generated.")
            val source = result.optString("_source", "local")
            
            // Calculate reward
            val reward = when {
                feedback == "answered" -> 0.75
                action.contains("ask", true) -> 0.6
                action.contains("explain", true) -> 0.7
                else -> 0.5
            }
            
            // Store in database
            AppDatabase.get(context).interactionDao().insert(
                InteractionEntity(topic = TOPIC, action = action, reward = reward)
            )
            
            // Update UI on main thread
            withContext(Dispatchers.Main) {
                lastAction = action
                response = message
                status = if (source == "backend") 
                    "Connected to backend bridge" 
                else 
                    "Using local fallback"
                if (clearEval) evalText = ""
            }
            refreshStats()
            
        } catch (e: Exception) {
            Log.e(TAG, "Submit failed", e)
            withContext(Dispatchers.Main) {
                status = "Request failed: ${e.message ?: "unknown error"}"
            }
        } finally {
            withContext(Dispatchers.Main) {
                busy = false
            }
        }
    }
}
```

### 2. Process Request (Network Call)
```kotlin
private suspend fun processDeskRequest(
    context: Context,
    userInput: String,
    lastAction: String,
    feedback: String
): JSONObject {
    // Build JSON request
    val req = JSONObject()
        .put("topic", TOPIC)                    // "thermodynamics"
        .put("user_input", userInput)           // User typed text
        .put("confidence", 0.55)                // Learning parameter
        .put("weakness", 0.45)                  // Learning parameter
        .put("last_action", lastAction)         // Previous action
        .put("user_feedback", feedback)         // "ask" or "answered"
        .put("mode", "quiz")                    // Mode
        .put("license_valid", true)             // For exam mode
    
    return try {
        // Try network backend
        EngineClient.send(req).apply { 
            put("_source", "backend") 
        }
    } catch (e: Exception) {
        Log.w(TAG, "Backend unavailable: ${e.message}")
        
        // Fallback to local processing
        PythonService.getInstance(context).processWithEngine(
            topic = TOPIC,
            confidence = 0.55,
            weakness = 0.45,
            lastAction = lastAction,
            userFeedback = feedback,
            profileName = "strict_examiner"
        ).apply { 
            put("_source", "local") 
        }
    }
}
```

### 3. Network Call (EngineClient)
```kotlin
fun send(request: JSONObject): JSONObject {
    val url = URL("$BASE_URL/process")
    val conn = url.openConnection() as HttpURLConnection
    
    try {
        // Setup connection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true
        conn.connectTimeout = 4000  // Don't wait forever
        conn.readTimeout = 6000
        
        // Send request body
        OutputStreamWriter(conn.outputStream).use { writer ->
            writer.write(request.toString())
        }
        
        // Read response
        val code = conn.responseCode
        val stream = if (code in 200..299) 
            conn.inputStream 
        else 
            conn.errorStream
            
        val body = BufferedReader(InputStreamReader(stream)).use { 
            it.readText() 
        }
        
        // Parse response
        return if (code in 200..299) {
            JSONObject(body)
        } else {
            // Network error - return error response
            JSONObject()
                .put("status", "error")
                .put("action", "review")
                .put("message", "Backend returned HTTP $code")
                .put("http_code", code)
        }
        
    } catch (e: SocketTimeoutException) {
        throw Exception("Request timeout: ${e.message}")
    } catch (e: ConnectException) {
        throw Exception("Cannot connect to bridge: ${e.message}")
    } catch (e: IOException) {
        throw Exception("Network error: ${e.message}")
    } finally {
        conn.disconnect()
    }
}
```

---

## Database Storage

### InteractionEntity (Room Database)
```kotlin
@Entity(tableName = "interactions")
data class InteractionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val topic: String,
    val action: String,
    val reward: Double,
    val timestamp: Long = System.currentTimeMillis()
)
```

### Inserting After Response
```kotlin
AppDatabase.get(context).interactionDao().insert(
    InteractionEntity(
        topic = "thermodynamics",
        action = "explain",
        reward = 0.6,
        timestamp = System.currentTimeMillis()
    )
)
```

### Retrieving for Stats
```kotlin
scope.launch(Dispatchers.IO) {
    val all = AppDatabase.get(context).interactionDao().getAll()
    val stats = DeskStats(
        total = all.size,
        avg = if (all.isNotEmpty()) all.map { it.reward }.average() else 0.0,
        best = all.maxOfOrNull { it.reward } ?: 0.0
    )
    withContext(Dispatchers.Main) {
        // Update UI with stats
    }
}
```

---

## License Validation

### LicenseStore.kt
```kotlin
class LicenseStore(private val context: Context) {
    companion object {
        private const val PREF_NAME = "license_prefs"
        private const val KEY_LICENSE = "license_valid"
    }
    
    fun isValid(): Boolean {
        val pref = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return pref.getBoolean(KEY_LICENSE, false)
    }
    
    fun setValid(valid: Boolean) {
        val pref = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        pref.edit { putBoolean(KEY_LICENSE, valid) }
    }
}
```

### Usage in Request
```kotlin
val licenseStore = LicenseStore(context)
val req = JSONObject()
    .put("topic", "physics")
    .put("user_input", "...")
    // ... other fields
    .put("mode", if (isExamMode) "exam" else "quiz")
    .put("license_valid", licenseStore.isValid())  // Set based on license
```

---

## Error Handling Patterns

### Pattern 1: Timeout Recovery
```kotlin
try {
    return EngineClient.send(request)
} catch (e: SocketTimeoutException) {
    Log.w(TAG, "Request timeout, retrying...")
    Thread.sleep(500)  // Wait before retry
    return EngineClient.send(request)  // Retry once
} catch (e: Exception) {
    Log.e(TAG, "Fatal error", e)
    return PythonService.getInstance(context).processWithEngine(...)
}
```

### Pattern 2: Graceful Degradation with User Feedback
```kotlin
val result = try {
    val response = EngineClient.send(request)
    status = "✓ Backend connected"
    response
} catch (e: Exception) {
    Log.w(TAG, "Backend unavailable", e)
    status = "⚠ Using local mode (offline)"
    PythonService.getInstance(context).processWithEngine(...)
}
```

### Pattern 3: Queue Failed Requests
```kotlin
// Define DAO for pending requests
@Dao
interface PendingRequestDao {
    @Insert
    suspend fun insert(request: PendingRequest)
    
    @Query("SELECT * FROM pending_requests")
    suspend fun getAll(): List<PendingRequest>
    
    @Delete
    suspend fun delete(request: PendingRequest)
}

// When network fails
try {
    return EngineClient.send(request)
} catch (e: Exception) {
    // Queue for later
    AppDatabase.get(context).pendingRequestDao().insert(
        PendingRequest(request.toString(), System.currentTimeMillis())
    )
    return PythonService.getInstance(context).processWithEngine(...)
}

// Sync queue when network returns
scope.launch(Dispatchers.IO) {
    val dao = AppDatabase.get(context).pendingRequestDao()
    for (pending in dao.getAll()) {
        try {
            EngineClient.send(JSONObject(pending.body))
            dao.delete(pending)  // Remove from queue on success
        } catch (e: Exception) {
            Log.w(TAG, "Pending request still failed")
        }
    }
}
```

---

## Debugging Network Issues

### Enable Network Traffic Logging
```kotlin
// In Application.onCreate() or MainActivity.onCreate()
val httpClient = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor { msg ->
        Log.d("OkHttp", msg)
    }.setLevel(HttpLoggingInterceptor.Level.BODY))
    .build()
```

### Check Bridge Server Logs
```bash
# Windows
python bridge/server.py 2>&1 | tee bridge.log

# View logs
tail -f bridge.log
```

### Test with curl from Device
```bash
# SSH to emulator or device
adb shell

# Test connectivity
ping 10.0.2.2  # Emulator
ping 192.168.1.100  # Device (replace with your IP)

# Test HTTP connection
curl http://10.0.2.2:8001/process \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","user_input":"test","confidence":0.5,"weakness":0.5,"last_action":"ask","user_feedback":"ask"}'
```

### Monitor Network on PC (tcpdump)
```bash
# Windows (requires Wireshark or WinDump)
# Or use Android Studio Profiler:
# Android Studio → Profiler → Network tab

# Watch bridge traffic (from Python PC)
# netstat -an | find "8001"
```

### Check Logcat
```bash
# Show all logs
adb logcat

# Filter by tag
adb logcat | grep QuizDesk

# Filter by app package
adb logcat --pid=$(adb shell pidof com.example.examinerai)

# Save to file
adb logcat > app.log

# Clear logs
adb logcat -c
```

---

## Performance Optimization

### Reduce Timeout if Network is Fast
```kotlin
conn.connectTimeout = 2000  // 2 seconds instead of 4
conn.readTimeout = 3000     // 3 seconds instead of 6
```

### Use Coroutines for Non-Blocking
```kotlin
// Bad: Blocks UI thread
val result = EngineClient.send(request)  // ❌

// Good: Background thread
scope.launch(Dispatchers.IO) {
    val result = EngineClient.send(request)
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

### Cache Responses
```kotlin
// Simple cache
private val responseCache = mutableMapOf<String, JSONObject>()

fun send(request: JSONObject): JSONObject {
    val key = request.toString()
    responseCache[key]?.let { return it }
    
    val response = actualSend(request)
    responseCache[key] = response
    return response
}
```

### Batch Multiple Requests
```kotlin
// Bad: 5 requests = 5 * 300ms = 1.5s
repeat(5) { askQuestionAndWait() }

// Good: Request all together
val allQuestions = askQuestionsInBatch(5)
```

---

## Manifest Permissions
Ensure AndroidManifest.xml has:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

## Summary

| Scenario | BASE_URL | Command |
|----------|----------|---------|
| Emulator (dev) | `http://10.0.2.2:8001` | `python bridge/server.py` |
| Device (local) | `http://192.168.x.x:8001` | `python -c "from bridge.server import run; run(host='0.0.0.0', port=8001)"` |
| Production | `https://api.example.com:8001` | Docker container on server |

Choose your scenario, update `EngineClient.kt` BASE_URL, start the bridge, and build the app!
