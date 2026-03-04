# SatyaSetu Integration Contract

This document defines the API endpoints, WebSocket events, and integration points between the frontend and backend.

## API Endpoints

### Voice Processing

#### POST `/api/voice/process-audio`
Process uploaded audio file through AI pipeline.

**Request:**
- `audio`: File (multipart/form-data)
- `user_id`: string (optional, default: "anonymous")

**Response:**
```json
{
  "success": boolean,
  "transcribed_text": string,
  "intent": string,
  "response": string,
  "audio_url": string,
  "processing_time": number,
  "error": string
}
```

#### POST `/api/voice/process-text`
Process text input through AI pipeline (for testing).

**Request:**
```json
{
  "text": string,
  "user_id": string,
  "language": string
}
```

**Response:** Same as process-audio

#### GET `/api/voice/health`
Voice service health check.

### Admin Dashboard

#### GET `/api/admin/stats`
Get comprehensive system statistics.

**Response:**
```json
{
  "uptime": string,
  "total_requests": number,
  "active_connections": number,
  "recent_events": TelemetryEvent[],
  "ai_pipeline_stats": {
    "total_processed": number,
    "avg_processing_time": number,
    "success_rate": number,
    "most_common_intent": string,
    "node_performance": object
  }
}
```

#### GET `/api/admin/events?limit=50`
Get recent telemetry events.

#### GET `/api/admin/pipeline-status`
Get AI pipeline component status.

#### POST `/api/admin/trigger-test-event`
Trigger a test telemetry event.

### Debug

#### POST `/api/debug/chat`
Debug chat endpoint for testing.

#### GET `/api/debug/pipeline-test`
Test the AI pipeline with mock data.

#### GET `/api/debug/mock-data`
Get mock data for frontend testing.

## WebSocket Events

### Connection: `ws://localhost:8000/ws/telemetry`

Real-time telemetry feed for admin dashboard.

### Event Types

#### System Events
- `telemetry_system_initialized`
- `telemetry_client_connected`
- `telemetry_client_disconnected`

#### Voice Processing Events
- `voice_processing_started`
- `voice_processing_completed`
- `voice_processing_error`

#### AI Pipeline Node Events
- `node_safety_check_started`
- `node_safety_check_completed`
- `node_intent_router_started`
- `node_intent_router_completed`
- `node_retrieve_context_started`
- `node_retrieve_context_completed`
- `node_generate_response_started`
- `node_generate_response_completed`
- `node_post_process_started`
- `node_post_process_completed`

#### Admin Events
- `admin_test_event`

### Event Payload Structure
```json
{
  "type": string,
  "timestamp": string (ISO 8601),
  "data": object
}
```

## TODO: Streaming Integration Points

### 1. STT (Speech-to-Text) Integration
**Location:** `backend/core/orchestrator.py` → `_intent_router_node()`

```python
# TODO: Replace mock transcription
if state.audio_data and not state.transcribed_text:
    # Integrate Whisper or similar STT service
    state.transcribed_text = await stt_service.transcribe(state.audio_data)
```

### 2. TTS (Text-to-Speech) Integration
**Location:** `backend/core/orchestrator.py` → `_post_process_node()`

```python
# TODO: Replace mock TTS
# Integrate ElevenLabs or similar TTS service
state.audio_response = await tts_service.synthesize(
    text=state.response,
    language="hi",  # Hindi support
    voice_id="rural_friendly_voice"
)
```

### 3. Vector Database Integration
**Location:** `backend/core/orchestrator.py` → `_retrieve_context_node()`

```python
# TODO: Replace mock context retrieval
# Integrate Pinecone or similar vector DB
context_results = await vector_db.similarity_search(
    query=state.user_input,
    filter={"region": "rural_india", "language": "hi"},
    top_k=5
)
```

### 4. Redis Semantic Cache
**Location:** `backend/core/orchestrator.py` → `_retrieve_context_node()`

```python
# TODO: Add semantic caching
cache_key = generate_semantic_hash(state.user_input)
cached_response = await redis_client.get(cache_key)
if cached_response:
    return cached_response
```

### 5. LLM Integration
**Location:** `backend/core/orchestrator.py` → `_generate_response_node()`

```python
# TODO: Replace mock response generation
response = await llm_client.generate(
    prompt=build_rural_cybersecurity_prompt(state.context, state.user_input),
    language="hi",
    max_tokens=200,
    temperature=0.7
)
```

## Frontend Integration Points

### 1. Real Voice Recording
**Location:** `frontend/app/voice/page.tsx` → `startListening()`

```typescript
// TODO: Implement actual voice recording
const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
const mediaRecorder = new MediaRecorder(stream)
// Handle recording and upload to /api/voice/process-audio
```

### 2. Audio Playback
**Location:** `frontend/app/voice/page.tsx` → Response display

```typescript
// TODO: Implement audio response playback
const playAudioResponse = (audioData: ArrayBuffer) => {
  const audioContext = new AudioContext()
  // Decode and play audio response
}
```

### 3. Spline 3D Integration
**Location:** `frontend/app/page.tsx` → Spline container

```typescript
// TODO: Add actual Spline 3D model
import Spline from '@splinetool/react-spline'

<Spline scene="https://prod.spline.design/your-scene-url" />
```

## Environment Variables Required

### Backend (.env)
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
REDIS_URL=redis://localhost:6379
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Development Setup

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access Points:**
   - Landing: http://localhost:3000
   - Voice UI: http://localhost:3000/voice
   - Admin Dashboard: http://localhost:3000/admin
   - API Docs: http://localhost:8000/docs

## Demo Flow

1. User visits landing page
2. Clicks "Start Voice Chat" → Voice UI
3. Records voice or types text
4. Backend processes through AI pipeline
5. Real-time telemetry visible in admin dashboard
6. Response displayed with mock audio playback option

This contract ensures the frontend and backend can work together even with mock implementations, providing a solid foundation for completing the remaining integrations.