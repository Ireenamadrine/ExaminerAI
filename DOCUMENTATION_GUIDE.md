# ExaminerAI Bridge Documentation: Navigation Guide

Welcome! I've created comprehensive documentation for your Android-Python bridge system. This guide helps you find what you need.

---

## 📚 Documentation Files Overview

### 1. **[BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md)** ⚡ START HERE
**Best for**: Quick lookups, getting started, troubleshooting
- Base URLs at a glance
- Curl testing examples
- Endpoint summary (POST /process, POST /web-check)
- Actions reference table
- Common issues & quick fixes
- Configuration examples
- ~5 minute read

**Use when you need**: 
- "What's the endpoint URL?"
- "How do I test this?"
- "Why am I getting a 429 error?"
- Quick reference while coding

---

### 2. **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** 📖 COMPLETE REFERENCE
**Best for**: Understanding complete API structure, spec compliance, formal documentation
- Full endpoint documentation with all fields
- Request/response JSON schemas with examples
- Detailed field validation rules
- Learning state parameter explanations
- HTTP error codes and responses
- Python and Kotlin code examples
- Network configuration details
- Security considerations
- ~30 minute read

**Use when you need**:
- Complete API specification
- All request/response variations
- Understanding confidence/weakness parameters
- Implementing error handling
- Setting up different deployment scenarios

---

### 3. **[BRIDGE_TECHNICAL_REFERENCE.md](BRIDGE_TECHNICAL_REFERENCE.md)** 🔧 DEEP DIVE
**Best for**: Understanding architecture, advanced scenarios, performance optimization
- Real-world request scenarios with full flow
- State management and Q-learning details
- Network architecture diagram
- Performance metrics and timings
- Connection modes (emulator, device, network)
- Learning profiles explanation
- Advanced Python testing code
- Request lifecycle with timing
- Error recovery strategies with code
- ~45 minute read

**Use when you need**:
- Understand how Q-learning chooses actions
- Optimize performance
- Implement advanced error recovery
- Multiple device configuration
- Deep understanding of request flow
- Testing bridge directly with Python

---

### 4. **[ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md)** 📱 ANDROID FOCUS
**Best for**: Android developers, app configuration, troubleshooting
- File location reference
- Configuration for different scenarios (emulator, device, production)
- Step-by-step setup for each scenario
- Request flow in QuizScreen with actual code
- Database storage (InteractionEntity, queries)
- License validation details
- Error handling patterns with code
- Network debugging techniques
- Performance optimization tips
- Manifest permissions checklist
- ~40 minute read

**Use when you need**:
- Set up Android app for your environment
- Update EngineClient.kt for your IP
- Understand how QuizScreen works
- Debug network issues from Android
- Configure for physical device vs emulator
- Implement offline/fallback behavior
- Understand database integration

---

## 🎯 Quick Navigation by Task

### "I want to get started right now"
1. Read: [BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md) (5 min)
2. Start bridge: `python bridge/server.py`
3. Test: `curl -X POST http://localhost:8001/process ...`

### "I'm building the Android app"
1. Read: [ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md)
2. Update EngineClient.kt BASE_URL
3. Test with emulator or device
4. Reference [BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md) for API format

### "I need complete API spec"
1. Read: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Use as reference while implementing
3. Check examples for each action

