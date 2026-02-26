# Complete Integration Example

## Full Working Example: Chat + Streaming + Quality + Export

### Step 1: Create Chat ViewModel

```kotlin
// ui/viewmodels/ChatViewModel.kt
package com.example.examinerai.ui.viewmodels

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.examinerai.data.ChatMessage
import com.example.examinerai.data.ThinkingStep
import com.example.examinerai.data.QualityMetrics
import com.example.examinerai.network.ChatApiService
import kotlinx.coroutines.launch

class ChatViewModel : ViewModel() {
    
    // Chat messages list
    private val _messages = mutableStateListOf<ChatMessage>()
    val messages: List<ChatMessage> = _messages
    
    // Current input
    private val _currentInput = mutableStateOf("")
    val currentInput = _currentInput
    
    // Loading state
    private val _isLoading = mutableStateOf(false)
    val isLoading = _isLoading
    
    // Error state
    private val _error = mutableStateOf<String?>(null)
    val error = _error
    
    // API service
    private val apiService = ChatApiService()
    
    // Send a message and stream response
    fun sendMessage(query: String) {
        if (query.isBlank()) return
        
        // Clear input
        _currentInput.value = ""
        
        // Add user message
        _messages.add(ChatMessage(
            id = "msg_user_${System.currentTimeMillis()}",
            role = "user",
            content = query,
            timestamp = System.currentTimeMillis()
        ))
        
        // Set loading
        _isLoading.value = true
        _error.value = null
        
        // Stream response
        viewModelScope.launch {
            try {
                val assistantMessage = ChatMessage(
                    id = "msg_assistant_${System.currentTimeMillis()}",
                    role = "assistant",
                    content = "",
                    timestamp = System.currentTimeMillis(),
                    thinkingProcess = mutableListOf(),
                    qualityMetrics = null
                )
                
                _messages.add(assistantMessage)
                val messageIndex = _messages.size - 1
                
                // Stream from backend
                apiService.streamChat(query) { event ->
                    when (event["type"]) {
                        "thinking" -> {
                            val step = ThinkingStep(
                                stepNumber = event["step"] as Int,
                                title = event["title"] as String,
                                reasoning = event["reasoning"] as String,
                                durationMs = (event["duration_ms"] as Number).toFloat()
                            )
                            
                            assistantMessage.thinkingProcess?.add(step)
                            _messages[messageIndex] = assistantMessage.copy()
                        }
                        
                        "content" -> {
                            val chunk = event["chunk"] as String
                            assistantMessage.content += chunk
                            _messages[messageIndex] = assistantMessage.copy()
                        }
                        
                        "quality" -> {
                            @Suppress("UNCHECKED_CAST")
                            val metricsMap = event["metrics"] as Map<String, Any>
                            
                            assistantMessage.qualityMetrics = QualityMetrics(
                                overallQualityPercentage = (metricsMap["overall_quality_percentage"] as Number).toFloat(),
                                qualityLevel = metricsMap["quality_level"] as String,
                                relevanceScore = (metricsMap["relevance_score"] as Number).toFloat(),
                                clarityScore = (metricsMap["clarity_score"] as Number).toFloat(),
                                completenessScore = (metricsMap["completeness_score"] as Number).toFloat(),
                                accuracyScore = (metricsMap["accuracy_score"] as Number).toFloat(),
                                engagementScore = (metricsMap["engagement_score"] as Number).toFloat(),
                                insights = (metricsMap["insights"] as? List<String>) ?: emptyList(),
                                recommendations = (metricsMap["recommendations"] as? List<String>) ?: emptyList(),
                                wordCount = (metricsMap["word_count"] as? Number)?.toInt() ?: 0
                            )
                            
                            _messages[messageIndex] = assistantMessage.copy()
                        }
                        
                        "complete" -> {
                            _isLoading.value = false
                        }
                        
                        "error" -> {
                            _error.value = event["message"] as String
                            _isLoading.value = false
                        }
                    }
                }
            } catch (e: Exception) {
                _error.value = "Error: ${e.message}"
                _isLoading.value = false
            }
        }
    }
    
    // Export current message as PDF
    fun exportCurrentMessageAsPdf() {
        if (_messages.isEmpty()) return
        
        val lastMessage = _messages.last()
        if (lastMessage.role != "assistant") return
        
        viewModelScope.launch {
            try {
                val pdfPath = apiService.exportToPdf(
                    lastMessage.toExportDto()
                )
                _error.value = "✓ Exported to: $pdfPath"
            } catch (e: Exception) {
                _error.value = "Export failed: ${e.message}"
            }
        }
    }
    
    // Export as Word document
    fun exportCurrentMessageAsWord() {
        if (_messages.isEmpty()) return
        
        val lastMessage = _messages.last()
        if (lastMessage.role != "assistant") return
        
        viewModelScope.launch {
            try {
                val docPath = apiService.exportToWord(
                    lastMessage.toExportDto()
                )
                _error.value = "✓ Exported to: $docPath"
            } catch (e: Exception) {
                _error.value = "Export failed: ${e.message}"
            }
        }
    }
    
    // Update input
    fun updateInput(newInput: String) {
        _currentInput.value = newInput
    }
    
    // Clear chat
    fun clearChat() {
        _messages.clear()
        _error.value = null
    }
}
```

