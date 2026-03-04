# SatyaSetu - Priority Implementation Guide

## 🎯 The Core Challenge

Your project is **70% architecturally complete** but **30% functionally implemented**. Here's what needs to be done:

---

## 🔴 PHASE 1: CRITICAL PATH (Next 1 Week)

### 1.1 Replace Orchestrator Placeholders

**File:** `backend/orchestrator.py`

Current status: TODO placeholders throughout. Replace with:

```python
# TASKS:
✅ safety_check() - Integrate Guardrails AI
✅ intent_router() - Use small BERT model or LLM
✅ retrieve_context() - Connect to Chroma vector DB
✅ generate_response() - Stream from OpenAI
✅ post_process() - Add confidence & source tracking
```

### 1.2 Implement Core LLM Integration

**File:** `backend/core/orchestrator.py` (new) or `backend/orchestrator.py`

```python
# REQUIRED IMPLEMENTATION:
- OpenAI client initialization with API key
- LLM call functions with streaming
- Token counting for rate limiting
- Error handling and retry logic
- Prompt templates for scam detection

# Key prompts needed:
1. Safety classifier prompt
2. Intent detection prompt
3. Scam verdict prompt
4. Risk level classifier prompt
```

### 1.3 Setup Vector Database with Real Data

**File:** `backend/services/vector_db.py` (new)

```python
# IMPLEMENTATION:
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Load sample data:
- 50 common scam messages (Hindi + English)
- 30 government scheme details (from PIB)
- 20 banking safety guidelines (from RBI)
- 15 payment fraud patterns

# Upload to Chroma with metadata (source, language, category)
```

**Data to collect:**
```
scams_database.json
├── voice_scams[]     # "Your bank account is compromised"
├── payment_scams[]   # "Verify UPI ID now"
├── scheme_scams[]    # "Free government grant available"
└── phishing_scams[]  # "Click link to update Aadhar"
```

---

## 🟡 PHASE 2: VOICE I/O (Next 3-5 Days)

### 2.1 Speech-to-Text (STT) Integration

**File:** `backend/app/services/voice/stt.py`

```python
from google.cloud import speech_v1

# IMPLEMENT:
def transcribe_audio(audio_bytes: bytes, language_code: str) -> str:
    """Convert audio to text in specified language"""
    # Support: "en-US", "hi-IN", "ta-IN", "te-IN"
    # Error handling for invalid audio
    # Return confidence scores
```

### 2.2 Text-to-Speech (TTS) Integration

**File:** `backend/app/services/voice/tts.py`

```python
from google.cloud import texttospeech_v1

# IMPLEMENT:
def synthesize_speech(text: str, language_code: str) -> bytes:
    """Convert text to speech in specified language"""
    # Use natural sounding voices (Wavenet if available)
    # Return audio bytes (MP3/WAV)
```

---

## 🟢 PHASE 3: FRONTEND POLISH (Next Week)

### 3.1 Voice Recording UI Component

**File:** `frontend/components/VoiceRecorder.tsx`

```typescript
// REQUIRED:
- Record audio with MediaRecorder API
- Show waveform visualization
- Display live transcription
- Show confidence score
- Play back response audio

// Error handling:
- Microphone permission denied
- Browser not supported
- Network timeout
```

### 3.2 Results Display Component

**File:** `frontend/components/VerificationResult.tsx`

```typescript
// SHOW:
interface VerificationResult {
  verdict: "SCAM" | "SAFE" | "UNCERTAIN"
  confidence: number           // 0.0-1.0, show as gauge
  riskLevel: "LOW" | "MEDIUM" | "HIGH"
  sources: Source[]            // With links
  riskFlags: string[]          // Colored badges
  explanation: string          // In user's language
  responseAudio: string        // Audio URL for playback
}
```

---

## 📊 PHASE 4: DATA INGESTION (Parallel to Phase 2-3)

### 4.1 Government Data Sources

Create `data/ingest_sources.py`:

```python
# SOURCE 1: PIB (Press Information Bureau)
def ingest_pib_news():
    """Get latest PIB articles to Redis cache"""
    # Parse PIB RSS feed
    # Extract key points
    # Upload to vector DB

# SOURCE 2: RBI Circulars
def ingest_rbi_circulars():
    """Get latest RBI circulars"""
    # Scrape RBI website
    # Extract scheme/payment info
    # Upload to vector DB

# SOURCE 3: Common Scam Patterns
def ingest_scam_patterns():
    """Upload known scam signatures"""
    # Load from CSV
    # Add to vector DB with HIGH priority
```

### 4.2 Fact-Check Integration

```python
# Connect to fact-check APIs:
- Alt News (Indian focused)
- Boomslang (Multi-language)
- AFP Fact Check
- Snopes (International)

# Store verified claims in vector DB
```

---

## 🏗️ FILE-BY-FILE IMPLEMENTATION CHECKLIST

### Backend Files (Priority Order)

```
backend/
├── orchestrator.py
│   TODO: Replace all placeholder functions ✅
│   TODO: Add LLM integration ✅
│
├── core/
│   ├── orchestrator.py (NEW)
│   │   TODO: Main LangGraph orchestrator
│   │
│   ├── llm_client.py (NEW)
│   │   TODO: OpenAI client with streaming
│   │
│   └── vector_store.py (NEW)
│       TODO: Chroma DB initialization & Utils
│
├── services/
│   ├── vector_db.py (NEW)
│   │   TODO: Data loading & retrieval
│   │
│   └── verification_engine.py (NEW)
│       TODO: Confidence scoring & risk classification
│
├── api/routes/
│   ├── voice.py
│   │   TODO: Connect to orchestrator
│   │   TODO: Add streaming response
│   │
│   └── admin.py
│       TODO: Add verification stats endpoint
│
└── data/
    ├── scams_hindi.json (NEW)
    ├── scams_english.json (NEW)
    ├── government_schemes.json (NEW)
    └── payment_guidelines.json (NEW)
```

