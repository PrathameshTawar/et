"""
Telemetry Manager for real-time system monitoring
Emits events at every major step for admin dashboard
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Set
from fastapi import WebSocket

class TelemetryManager:
    """Manages real-time telemetry events and WebSocket clients"""
    
    def __init__(self):
        self.clients: Dict[str, WebSocket] = {}
        self.event_history: list = []
        self.max_history = 1000
        
    async def initialize(self):
        """Initialize telemetry system"""
        await self.emit("telemetry_system_initialized", {
            "timestamp": datetime.now().isoformat()
        })
    
    async def cleanup(self):
        """Cleanup telemetry system"""
        for client_id in list(self.clients.keys()):
            await self.remove_client(client_id)
    
    async def add_client(self, client_id: str, websocket: WebSocket):
        """Add a WebSocket client for telemetry updates"""
        self.clients[client_id] = websocket
        
        # Send recent history to new client
        for event in self.event_history[-50:]:  # Last 50 events
            try:
                await websocket.send_text(json.dumps(event))
            except:
                break
        
        await self.emit("telemetry_client_connected", {
            "client_id": client_id,
            "total_clients": len(self.clients)
        })
    
    async def remove_client(self, client_id: str):
        """Remove a WebSocket client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].close()
            except:
                pass
            del self.clients[client_id]
            
            await self.emit("telemetry_client_disconnected", {
                "client_id": client_id,
                "total_clients": len(self.clients)
            })
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """Emit a telemetry event to all connected clients"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Send to all connected clients
        disconnected_clients = []
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send_text(json.dumps(event))
            except:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.remove_client(client_id)
    
    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent telemetry events"""
        return self.event_history[-limit:]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        return {
            "connected_clients": len(self.clients),
            "total_events": len(self.event_history),
            "uptime": datetime.now().isoformat(),
            "recent_event_types": list(set([
                event["type"] for event in self.event_history[-20:]
            ]))
        }