### "I'm debugging connection issues"
1. Check [BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md#-common-issues--fixes)
2. Read [ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md#debugging-network-issues)
3. Follow testing checklist in [BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md#-testing-checklist)

### "I want to understand the architecture"
1. Read: [BRIDGE_TECHNICAL_REFERENCE.md](BRIDGE_TECHNICAL_REFERENCE.md)
2. Study network architecture diagram
3. Follow real-world request scenarios
4. Review Q-learning section

### "I need to optimize performance"
1. Check: [BRIDGE_TECHNICAL_REFERENCE.md](BRIDGE_TECHNICAL_REFERENCE.md#performance-metrics)
2. Review: [ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md#performance-optimization)
3. Adjust timeouts and parameters

### "I'm setting up for production"
1. Read: [API_DOCUMENTATION.md](API_DOCUMENTATION.md#security-considerations)
2. Review: [ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md#scenario-c-multiple-devices)
3. Check: [BRIDGE_TECHNICAL_REFERENCE.md](BRIDGE_TECHNICAL_REFERENCE.md#connection-modes)

---

## 📊 Documentation Roadmap

```
New User?
    ↓
[QUICK_REFERENCE] (5 min)
    ↓
Is it Android?  →  [ANDROID_IMPL_GUIDE] (40 min)
    ↓ No
Full API?      →  [API_DOCUMENTATION] (30 min)
    ↓ No (Understanding)
Architecture?  →  [TECHNICAL_REFERENCE] (45 min)
```

---

## 🔑 Key Concepts Quick Lookup

### Endpoints
```
POST /process     ← Main learning engine (ask, evaluate, study)
POST /web-check   ← Extract text from URLs
```
See: [BRIDGE_QUICK_REFERENCE.md#-endpoints](BRIDGE_QUICK_REFERENCE.md#-endpoints)

### Actions (Possible Responses)
```
explain, explain_step_by_step, ask_clarification, be_concise, refuse, stay_silent
```
See: [BRIDGE_QUICK_REFERENCE.md#-actions-reference](BRIDGE_QUICK_REFERENCE.md#-actions-reference)

### Base URLs
```
Emulator:  http://10.0.2.2:8001
Device:    http://192.168.1.100:8001 (replace with your IP)
Dev:       http://localhost:8001
```
See: [BRIDGE_QUICK_REFERENCE.md#-base-urls](BRIDGE_QUICK_REFERENCE.md#-base-urls)

### Required Fields
```json
{
  "topic": "string",
  "user_input": "string",
  "confidence": 0.0-1.0,
  "weakness": 0.0-1.0,
  "last_action": "string",
  "user_feedback": "string"
}
```
See: [API_DOCUMENTATION.md](API_DOCUMENTATION.md#request-schema)

### Error Codes
```
200 - Success
400 - Invalid request / Missing fields
402 - License required for exam mode
413 - Input too long
429 - Rate limit exceeded
502 - Fetch failed
```
See: [BRIDGE_QUICK_REFERENCE.md#-testing-checklist](BRIDGE_QUICK_REFERENCE.md#-testing-checklist)

---

## 🛠️ Code Snippets Quick Links

### Starting the Bridge
[BRIDGE_QUICK_REFERENCE.md#-quick-start](BRIDGE_QUICK_REFERENCE.md#-quick-start)

### Testing with cURL
[BRIDGE_QUICK_REFERENCE.md#-quick-start](BRIDGE_QUICK_REFERENCE.md#-quick-start)
[BRIDGE_TECHNICAL_REFERENCE.md#advanced-direct-python-testing](BRIDGE_TECHNICAL_REFERENCE.md#advanced-direct-python-testing)

### Android EngineClient.kt
[ANDROID_IMPLEMENTATION_GUIDE.md#2-process-request-network-call](ANDROID_IMPLEMENTATION_GUIDE.md#2-process-request-network-call)
[BRIDGE_QUICK_REFERENCE.md#-android-code-snippets](BRIDGE_QUICK_REFERENCE.md#-android-code-snippets)

### Building Requests
[API_DOCUMENTATION.md#request-examples](API_DOCUMENTATION.md#request-examples)
[BRIDGE_TECHNICAL_REFERENCE.md#scenario-1-student-asking-a-question](BRIDGE_TECHNICAL_REFERENCE.md#scenario-1-student-asking-a-question)

### Error Handling
[ANDROID_IMPLEMENTATION_GUIDE.md#error-handling-patterns](ANDROID_IMPLEMENTATION_GUIDE.md#error-handling-patterns)
[BRIDGE_TECHNICAL_REFERENCE.md#error-recovery-strategies](BRIDGE_TECHNICAL_REFERENCE.md#error-recovery-strategies)

### Database
[ANDROID_IMPLEMENTATION_GUIDE.md#database-storage](ANDROID_IMPLEMENTATION_GUIDE.md#database-storage)

---

## 📋 Implementation Checklist

### Minimal Setup (5 minutes)
- [ ] Read QUICK_REFERENCE
- [ ] Start bridge: `python bridge/server.py`
- [ ] Test with curl
- [ ] Success! ✅

### Basic Integration (30 minutes)
- [ ] Update EngineClient.kt BASE_URL
- [ ] Build and run Android app
- [ ] Send test request from QuizScreen
- [ ] Verify response in logs
- [ ] Check database storage
- [ ] Success! ✅

### Production Setup (2 hours)
- [ ] Read API_DOCUMENTATION
- [ ] Configure for your deployment (emulator/device/cloud)
- [ ] Set up firewall rules
- [ ] Implement error handling
- [ ] Test all edge cases (429, 402, 400, etc.)
- [ ] Set up monitoring
- [ ] Document your configuration
- [ ] Success! ✅

---

## 🔍 Searching These Docs

### By Endpoint
- `/process` → [API_DOCUMENTATION.md](API_DOCUMENTATION.md#1-process---core-intelligence-endpoint)
- `/web-check` → [API_DOCUMENTATION.md](API_DOCUMENTATION.md#2-web-check---web-content-extraction-endpoint)

### By Language
- **Python** → [BRIDGE_TECHNICAL_REFERENCE.md](BRIDGE_TECHNICAL_REFERENCE.md) & [API_DOCUMENTATION.md](API_DOCUMENTATION.md#python-backend-bridgeserverpy)
- **Kotlin** → [ANDROID_IMPLEMENTATION_GUIDE.md](ANDROID_IMPLEMENTATION_GUIDE.md) & [BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md#-android-code-snippets)
- **JSON** → [API_DOCUMENTATION.md](API_DOCUMENTATION.md#request-schema)
- **cURL** → [BRIDGE_QUICK_REFERENCE.md](BRIDGE_QUICK_REFERENCE.md#test-with-curl)

### By Scenario
- **Emulator** → [ANDROID_IMPLEMENTATION_GUIDE.md#scenario-a-development-emulator-on-same-machine](ANDROID_IMPLEMENTATION_GUIDE.md#scenario-a-development-emulator-on-same-machine)
- **Physical Device** → [ANDROID_IMPLEMENTATION_GUIDE.md#scenario-b-physical-device-on-local-network](ANDROID_IMPLEMENTATION_GUIDE.md#scenario-b-physical-device-on-local-network)
- **Production** → [ANDROID_IMPLEMENTATION_GUIDE.md#scenario-c-multiple-devices](ANDROID_IMPLEMENTATION_GUIDE.md#scenario-c-multiple-devices)
- **Offline/Fallback** → [ANDROID_IMPLEMENTATION_GUIDE.md#error-handling-patterns](ANDROID_IMPLEMENTATION_GUIDE.md#error-handling-patterns)

### By Problem
- **Connection refused** → [BRIDGE_QUICK_REFERENCE.md#issue-connection-refused](BRIDGE_QUICK_REFERENCE.md#issue-connection-refused)
- **Connection timeout** → [BRIDGE_QUICK_REFERENCE.md#issue-connection-timeout-1002022](BRIDGE_QUICK_REFERENCE.md#issue-connection-timeout-1002022)
- **HTTP 429** → [BRIDGE_QUICK_REFERENCE.md#issue-device-returns-http-429](BRIDGE_QUICK_REFERENCE.md#issue-device-returns-http-429)
- **HTTP 402** → [BRIDGE_QUICK_REFERENCE.md#issue-exam-mode-requires-activation](BRIDGE_QUICK_REFERENCE.md#issue-exam-mode-requires-activation)
- **Empty response** → [BRIDGE_QUICK_REFERENCE.md#issue-empty-response](BRIDGE_QUICK_REFERENCE.md#issue-empty-response)
- **Database issues** → [ANDROID_IMPLEMENTATION_GUIDE.md#database-storage](ANDROID_IMPLEMENTATION_GUIDE.md#database-storage)

---

## 📞 Document Quick Stats

| Document | Length | Time | Level | Focus |
|----------|--------|------|-------|-------|
| QUICK_REFERENCE | 5 min | Quick lookup | Beginner | All aspects |
| API_DOCUMENTATION | 30 min | Complete spec | Intermediate | API reference |
| BRIDGE_TECHNICAL | 45 min | Deep understanding | Advanced | Architecture |
| ANDROID_IMPL | 40 min | Implementation | Intermediate | Android setup |

---

## 🚀 Recommended Reading Order

### For Full Understanding
1. QUICK_REFERENCE (overview)
2. API_DOCUMENTATION (spec)
3. ANDROID_IMPLEMENTATION_GUIDE (if doing Android)
4. BRIDGE_TECHNICAL_REFERENCE (architecture)

### For Rapid Integration
1. QUICK_REFERENCE (5 min)
2. ANDROID_IMPLEMENTATION_GUIDE (for your scenario)
3. BRIDGE_QUICK_REFERENCE (troubleshooting as needed)

### For Deep Architecture
1. API_DOCUMENTATION (foundation)
2. BRIDGE_TECHNICAL_REFERENCE (deep dive)
3. ANDROID_IMPLEMENTATION_GUIDE (client specifics)

---

## 📝 Document Maintenance

**Created**: 2026-02-22  
**Version**: 1.0  
**Coverage**: 
- ✅ Endpoint paths & methods
- ✅ Request/response JSON for all actions
- ✅ Auth/headers & base URLs
- ✅ Android-Python bridge architecture
- ✅ Emulator & device configuration
- ✅ Error handling & troubleshooting

---

## 💡 Pro Tips

1. **Bookmark QUICK_REFERENCE** - You'll return to it most
2. **Keep API_DOCUMENTATION open** while implementing
3. **Use BRIDGE_TECHNICAL_REFERENCE for understanding**, not lookup
4. **Reference ANDROID_IMPLEMENTATION_GUIDE for your specific scenario**
5. **Check testing checklist before deployment**

---

## 🎓 Learning Path

```
START
  ↓
[QUICK_REFERENCE] 5 min - Basic facts and testing
  ↓ Understand structure?
[API_DOCUMENTATION] 30 min - Formal specification
  ↓ Ready to code?
[ANDROID_IMPL] 40 min - Implementation details
  ↓ Want deep knowledge?
[TECHNICAL_REFERENCE] 45 min - Architecture & optimization
  ↓
MASTER
```

---

## ✅ Verification Checklist

After reading the docs, verify you understand:
- [ ] How to start the Python bridge
- [ ] What the base URL is for your scenario
- [ ] The 6 required fields in a request
- [ ] What the 6 possible actions are
- [ ] How to handle errors (429, 402, 400, etc.)
- [ ] How Android app connects to Python
- [ ] How to test with curl
- [ ] How database storage works
- [ ] What confidence/weakness parameters mean
- [ ] How to configure for emulator vs device

If all ✅, you're ready to go!

---

**Happy Coding! 🚀**

Need clarification on something? Check the specific document listed in the quick lookup tables above.
