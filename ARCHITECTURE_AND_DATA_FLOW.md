# Chat System Architecture & Data Flow

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ExaminerAI Chat System                      │
└─────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │   Android    │
                            │ Chat Screen  │  ← Beautiful UI
                            │   (Kotlin)   │
                            └──────┬───────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼──────┐  ┌────▼─────┐  ┌───▼────────┐
            │ Send Message │  │ UI State │  │  Display   │
            │              │  │ Management│  │  Response  │
            └───────┬──────┘  └────┬─────┘  └───┬────────┘
                    │              │            │
                    └──────────────┼────────────┘
                                   │ JSON Request
                                   ▼
                    ┌──────────────────────────┐
                    │   Python Backend API     │  ← Call from Kotlin
                    │    LocalHost:8000        │     (HTTP/WebSocket)
                    └──────────────┬───────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   ┌────▼──────────┐  ┌───────────▼──────────┐  ┌──────────▼──┐
   │   Streaming   │  │  Response Quality    │  │  Document   │
   │   Chat Engine │  │     Analyzer         │  │  Generator  │
   │               │  │                      │  │             │
   │ • 5-step      │  │ • 5 dimensions       │  │ • PDF       │
   │   thinking    │  │ • Scoring heuristics │  │ • Word/.docx│
   │ • Ollama      │  │ • Quality levels     │  │ • Batch     │
   │   integration │  │ • Insights/Recs      │  │   export    │
   │ • Streaming   │  │                      │  │             │
   │   events      │  │                      │  │             │
   └────┬──────────┘  └───────────┬──────────┘  └──────────┬──┘
        │                         │                        │
        │ Events: thinking,       │ Quality Dict           │ File path
        │ content, quality,       │ (scores + insights)    │ (PDF/DOCX)
        │ complete                │                        │
        │                         │                        │
        └─────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────▼──────────┐
                    │  Ollama LLM Service    │
                    │  (localhost:11434)     │
                    │  Model: qwen:7b        │
                    └────────────────────────┘
```

## Data Flow: User Asks a Question

### Phase 1: Question Received (100ms)

```
User Input:
"What is Artificial Intelligence?"
         │
         ▼
JavaScript/Kotlin UI sends HTTP POST:
{
  "query": "What is Artificial Intelligence?",
  "conversation_id": "conv_123",
  "include_thinking": true,
  "include_quality": true
}
         │
         ▼
Python Backend Routes to:
StreamingChatEngine.stream_response()
```

### Phase 2: Thinking Process (600ms)

```
StreamingChatEngine receives query
         │
         ▼
_generate_thinking_steps() creates:
{
  "step_number": 1,
  "title": "Question Analysis",
  "reasoning": "Analyzing user query to understand core question...",
  "duration_ms": 145.3
},
{
  "step_number": 2,
  "title": "Intent & Context Detection",
  "reasoning": "User appears to be seeking foundational knowledge...",
  "duration_ms": 234.7
},
... (3 more steps) ...
         │
         ▼
UI STREAMS Event Type: "thinking"
{
  "type": "thinking",
  "step": 1,
  "title": "Question Analysis",
  "reasoning": "Analyzing user query to understand...",
  "duration_ms": 145.3
}
         │
         ▼
Kotlin UI Receives → Displays:
💭 Step 1: Question Analysis
   Analyzing user query to understand core question...
   ⏱ 145.3ms
```

### Phase 3: Response Streaming (2000-3000ms)

```
StreamingChatEngine._stream_from_ollama():
{
  "prompt": "What is Artificial Intelligence? [CONTEXT]",
  "stream": true,
  "model": "qwen:7b"
}
         │
         ▼
Ollama returns streaming response:
"Artificial" → "Intelligence" → "(AI)" → "is" → "a" → ...
         │
         ▼
For each chunk received:
UI STREAMS Event Type: "content"
{
  "type": "content",
  "chunk": "Artificial Intelligence (AI) is a"
}
         │
         ▼
Kotlin UI receives → Appends to message:
Assistant:
Artificial Intelligence (AI) is a [continuing...]
Artificial Intelligence (AI) is a broad field of...
Artificial Intelligence (AI) is a broad field of computer science...
[Response grows character by character in real-time]
```

### Phase 4: Quality Analysis (300ms)

```
Once response complete:
Full Response Buffer =
"Artificial Intelligence (AI) is a broad field of computer science
aimed at creating intelligent machines that can perform tasks that
typically require human intelligence..."
         │
         ▼
ResponseQualityAnalyzer.analyze(response, question)
         │
         ▼
