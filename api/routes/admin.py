"""
Admin API Routes
System monitoring, telemetry, and configuration
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()

class SystemStats(BaseModel):
    uptime: str
    total_requests: int
    active_connections: int
    recent_events: List[Dict[str, Any]]
    ai_pipeline_stats: Dict[str, Any]

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get comprehensive system statistics"""
    
    from main import telemetry_manager
    
    stats = telemetry_manager.get_system_stats()
    recent_events = telemetry_manager.get_recent_events(20)
    
    # Mock AI pipeline stats
    ai_stats = {
        "total_processed": 42,
        "avg_processing_time": 1.2,
        "success_rate": 0.95,
        "most_common_intent": "cybersecurity_education",
        "languages_detected": ["hi", "en"],
        "node_performance": {
            "safety_check": {"avg_time": 0.1, "success_rate": 1.0},
            "intent_router": {"avg_time": 0.3, "success_rate": 0.98},
            "retrieve_context": {"avg_time": 0.4, "success_rate": 0.95},
            "generate_response": {"avg_time": 0.8, "success_rate": 0.92},
            "post_process": {"avg_time": 0.2, "success_rate": 1.0}
        }
    }
    
    return SystemStats(
        uptime=stats["uptime"],
        total_requests=156,  # Mock
        active_connections=stats["connected_clients"],
        recent_events=recent_events,
        ai_pipeline_stats=ai_stats
    )

@router.get("/events")
async def get_recent_events(limit: int = 50):
    """Get recent telemetry events"""
    
    from main import telemetry_manager
    
    return {
        "events": telemetry_manager.get_recent_events(limit),
        "total_events": len(telemetry_manager.event_history)
    }

@router.get("/pipeline-status")
async def get_pipeline_status():
    """Get AI pipeline component status"""
    
    return {
        "components": {
            "safety_check": {"status": "healthy", "last_check": datetime.now().isoformat()},
            "intent_router": {"status": "healthy", "last_check": datetime.now().isoformat()},
            "retrieve_context": {"status": "degraded", "last_check": datetime.now().isoformat(), "note": "Vector DB connection slow"},
            "generate_response": {"status": "healthy", "last_check": datetime.now().isoformat()},
            "post_process": {"status": "healthy", "last_check": datetime.now().isoformat()}
        },
        "external_services": {
            "vector_db": {"status": "mock", "note": "TODO: Connect Pinecone"},
            "redis_cache": {"status": "mock", "note": "TODO: Setup Redis"},
            "stt_service": {"status": "mock", "note": "TODO: Configure Whisper"},
            "tts_service": {"status": "mock", "note": "TODO: Configure ElevenLabs"}
        }
    }

@router.post("/trigger-test-event")
async def trigger_test_event():
    """Trigger a test telemetry event for dashboard testing"""
    
    from main import telemetry_manager
    
    await telemetry_manager.emit("admin_test_event", {
        "message": "Test event triggered from admin panel",
        "test_data": {"value": 123, "status": "success"}
    })
    
    return {"message": "Test event triggered successfully"}