### Frontend Files (Priority Order)

```
frontend/
├── components/
│   ├── VoiceRecorder.tsx (NEW or UPDATE)
│   │   TODO: Add real mic recording
│   │   TODO: Add visual feedback
│   │
│   └── VerificationResult.tsx (NEW or UPDATE)
│       TODO: Display verdict with gauge
│       TODO: Show sources with links
│       TODO: Play audio response
│
├── pages/
│   ├── voice.tsx (UPDATE)
│   │   TODO: Integrate all components
│   │   TODO: Add error boundaries
│   │
│   └── admin.tsx (NEW)
│       TODO: Show live verification stats
│
└── lib/
    ├── api.ts (UPDATE)
    │   TODO: Add voice endpoint client
    │
    └── voice_stream.ts (NEW)
        TODO: Audio streaming utilities
```

---

## 🧪 QUICK VALIDATION TESTS

After implementing each phase, run these:

### Phase 1 Validation
```bash
# Test orchestrator without external APIs (mock)
pytest backend/tests/test_orchestrator.py

# Check structure
python -c "from orchestrator import ConversationState; print('✅ Orchestrator imports')"
```

### Phase 2 Validation
```bash
# Record audio file, transcribe it
python backend/services/voice/stt.py test_audio.wav

# Generate speech
python backend/services/voice/tts.py "Hello world" hi-IN
```

### Phase 3 Validation
```bash
# Fresh frontend should:
npm run dev
# Navigate to /voice
# Should show microphone UI
```

---

## 🌍 MULTILINGUAL SUPPORT CHECKLIST

For **complete** multilingual support, you need:

```yaml
Languages:
  Hindi:
    ✅ Language code: "hi-IN"
    ✅ STT model training data
    ✅ Common scam phrases
    ✅ Scam dataset (50+ examples)
    
  English:
    ✅ Language code: "en-IN" (or "en-US")
    ✅ Existing support
    
  Tamil:
    ✅ Language code: "ta-IN"
    ✅ TTS voice available
    TODO: Add scam dataset
    
  Telugu:
    ✅ Language code: "te-IN"
    ✅ TTS voice available
    TODO: Add scam dataset
    
  Kannada:
    ✅ Language code: "kn-IN"
    TODO: Add scam dataset
    
  Malayalam:
    ✅ Language code: "ml-IN"
    TODO: Add scam dataset
```

---

## 📋 IMPLEMENTATION ORDER (DO THIS)

| Week | Task | Time | Files |
|------|------|------|-------|
| 1 | Fix orchestrator.py placeholders | 2 days | `orchestrator.py` |
| 1 | Add OpenAI client | 1 day | `core/llm_client.py` |
| 1-2 | Setup Chroma + load scams | 2 days | `services/vector_db.py`, data/*.json |
| 2 | Implement STT | 2 days | `services/voice/stt.py` |
| 2 | Implement TTS | 2 days | `services/voice/tts.py` |
| 2-3 | Update VoiceRecorder component | 2 days | `components/VoiceRecorder.tsx` |
| 3 | Build VerificationResult component | 2 days | `components/VerificationResult.tsx` |
| 3 | End-to-end testing | 2 days | `tests/test_e2e.py` |
| 3 | Deploy to staging | 1 day | Docker + deployment scripts |

---

## 🎯 SUCCESS METRICS

By end of Phase 1:
```
✅ POST /api/voice/query accepts text and returns verdict
✅ Confidence score is calculated and returned
✅ At least 10 test scams detect correctly
✅ API responds in <1 second
```

By end of Phase 2:
```
✅ Audio upload to text works
✅ Response audio can be played back
✅ Hindi language transcription works
```

By end of Phase 3:
```
✅ Frontend records and sends audio
✅ Shows verification result with sources
✅ Displays confidence gauge
✅ Plays response audio
```

---

## 🚀 DEPLOYMENT CHECKLIST

Before submitting to hackathon:

```
TESTING:
[ ] Test with 50+ real scams (mix Hindi/English)
[ ] Test with 20+ legitimate messages
[ ] Latency <2 seconds on 50 concurrent requests
[ ] Language switching works smoothly
[ ] Error handling tested

DEPLOYMENT:
[ ] Docker images build successfully
[ ] Environment variables configured
[ ] API keys secured (not in code)
[ ] Database seeded with real data
[ ] CI/CD pipeline working
[ ] Staging deployment stable

DOCUMENTATION:
[ ] API endpoint documented
[ ] Setup instructions clear
[ ] Code comments added
[ ] Architecture diagram updated
[ ] README has usage examples
```

---

## 💡 PRO TIPS

1. **Start with mock data** - Don't wait for real APIs. Use test scams.
2. **Use free tiers** - Google Cloud, OpenAI all have free credits.
3. **Parallel work** - While one person does backend, another does frontend.
4. **Test early** - Don't wait for everything to be perfect.
5. **Cache results** - Redis can cache verification results for same messages.

---

**Ready to implement? Start with Phase 1.1 - it takes 2 days!**
