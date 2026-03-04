"""
Monitoring and metrics collection for SatyaSetu
Performance tracking, error monitoring, and health checks
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class HealthStatus:
    """Health check status"""
    service: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        
    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Record a counter metric"""
        self.counters[name] += value
        self.metrics[name].append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        ))
        
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge metric"""
        self.gauges[name] = value
        self.metrics[name].append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        ))
        
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric (for timing, etc.)"""
        self.metrics[name].append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        ))
        
    def get_metric_summary(self, name: str, window_minutes: int = 5) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        if name not in self.metrics:
            return {}
            
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_points = [
            point for point in self.metrics[name] 
            if point.timestamp >= cutoff_time
        ]
        
        if not recent_points:
            return {}
            
        values = [point.value for point in recent_points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
            "latest": values[-1] if values else 0
        }
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "summaries": {
                name: self.get_metric_summary(name) 
                for name in self.metrics.keys()
            }
        }

class HealthChecker:
    """Monitors service health"""
    
    def __init__(self):
        self.health_status: Dict[str, HealthStatus] = {}
        
    async def check_service_health(self, service_name: str, check_func) -> HealthStatus:
        """Check health of a specific service"""
        try:
            start_time = time.time()
            result = await check_func()
            check_time = time.time() - start_time
            
            status = HealthStatus(
                service=service_name,
                status="healthy" if result else "unhealthy",
                last_check=datetime.now(),
                details={
                    "response_time": check_time,
                    "result": result
                }
            )
            
        except Exception as e:
            status = HealthStatus(
                service=service_name,
                status="unhealthy",
                last_check=datetime.now(),
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
        self.health_status[service_name] = status
        return status
        
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        if not self.health_status:
            return {"status": "unknown", "services": {}}
            
        healthy_count = sum(1 for s in self.health_status.values() if s.status == "healthy")
        total_count = len(self.health_status)
        
        if healthy_count == total_count:
            overall_status = "healthy"
        elif healthy_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
            
        return {
            "status": overall_status,
            "healthy_services": healthy_count,
            "total_services": total_count,
            "services": {
                name: {
                    "status": health.status,
                    "last_check": health.last_check.isoformat(),
                    "details": health.details
                }
                for name, health in self.health_status.items()
            }
        }

class PerformanceMonitor:
    """Monitors application performance"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.active_requests: Dict[str, float] = {}
        
    def start_request(self, request_id: str, endpoint: str):
        """Start tracking a request"""
        self.active_requests[request_id] = time.time()
        self.metrics.record_counter("requests_started", tags={"endpoint": endpoint})
        
    def end_request(self, request_id: str, endpoint: str, status_code: int):
        """End tracking a request"""
        if request_id in self.active_requests:
            duration = time.time() - self.active_requests[request_id]
            del self.active_requests[request_id]
            
            self.metrics.record_histogram("request_duration", duration, tags={
                "endpoint": endpoint,
                "status_code": str(status_code)
            })
            self.metrics.record_counter("requests_completed", tags={
                "endpoint": endpoint,
                "status_code": str(status_code)
            })
            
    def record_ai_processing(self, duration: float, intent: str, success: bool):
        """Record AI processing metrics"""
        self.metrics.record_histogram("ai_processing_duration", duration, tags={
            "intent": intent,
            "success": str(success)
        })
        
        if success:
            self.metrics.record_counter("ai_processing_success", tags={"intent": intent})
        else:
            self.metrics.record_counter("ai_processing_error", tags={"intent": intent})
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "active_requests": len(self.active_requests),
            "request_duration": self.metrics.get_metric_summary("request_duration"),
            "ai_processing_duration": self.metrics.get_metric_summary("ai_processing_duration"),
            "requests_per_minute": self.metrics.get_metric_summary("requests_completed", window_minutes=1),
            "error_rate": self._calculate_error_rate()
        }
        
    def _calculate_error_rate(self) -> float:
        """Calculate error rate over the last 5 minutes"""
        success_summary = self.metrics.get_metric_summary("ai_processing_success")
        error_summary = self.metrics.get_metric_summary("ai_processing_error")
        
        success_count = success_summary.get("count", 0)
        error_count = error_summary.get("count", 0)
        total_count = success_count + error_count
        
        if total_count == 0:
            return 0.0
            
        return error_count / total_count

# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
performance_monitor = PerformanceMonitor(metrics_collector)

async def run_health_checks():
    """Run periodic health checks"""
    async def check_redis():
        # TODO: Implement actual Redis health check
        return True
        
    async def check_vector_db():
        # TODO: Implement actual Vector DB health check
        return True
        
    async def check_ai_services():
        # TODO: Implement AI services health check
        return True
    
    # Run health checks
    await health_checker.check_service_health("redis", check_redis)
    await health_checker.check_service_health("vector_db", check_vector_db)
    await health_checker.check_service_health("ai_services", check_ai_services)

async def start_monitoring():
    """Start background monitoring tasks"""
    async def monitoring_loop():
        while True:
            try:
                await run_health_checks()
                
                # Record system metrics
                metrics_collector.record_gauge("active_requests", len(performance_monitor.active_requests))
                
                # Log health status
                health = health_checker.get_overall_health()
                logger.info(f"System health: {health['status']} ({health['healthy_services']}/{health['total_services']} services healthy)")
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                
            await asyncio.sleep(30)  # Check every 30 seconds
    
    # Start monitoring in background
    asyncio.create_task(monitoring_loop())