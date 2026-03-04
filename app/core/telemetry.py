"""
Telemetry Manager for Real-Time Admin Dashboard
Broadcasts AI pipeline events via WebSocket
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class TelemetryManager:
    """
    Manages WebSocket connections and broadcasts telemetry events
    to the admin dashboard in real-time
    """
    
    def __init__(self):
        self.clients: Dict[str, WebSocket] = {}
        self.event_history: list = []
        self.max_history = 1000
        
    async def initialize(self):
        """Initialize telemetry system"""
        logger.info("📡 Telemetry Manager initialized")
        
    async def add_client(self, client_id: str, websocket: WebSocket):
        """Register a new WebSocket client"""
        self.clients[client_id] = websocket
        logger.info(f"✅ Client connected: {client_id}")
        
        # Send recent history to new client
        for event in self.event_history[-50:]:  # Last 50 events
            try:
                await websocket.send_text(json.dumps(event))
            except:
                pass
    
    async def remove_client(self, client_id: str):
        """Unregister a WebSocket client"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"❌ Client disconnected: {client_id}")
    
    async def emit(self, event_type: str, payload: Dict[str, Any]):
        """
        Broadcast telemetry event to all connected clients
        
        Event types:
        - safety_check_start
        - safety_block
        - intent_classified
        - retrieval_start
        - cache_hit
        - generation_start
        - response_complete
        - ingestion_status
        - scam_detected
        """
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Broadcast to all clients
        disconnected_clients = []
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send_text(json.dumps(event))
            except Exception as e:
                logger.warning(f"Failed to send to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.remove_client(client_id)
    
    async def cleanup(self):
        """Cleanup all connections"""
        logger.info("🧹 Cleaning up Telemetry Manager...")
        for client_id in list(self.clients.keys()):
            await self.remove_client(client_id)
