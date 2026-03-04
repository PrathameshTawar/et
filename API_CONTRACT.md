# SatyaSetu API Integration Contract

## Overview
This document defines the contract between the Next.js frontend and FastAPI backend.

## Base URL
- **Development:** `http://localhost:8000`
- **Production:** TBD

---

## REST API Endpoints

### 1. Health Check
```
GET /
```
**Response:**
```json
{
  "message": "SatyaSetu Backend Active",
  "timestamp": "2026-01-31T21:00:00",
  "status": "ready"
}
```

### 2. Process Voice Query
```
POST /api/v1/voice/query
```
**Request:**
```json
{
  "user_id": "string",
  "query": "string",
  "language": "en" | "hi",
  "offline_mode": boolean
}
```

**Response:**
```typescript
{
  "text": string,
  "confidence": number,  // 0-1
  "riskLevel": "low" | "medium" | "high",
  "sources": string[],
  "riskFlags": string[],
  "intent": string,
  "timestamp": string
}
```

### 3. Admin Stats
```
GET /api/v1/admin/stats
```
**Headers:**
```
X-Admin-API-Key: <admin_api_key>
```

**Response:**
```json
{
  "totalQueries": number,
  "scamsBlocked": number,
  "cacheHitRate": number,
  "avgLatency": number,
  "uptime": number
}
```

---

## WebSocket Events

### Connection
```
ws://localhost:8000/ws/telemetry
```

### Server → Client Events

#### 1. Safety Check Start
```typescript
{
  "type": "safety_check_start",
  "payload": {
    "user_id": string,
    "query_preview": string
  },
  "timestamp": string
}
```

#### 2. Safety Block
```typescript
{
  "type": "safety_block",
  "payload": {
    "user_id": string,
    "reason": string[]
  },
  "timestamp": string
}
```

#### 3. Intent Classified
```typescript
{
  "type": "intent_classified",
  "payload": {
    "user_id": string,
    "intent": "scam_verify" | "scheme_lookup" | "general_question" | "offline_fallback"
  },
  "timestamp": string
}
```

#### 4. Cache Hit
```typescript
{
  "type": "cache_hit",
  "payload": {
    "query": string,
    "latency_ms": number
  },
  "timestamp": string
}
```

#### 5. Retrieval Start
```typescript
{
  "type": "retrieval_start",
  "payload": {
    "intent": string,
    "query": string
  },
  "timestamp": string
}
```

#### 6. Generation Start
```typescript
{
  "type": "generation_start",
  "payload": {
    "intent": string,
    "docs_count": number
  },
  "timestamp": string
}
```

#### 7. Response Complete
```typescript
{
  "type": "response_complete",
  "payload": {
    "user_id": string,
    "confidence": number,
    "response_length": number,
    "sources": string[]
  },
  "timestamp": string
}
```

#### 8. Ingestion Status
```typescript
{
  "type": "ingestion_status",
  "payload": {
    "file": string,
    "status": "chunking" | "embedding" | "storing" | "complete",
    "progress": number  // 0-100
  },
  "timestamp": string
}
```

#### 9. Scam Detected
```typescript
{
  "type": "scam_detected",
  "payload": {
    "type": "phishing" | "lottery" | "kyc_fraud" | "job_fake",
    "location": string
  },
  "timestamp": string
}
```

---

## Frontend Integration Examples

### React Hook for WebSocket
```typescript
// hooks/useTelemetry.ts
import { useEffect, useState } from 'react'

export function useTelemetry() {
  const [events, setEvents] = useState<any[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/telemetry')
    
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setEvents(prev => [...prev.slice(-50), data])
    }

    return () => ws.close()
  }, [])

  return { events, connected }
}
```

### API Client
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function processVoiceQuery(
  userId: string,
  query: string,
  language: 'en' | 'hi' = 'en'
) {
  const response = await fetch(`${API_BASE}/api/v1/voice/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, query, language })
  })
  
  return response.json()
}
```

---

## Error Handling

All endpoints return errors in this format:
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "ISO-8601 timestamp"
}
```

Common error codes:
- `SAFETY_VIOLATION` - Request blocked by safety guardrails
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INVALID_LANGUAGE` - Unsupported language code
- `SYSTEM_ERROR` - Internal server error

---

## Rate Limits
- **Voice Query:** 60 requests/minute per user
- **Admin Stats:** 120 requests/minute
- **WebSocket:** 1 connection per client

---

## Authentication
- **Admin endpoints:** Require `X-Admin-API-Key` header
- **User endpoints:** No auth required (for demo)
- **Production:** Implement JWT-based auth

---

## TODO for Production
- [ ] Add JWT authentication
- [ ] Implement request signing
- [ ] Add response compression
- [ ] Enable HTTPS only
- [ ] Add request/response validation
- [ ] Implement proper CORS policies