### Step 2: Create Data Models

```kotlin
// data/ChatMessage.kt
package com.example.examinerai.data

data class ChatMessage(
    val id: String,
    val role: String,  // "user" or "assistant"
    var content: String,
    val timestamp: Long,
    val thinkingProcess: MutableList<ThinkingStep>? = null,
    var qualityMetrics: QualityMetrics? = null
) {
    fun toExportDto(): ChatExportDto {
        return ChatExportDto(
            userQuery = if (role == "user") content else "",
            response = if (role == "assistant") content else "",
            thinkingProcess = thinkingProcess?.map {
                mapOf(
                    "step_number" to it.stepNumber,
                    "title" to it.title,
                    "reasoning" to it.reasoning,
                    "duration_ms" to it.durationMs
                )
            } ?: emptyList(),
            qualityMetrics = qualityMetrics?.toMap() ?: emptyMap(),
            model = "qwen:7b-instruct",
            timestamp = System.currentTimeMillis()
        )
    }
}

data class ThinkingStep(
    val stepNumber: Int,
    val title: String,
    val reasoning: String,
    val durationMs: Float
)

data class QualityMetrics(
    val overallQualityPercentage: Float,
    val qualityLevel: String,
    val relevanceScore: Float,
    val clarityScore: Float,
    val completenessScore: Float,
    val accuracyScore: Float,
    val engagementScore: Float,
    val insights: List<String>,
    val recommendations: List<String>,
    val wordCount: Int
) {
    fun toMap(): Map<String, Any> = mapOf(
        "overall_quality_percentage" to overallQualityPercentage,
        "quality_level" to qualityLevel,
        "relevance_score" to relevanceScore,
        "clarity_score" to clarityScore,
        "completeness_score" to completenessScore,
        "accuracy_score" to accuracyScore,
        "engagement_score" to engagementScore,
        "insights" to insights,
        "recommendations" to recommendations,
        "word_count" to wordCount
    )
}

data class ChatExportDto(
    val userQuery: String,
    val response: String,
    val thinkingProcess: List<Map<String, Any>>,
    val qualityMetrics: Map<String, Any>,
    val model: String,
    val timestamp: Long
)
```

### Step 3: Create Chat API Service

```kotlin
// network/ChatApiService.kt
package com.example.examinerai.network

import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class ChatApiService {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()
    
    private val baseUrl = "http://localhost:8000"  // Python backend
    
    // Stream chat response
    fun streamChat(
        query: String,
        onEvent: (Map<String, Any>) -> Unit
    ) {
        val payload = JSONObject().apply {
            put("query", query)
            put("conversation_id", "conv_${System.currentTimeMillis()}")
            put("include_thinking", true)
            put("include_quality", true)
        }
        
        val request = Request.Builder()
            .url("$baseUrl/api/chat/stream")
            .post(payload.toString().toRequestBody())
            .build()
        
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                onEvent(mapOf(
                    "type" to "error",
                    "message" to "Backend error: ${response.code}"
                ))
                return@use
            }
            
            response.body?.source()?.use { source ->
                while (!source.exhausted()) {
                    val line = source.readUtf8Line() ?: continue
                    if (line.isEmpty()) continue
                    
                    // Parse SSE format: data: {...json...}
                    if (line.startsWith("data: ")) {
                        try {
                            val json = JSONObject(line.substring(6))
                            val event = json.toMap()
                            onEvent(event)
                        } catch (e: Exception) {
                            // Skip malformed events
                        }
                    }
                }
            }
        }
    }
    
    // Export to PDF
    suspend fun exportToPdf(data: ChatExportDto): String {
        val payload = JSONObject().apply {
            put("user_query", data.userQuery)
            put("response", data.response)
            put("thinking_process", JSONObject().apply {
                data.thinkingProcess.forEach {
                    put("thinking", it)
                }
            })
            put("quality_metrics", JSONObject(data.qualityMetrics))
            put("model", data.model)
            put("timestamp", data.timestamp)
        }
        
        val request = Request.Builder()
            .url("$baseUrl/api/export/pdf")
            .post(payload.toString().toRequestBody())
            .build()
        
        return client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Export failed")
            
            val json = JSONObject(response.body?.string() ?: "{}")
            json.getString("file_path")
        }
    }
    
    // Export to Word
    suspend fun exportToWord(data: ChatExportDto): String {
        val payload = JSONObject().apply {
            put("user_query", data.userQuery)
            put("response", data.response)
            put("thinking_process", JSONObject())
            put("quality_metrics", JSONObject(data.qualityMetrics))
            put("model", data.model)
        }
        
        val request = Request.Builder()
            .url("$baseUrl/api/export/word")
            .post(payload.toString().toRequestBody())
            .build()
        
        return client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Export failed")
            
            val json = JSONObject(response.body?.string() ?: "{}")
            json.getString("file_path")
        }
    }
}

// Helper extension
fun JSONObject.toMap(): Map<String, Any> {
    val map = mutableMapOf<String, Any>()
    keys().forEach { key ->
        map[key] = get(key)
    }
    return map
}
```

