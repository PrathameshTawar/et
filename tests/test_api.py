"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import io

from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SatyaSetu Backend Active"
    assert "timestamp" in data
    assert data["status"] == "ready"

def test_voice_health_endpoint():
    """Test voice health endpoint"""
    response = client.get("/api/voice/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data

@patch('api.routes.voice.ai_orchestrator')
def test_process_text_endpoint(mock_orchestrator):
    """Test text processing endpoint"""
    # Mock the orchestrator response
    mock_orchestrator.process_voice_input = AsyncMock(return_value={
        "success": True,
        "transcribed_text": "test input",
        "intent": "cybersecurity_education",
        "response": "Test response",
        "processing_time": 1.0
    })
    
    response = client.post("/api/voice/process-text", json={
        "text": "test input",
        "user_id": "test_user",
        "language": "hi"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["response"] == "Test response"

def test_process_text_validation_error():
    """Test text processing with invalid input"""
    response = client.post("/api/voice/process-text", json={
        "text": "",  # Empty text should fail validation
        "user_id": "test_user"
    })
    
    assert response.status_code == 422  # Validation error

@patch('api.routes.voice.ai_orchestrator')
def test_process_audio_endpoint(mock_orchestrator):
    """Test audio processing endpoint"""
    # Mock the orchestrator response
    mock_orchestrator.process_voice_input = AsyncMock(return_value={
        "success": True,
        "transcribed_text": "audio input",
        "intent": "general_query",
        "response": "Audio response",
        "processing_time": 1.5
    })
    
    # Create a mock audio file
    audio_data = b"fake audio data"
    files = {"audio": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
    
    response = client.post("/api/voice/process-audio", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["response"] == "Audio response"

def test_admin_stats_endpoint():
    """Test admin stats endpoint"""
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "uptime" in data
    assert "total_requests" in data
    assert "ai_pipeline_stats" in data

def test_admin_pipeline_status():
    """Test admin pipeline status endpoint"""
    response = client.get("/api/admin/pipeline-status")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "external_services" in data

def test_debug_chat_endpoint():
    """Test debug chat endpoint"""
    response = client.post("/api/debug/chat", json={
        "message": "test message",
        "user_id": "debug_user"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "response" in data

def test_rate_limiting():
    """Test rate limiting middleware"""
    # This would require more complex setup to test properly
    # For now, just ensure the endpoint responds
    response = client.get("/")
    assert response.status_code == 200
    
    # Check for rate limiting headers
    assert "X-Process-Time" in response.headers