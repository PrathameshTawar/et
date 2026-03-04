"""
Debug API Routes
Development and testing utilities
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class DebugQuery(BaseModel):
    message: str
    simulate_node: Optional[str] = None
    user_id: Optional[str] = "debug_user"

@router.post("/chat")
async def debug_chat(query: DebugQuery):
    """Debug chat endpoint for testing AI responses"""
    
    from main import ai_orchestrator, telemetry_manager
    
    # Emit debug event
    await telemetry_manager.emit("debug_chat_started", {
        "message": query.message,
        "user_id": query.user_id
    })
    
    # Mock processing based on message content
    if "test" in query.message.lower():
        response = "Debug mode: Test message received successfully!"
    elif "error" in query.message.lower():
        response = "Debug mode: Simulating error handling..."
    elif "hindi" in query.message.lower() or "हिंदी" in query.message:
        response = "डिबग मोड: हिंदी संदेश प्राप्त हुआ!"
    else:
        response = f"Debug echo: {query.message}"
    
    return {
        "success": True,
        "original_message": query.message,
        "response": response,
        "debug_info": {
            "simulated_node": query.simulate_node,
            "processing_mode": "debug",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }

@router.get("/pipeline-test")
async def test_pipeline():
    """Test the AI pipeline with mock data"""
    
    from main import ai_orchestrator
    
    # Test with mock audio data
    mock_audio = b"mock_test_audio_data"
    result = await ai_orchestrator.process_voice_input(mock_audio, "pipeline_test")
    
    return {
        "pipeline_test": "completed",
        "result": result,
        "nodes_executed": [
            "safety_check",
            "intent_router", 
            "retrieve_context",
            "generate_response",
            "post_process"
        ]
    }

@router.get("/mock-data")
async def get_mock_data():
    """Get mock data for frontend testing"""
    
    return {
        "sample_conversations": [
            {
                "user_input": "मुझे साइबर सुरक्षा के बारे में बताएं",
                "intent": "cybersecurity_education",
                "response": "साइबर सुरक्षा के लिए मजबूत पासवर्ड का उपयोग करें।"
            },
            {
                "user_input": "I received a suspicious email",
                "intent": "threat_report",
                "response": "Please do not click any links. Report this to authorities."
            }
        ],
        "telemetry_events": [
            {"type": "voice_processing_started", "timestamp": "2024-01-01T10:00:00Z"},
            {"type": "node_safety_check_completed", "timestamp": "2024-01-01T10:00:01Z"},
            {"type": "node_intent_router_completed", "timestamp": "2024-01-01T10:00:02Z"}
        ],
        "system_metrics": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "active_connections": 3,
            "requests_per_minute": 12
        }
    }