### Step 4: Create Chat UI Screen

```kotlin
// ui/screens/ChatScreen.kt
package com.example.examinerai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.examinerai.data.ChatMessage
import com.example.examinerai.ui.viewmodels.ChatViewModel

@Composable
fun ChatScreenWithIntegration(
    viewModel: ChatViewModel = viewModel()
) {
    val messages = viewModel.messages
    val isLoading = viewModel.isLoading
    val currentInput = viewModel.currentInput
    val error = viewModel.error
    val listState = rememberLazyListState()
    
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
    ) {
        // Header
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            color = Color(0xFF1976D2),
            shape = RoundedCornerShape(8.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text(
                    "ExaminerAI Chat",
                    fontSize = 24.sp,
                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    "Powered by Qwen 2.5 • Streaming Enabled",
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.8f)
                )
            }
        }
        
        // Messages
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            state = listState,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(messages) { message ->
                ChatMessageBox(message)
            }
            
            if (isLoading.value) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(8.dp)
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }
            }
        }
        
        // Error message
        if (error.value != null) {
            Text(
                error.value ?: "",
                color = if (error.value?.startsWith("✓") == true) 
                    Color(0xFF4CAF50) else Color.Red,
                fontSize = 12.sp,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp)
            )
        }
        
        Divider()
        
        // Input
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextField(
                value = currentInput.value,
                onValueChange = { viewModel.updateInput(it) },
                modifier = Modifier
                    .weight(1f)
                    .heightIn(min = 50.dp),
                placeholder = { Text("Ask a question...") },
                shape = RoundedCornerShape(8.dp),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(
                    onSend = {
                        viewModel.sendMessage(currentInput.value)
                    }
                ),
                enabled = !isLoading.value,
                singleLine = false
            )
            
            IconButton(
                onClick = {
                    viewModel.sendMessage(currentInput.value)
                },
                enabled = !isLoading.value
            ) {
                Icon(
                    Icons.Default.Send,
                    "Send",
                    tint = Color(0xFF1976D2)
                )
            }
        }
        
        // Export buttons
        if (messages.isNotEmpty() && messages.last().role == "assistant") {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = { viewModel.exportCurrentMessageAsPdf() },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF1976D2)
                    )
                ) {
                    Text("📄 PDF")
                }
                
                Button(
                    onClick = { viewModel.exportCurrentMessageAsWord() },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF0D47A1)
                    )
                ) {
                    Text("📄 Word")
                }
            }
        }
    }
}

@Composable
fun ChatMessageBox(message: ChatMessage) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (message.role == "user") 
            Alignment.End else Alignment.Start
    ) {
        // Thinking process (assistant only)
        if (message.role == "assistant" && message.thinkingProcess?.isNotEmpty() == true) {
            var expandedThinking by remember { mutableStateOf(false) }
            
            Surface(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .background(Color(0xFFE0F7FA), RoundedCornerShape(8.dp)),
                color = Color.Transparent
            ) {
                Column(
                    modifier = Modifier.padding(8.dp)
                ) {
                    Text(
                        "💭 ${if (expandedThinking) "▼" else "▶"} Thinking Process",
                        fontSize = 12.sp,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                        modifier = Modifier
                            .clickable { expandedThinking = !expandedThinking }
                    )
                    
                    if (expandedThinking) {
                        message.thinkingProcess?.forEach { step ->
                            Text(
                                "Step ${step.stepNumber}: ${step.title} (${step.durationMs.toInt()}ms)",
                                fontSize = 11.sp,
                                color = Color(0xFF00796B),
                                modifier = Modifier.padding(top = 4.dp)
                            )
                        }
                    }
                }
            }
        }
        
        // Message bubble
        Surface(
            modifier = Modifier
                .fillMaxWidth(0.85f)
                .padding(vertical = 4.dp),
            color = if (message.role == "user") 
                Color(0xFF1976D2) else Color.White,
            shape = RoundedCornerShape(8.dp)
        ) {
            Text(
                message.content,
                color = if (message.role == "user") 
                    Color.White else Color.Black,
                fontSize = 14.sp,
                modifier = Modifier.padding(12.dp)
            )
        }
        
        // Quality metrics (assistant only)
        if (message.role == "assistant" && message.qualityMetrics != null) {
            var expandedQuality by remember { mutableStateOf(false) }
            
            val qm = message.qualityMetrics!!
            
            Surface(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .background(Color(0xFFF1F8E9), RoundedCornerShape(8.dp)),
                color = Color.Transparent
            ) {
                Column(
                    modifier = Modifier.padding(8.dp)
                ) {
                    Text(
                        "✓ Quality: ${qm.qualityLevel} (${qm.overallQualityPercentage.toInt()}%) " +
                        if (expandedQuality) "▼" else "▶",
                        fontSize = 12.sp,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                        color = Color(0xFF558B2F),
                        modifier = Modifier
                            .clickable { expandedQuality = !expandedQuality }
                    )
                    
                    if (expandedQuality) {
                        Column(modifier = Modifier.padding(top = 8.dp)) {
                            QualityMetricRow("Relevance", qm.relevanceScore)
                            QualityMetricRow("Clarity", qm.clarityScore)
                            QualityMetricRow("Completeness", qm.completenessScore)
                            QualityMetricRow("Accuracy", qm.accuracyScore)
                            QualityMetricRow("Engagement", qm.engagementScore)
                            
                            if (qm.insights.isNotEmpty()) {
                                Text(
                                    "Insights:",
                                    fontSize = 11.sp,
                                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                                    modifier = Modifier.padding(top = 8.dp)
                                )
                                qm.insights.forEach { insight ->
                                    Text(
                                        "• $insight",
                                        fontSize = 10.sp,
                                        color = Color(0xFF558B2F)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun QualityMetricRow(label: String, score: Float) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(label, fontSize = 11.sp, modifier = Modifier.width(80.dp))
        
        // Progress bar
        Box(
            modifier = Modifier
                .weight(1f)
                .height(8.dp)
                .background(Color.LightGray, RoundedCornerShape(4.dp))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(score)
                    .background(
                        color = when {
                            score >= 0.85f -> Color(0xFF4CAF50)
                            score >= 0.75f -> Color(0xFFFFC107)
                            else -> Color(0xFFF44336)
                        },
                        shape = RoundedCornerShape(4.dp)
                    )
            )
        }
        
        Text(
            "${(score * 100).toInt()}%",
            fontSize = 10.sp,
            modifier = Modifier.width(30.dp)
        )
    }
}

// Preview
@Preview
@Composable
fun ChatScreenPreview() {
    ChatScreenWithIntegration()
}
```