Calculate 5 Scores:
├─ Relevance Score: 0.92
│  (Keyword overlap: "intelligence" × 3, "AI" × 2)
│  (Context match: 92%)
│
├─ Clarity Score: 0.88
│  (Avg sentence length: 16 words - good)
│  (Paragraph structure: Yes)
│  (Formatting: Good)
│
├─ Completeness Score: 0.85
│  (Word count: 285 - excellent for "What is AI?")
│  (Covers definition: Yes)
│  (Covers examples: Yes)
│  (Covers applications: Yes)
│
├─ Accuracy Score: 0.90
│  (Confident language: 90%)
│  (Uncertain hedges: <5%)
│
└─ Engagement Score: 0.87
   (Has examples: Yes +0.15)
   (Has questions: Yes +0.10)
   (Has specific details: Yes +0.12)
         │
         ▼
Generate Quality Report:
{
  "overall_quality_percentage": 88.2,
  "quality_level": "Very Good",
  "relevance_score": 0.92,
  "clarity_score": 0.88,
  "completeness_score": 0.85,
  "accuracy_score": 0.90,
  "engagement_score": 0.87,
  "insights": [
    "Well-structured response with clear examples",
    "Good balance between detail and brevity",
    "Covers multiple aspects of the topic"
  ],
  "recommendations": [
    "Could add more technical depth for advanced users"
  ],
  "characteristics": {
    "has_examples": true,
    "has_structure": true,
    "is_concise": true,
    "tone_appropriate": true,
    "word_count": 285
  }
}
         │
         ▼
UI STREAMS Event Type: "quality"
{
  "type": "quality",
  "metrics": { ... above ... }
}
         │
         ▼
Kotlin UI Receives → Displays:

Response Quality: Very Good (88.2%)
├─ Relevance: ███████████░ 92%
├─ Clarity: ██████████░ 88%
├─ Completeness: █████████░ 85%
├─ Accuracy: ███████████░ 90%
└─ Engagement: ██████████░ 87%

Key Insights:
✓ Well-structured response with clear examples
✓ Good balance between detail and brevity
✓ Covers multiple aspects of the topic
```

### Phase 5: Completion & Export (500ms)

```
StreamingChatEngine finishes:
UI STREAMS Event Type: "complete"
{
  "type": "complete",
  "total_time_ms": 4231,
  "message_id": "msg_1234567"
}
         │
         ▼
Full Message Stored:
ChatMessage(
  id="msg_1234567",
  question="What is Artificial Intelligence?",
  response="Artificial Intelligence (AI) is...",
  thinking_process=[...5 steps...],
  quality_metrics={...85 metrics...},
  timestamp=1234567890
)
         │
         ▼
UI Shows "Ready for Export":
[📄 Export as PDF] [📄 Export as Word]
         │
         ▼
User clicks "Export as PDF"
         │
         ▼
Call: DocumentGenerator.create_pdf_document(message, "response.pdf")
         │
         ▼
PDF Created with:
┌─────────────────────────────────────────────┐
│ Metadata                                    │
├─────────────────────────────────────────────┤
│ Model: qwen:7b-instruct                     │
│ Generated: 2024-01-15 14:32:45              │
│ Quality Score: 88.2% (Very Good)            │
├─────────────────────────────────────────────┤
│ Question                                    │
├─────────────────────────────────────────────┤
│ What is Artificial Intelligence?            │
├─────────────────────────────────────────────┤
│ Thinking Process                            │
├─────────────────────────────────────────────┤
│ Step 1: Question Analysis (145.3ms)         │
│ Analyzing user query to understand...       │
│ ...                                         │
├─────────────────────────────────────────────┤
│ Response                                    │
├─────────────────────────────────────────────┤
│ Artificial Intelligence (AI) is a broad...  │
│ ...                                         │
├─────────────────────────────────────────────┤
│ Quality Analysis                            │
├─────────────────────────────────────────────┤
│ Overall: 88.2% (Very Good)                  │
│ Relevance: 92% | Clarity: 88% | ...         │
│ Insights:                                   │
│ • Well-structured response...               │
│ Recommendations:                            │
│ • Could add more technical depth...         │
└─────────────────────────────────────────────┘
         │
         ▼
File saved to:
exports/response_20240115_143245.pdf
         │
         ▼
