"""Telemetry manager for broadcasting events to WebSocket clients.

Provides a simple in-memory client registry and broadcast helper used
by the admin dashboard for live telemetry.

NOTE: This is a demo-grade implementation. Replace with a more robust
pub/sub system (Redis, NATS) for production and handle authorization.
"""
import asyncio
import json
import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class TelemetryManager:
    def __init__(self):
        self.clients: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
        self.event_history: List[Dict[str, Any]] = []
        self.started_at = None

    async def initialize(self):
        # Placeholder for any initialization logic (e.g., connect to Redis pubsub)
        self.started_at = __import__("datetime").datetime.utcnow()
        logger.info("TelemetryManager initialized")

    async def cleanup(self):
        # Close all websockets gracefully
        async with self._lock:
            for client_id, ws in list(self.clients.items()):
                try:
                    await ws.close()
                except Exception:
                    pass
            self.clients.clear()
        logger.info("TelemetryManager cleaned up")

    async def add_client(self, client_id: str, websocket: WebSocket):
        async with self._lock:
            self.clients[client_id] = websocket
        await self.emit("telemetry_client_connected", {"client_id": client_id})
        logger.info(f"Client added: {client_id}")

    async def remove_client(self, client_id: str):
        async with self._lock:
            if client_id in self.clients:
                try:
                    await self.clients[client_id].close()
                except Exception:
                    pass
                del self.clients[client_id]
        await self.emit("telemetry_client_disconnected", {"client_id": client_id})
        logger.info(f"Client removed: {client_id}")

    async def emit(self, event_type: str, data: dict):
        """Broadcast an event to all connected telemetry clients.

        Payload structure follows the integration contract:
          { type: str, timestamp: iso, data: object }
        """
        payload = {
            "type": event_type,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "data": data,
        }

        text = json.dumps(payload)

        # store recent events (capped)
        try:
            self.event_history.append(payload)
            if len(self.event_history) > 500:
                self.event_history.pop(0)
        except Exception:
            logger.exception("Failed to record event history")

        # Broadcast concurrently but don't fail the emitter if one client errors
        async with self._lock:
            clients = list(self.clients.items())

        async def _send(client_id: str, ws: WebSocket):
            try:
                await ws.send_text(text)
            except Exception:
                logger.warning(f"Failed to send telemetry to {client_id}, removing client")
                await self.remove_client(client_id)

        coros = [_send(cid, ws) for cid, ws in clients]
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    def get_recent_events(self, limit: int = 50):
        return list(self.event_history[-limit:])

    def get_system_stats(self):
        uptime = "unknown"
        if self.started_at:
            uptime = str((__import__("datetime").datetime.utcnow() - self.started_at))

        return {
            "uptime": uptime,
            "connected_clients": len(self.clients),
        }