### Step 5: Add to Navigation

```kotlin
// navigation/ExamineraiNavigation.kt
@Composable
fun ExamineraiNavigation() {
    val navController = rememberNavController()
    
    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(navController)
        }
        
        // ADD THIS:
        composable("chat") {
            ChatScreenWithIntegration()
        }
        
        composable("dashboard") {
            DashboardScreen(navController)
        }
    }
}
```

### Step 6: Add to MainActivity

```kotlin
// MainActivity.kt
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    setContent {
        ExamineraiTheme {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.background
            ) {
                ExamineraiNavigation()  // This now includes chat
            }
        }
    }
}
```

### Step 7: Python Backend Setup

Create `main_chat.py` in your Python backend:

```python
# main_chat.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
from core.chat_streaming import StreamingChatEngine
from core.response_quality import ResponseQualityAnalyzer
from core.document_generator import DocumentGenerator

app = FastAPI()

engine = StreamingChatEngine()
quality_analyzer = ResponseQualityAnalyzer()
doc_generator = DocumentGenerator()

@app.post("/api/chat/stream")
async def stream_chat(request: dict):
    """Stream chat response with thinking and quality metrics"""
    query = request.get("query", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query required")
    
    def event_generator():
        for event in engine.stream_response(query):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/export/pdf")
async def export_pdf(data: dict):
    """Export response as PDF"""
    try:
        path = doc_generator.create_pdf_document(data, f"response_{int(time.time())}.pdf")
        return {"file_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/word")
async def export_word(data: dict):
    """Export response as Word document"""
    try:
        path = doc_generator.create_word_document(data, f"response_{int(time.time())}.docx")
        return {"file_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Run Everything

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Python backend
cd c:\Users\harpr\examinerai
python main_chat.py

# Terminal 3: Android
cd android-app
./gradlew.bat assembleDebug

# OR run on device with Android Studio
```

### Test the Integration

1. **Start typing** in chat
2. **See thinking process** expand as it streams
3. **Watch response** appear character by character
4. **View quality metrics** appear after response
5. **Click "Export PDF"** or **"Export Word"**
6. **Find files** in `exports/` folder

**That's it!** You now have a complete ChatGPT-style chat system. 🎉