UI shows: ✓ PDF saved successfully!
Share button opens file in Mail/Drive/etc
```

## Complete Timeline

```
T=0ms      │ User types and sends "What is AI?"
T=50ms     │ HTTP request reaches Python backend
T=100ms    │ StreamingChatEngine.stream_response() starts
T=150ms    │ Thinking process generated (5 steps, ~1000ms total)
T=1150ms   │ First thinking event sent to UI
T=1200ms   │ First Ollama request sent
T=1250ms   │ First response chunk received
T=1260ms   │ First "content" event sent to UI
T=1300ms   │ Response visible in chat bubble
T=3200ms   │ Response generation complete (~2000 tokens)
T=3300ms   │ Quality analysis complete
T=3350ms   │ "quality" event sent to UI with metrics
T=3400ms   │ Quality dashboard visible above response
T=3450ms   │ "complete" event sent
T=3500ms   │ Chat ready for next question or export
T=3600ms   │ User clicks "Export as PDF"
T=3650ms   │ DocumentGenerator starts PDF creation
T=4100ms   │ PDF fully written to disk
T=4150ms   │ ✓ Export complete notification shown
─────────────────────────────────────
Total Time: ~4.2 seconds (user to readable response with export ready)
```

## Component Interactions

### StreamingChatEngine ↔ ResponseQualityAnalyzer

```
StreamingChatEngine:
  Generate thinking → Yield "thinking" event
  Stream response → Yield "content" events (chunks)
  Response complete → Pass to QualityAnalyzer
                  │
                  ▼
ResponseQualityAnalyzer:
  Analyze(full_response, question)
  Calculate 5 scores
  Generate insights
  Generate recommendations
  Return QualityMetrics dict
                  │
                  ▼
StreamingChatEngine:
  Yield "quality" event with metrics
  Yield "complete" event
```

### StreamingChatEngine ↔ DocumentGenerator

```
ChatScreen (Kotlin):
  User sends question
  Receives message with:
    - response text
    - thinking_process (5 steps)
    - quality_metrics (5 scores)
  
  Stores in memory:
    ChatMessage {
      id, role, content,
      thinking_process,
      quality_metrics
    }
                  │
                  ▼
  User clicks "Export as PDF"
                  │
                  ▼
  Call backend: DocumentGenerator.create_pdf_document(
    {
      user_query,
      response,
      thinking_process,
      quality_metrics,
      model_name,
      timestamp
    },
    filename
  )
                  │
                  ▼
  DocumentGenerator:
    Build PDF with all content
    Add styling and formatting
    Write to disk
    Return file_path
                  │
                  ▼
  ChatScreen:
    Show "✓ PDF created!"
    Offer to share/open
```

## Configuration Points

All components are configurable:

```python
# In core/__init__.py or config:

# Chat streaming
ENABLE_THINKING_PROCESS = True
THINKING_STEPS = 5
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen:7b-instruct"
STREAMING_CHUNK_SIZE = 50  # chars per event

# Quality analysis
QUALITY_SCORING_ENABLED = True
QUALITY_THRESHOLDS = {
    "excellent": 0.90,
    "very_good": 0.80,
    "good": 0.70,
    "acceptable": 0.60,
}

# Document generation
EXPORT_FORMATS = ["pdf", "word"]
EXPORT_INCLUDE_THINKING = True
EXPORT_INCLUDE_METRICS = True
EXPORT_DIRECTORY = "exports/"
```

## Performance Characteristics

```
Operation             │ Typical Time │ Range
─────────────────────┼──────────────┼──────────────
Thinking Generation  │ 1.0s         │ 0.8-1.5s
─────────────────────┼──────────────┼──────────────
Response Streaming*  │ 2.5s         │ 1.0-5.0s
  (*depends on answer length and Ollama speed)
─────────────────────┼──────────────┼──────────────
Quality Analysis     │ 0.2s         │ 0.1-0.3s
─────────────────────┼──────────────┼──────────────
PDF Generation       │ 1.0s         │ 0.5-2.0s
─────────────────────┼──────────────┼──────────────
Word Doc Generation  │ 0.8s         │ 0.3-1.5s
─────────────────────┼──────────────┼──────────────
Full Chat Flow       │ 3.5-5.5s     │ 2.0-8.0s
─────────────────────┼──────────────┼──────────────
```

## Error Handling Flow

```
If Ollama not running:
  StreamingChatEngine.stream_from_ollama()
    → No response from localhost:11434
    → Catch ConnectionError
    → Yield "error" event: "Ollama service unavailable"
    → UI shows: "⚠ LLM not available. Check Ollama is running."
    → Return gracefully

If response too short:
  ResponseQualityAnalyzer.analyze()
    → Detects word_count < 20
    → Completeness_score = 0.3
    → Overall quality drops
    → Recommendations: "Provide more detail"
    → UI shows: "Quality: Needs Improvement (45%)"

If PDF export fails:
  DocumentGenerator.create_pdf_document()
    → reportlab import missing?
    → FilePermissionError on write?
    → Exception caught
    → UI shows: "⚠ Export failed. PDF library may be missing."
```

This architecture ensures:
- ✅ Real-time streaming with visible reasoning
- ✅ Automatic quality verification
- ✅ Professional document export
- ✅ Graceful degradation on failures
- ✅ Modular design for easy customization
