"""
SatyaSetu Backend - FastAPI Entry Point
Voice-first rural cyber-defense system
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime

from config import settings
from api.routes import voice, admin, debug, history, render_video
from core.orchestrator import AIOrchestrator
from core.telemetry import TelemetryManager
from core.exceptions import SatyaSetuException
from core.middleware import RateLimitMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware
from core.monitoring import start_monitoring, performance_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
telemetry_manager = TelemetryManager()
ai_orchestrator = AIOrchestrator(telemetry_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 SatyaSetu Backend Starting...")
    try:
        await telemetry_manager.initialize()
        await ai_orchestrator.initialize()
        await start_monitoring()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 SatyaSetu Backend Shutting Down...")
    try:
        await telemetry_manager.cleanup()
        await ai_orchestrator.cleanup()
        logger.info("✅ Cleanup completed successfully")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

app = FastAPI(
    title="SatyaSetu API",
    description="Voice-first rural cyber-defense system",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

if settings.DEBUG:
    app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "testserver"]
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(render_video.router, prefix="/api/media", tags=["media"])

@app.get("/")
async def root():
    return {
        "message": "SatyaSetu Backend Active",
        "timestamp": datetime.now().isoformat(),
        "status": "ready"
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """Real-time telemetry feed for admin dashboard"""
    await websocket.accept()
    client_id = f"client_{datetime.now().timestamp()}"
    
    try:
        # Register client for telemetry updates
        await telemetry_manager.add_client(client_id, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        await telemetry_manager.remove_client(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
