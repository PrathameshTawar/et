"""
Tests for AI Orchestrator
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from core.orchestrator import AIOrchestrator, ConversationState
from core.telemetry import TelemetryManager

@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing"""
    telemetry_manager = Mock(spec=TelemetryManager)
    telemetry_manager.emit = AsyncMock()
    
    orchestrator = AIOrchestrator(telemetry_manager)
    asyncio.run(orchestrator.initialize())
    return orchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initializes correctly"""
    assert orchestrator.is_initialized
    assert orchestrator.graph is not None

@pytest.mark.asyncio
async def test_voice_processing_success(orchestrator):
    """Test successful voice processing"""
    audio_data = b"test audio data"
    result = await orchestrator.process_voice_input(audio_data, "test_user")
    
    assert result["success"] is True
    assert "response" in result
    assert "processing_time" in result
    assert result["processing_time"] > 0

@pytest.mark.asyncio
async def test_voice_processing_with_text_input(orchestrator):
    """Test processing with text input"""
    text_data = "मुझे साइबर सुरक्षा के बारे में बताएं".encode('utf-8')
    result = await orchestrator.process_voice_input(text_data, "test_user")
    
    assert result["success"] is True
    assert result["transcribed_text"] == "मुझे साइबर सुरक्षा के बारे में बताएं"

@pytest.mark.asyncio
async def test_intent_classification():
    """Test intent classification logic"""
    telemetry_manager = Mock(spec=TelemetryManager)
    telemetry_manager.emit = AsyncMock()
    
    orchestrator = AIOrchestrator(telemetry_manager)
    
    # Test cybersecurity education intent
    intent, confidence = orchestrator._classify_intent("मुझे साइबर सुरक्षा के बारे में जानकारी चाहिए")
    assert intent == "cybersecurity_education"
    assert confidence > 0.7
    
    # Test emergency intent
    intent, confidence = orchestrator._classify_intent("मदद चाहिए तत्काल")
    assert intent == "emergency"
    assert confidence > 0.6
    
    # Test threat report intent
    intent, confidence = orchestrator._classify_intent("मैं एक स्कैम की रिपोर्ट करना चाहता हूं")
    assert intent == "threat_report"
    assert confidence > 0.7

def test_conversation_state_validation():
    """Test conversation state model validation"""
    state = ConversationState(
        user_input="test input",
        confidence_score=1.5  # Should be clamped to 1.0
    )
    
    assert state.confidence_score == 1.0
    assert state.user_input == "test input"
    assert state.safety_status == "pending"
