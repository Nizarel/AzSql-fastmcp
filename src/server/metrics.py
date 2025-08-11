#!/usr/bin/env python3
"""
Health & Metrics Module

Handles server health monitoring, request tracking, and performance metrics.
"""

import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from fastmcp import Context

logger = logging.getLogger("azure_sql_health_metrics")


class HealthMetrics:
    """Server health and performance metrics tracking"""
    
    def __init__(self, max_request_history: int = 100):
        """Initialize metrics tracking"""
        self._start_time = time.time()
        self._request_count = 0
        self._request_times: List[float] = []
        self._max_request_history = max_request_history
        self._error_count = 0
        self._last_error_time = None
        
        logger.info("Health metrics initialized")
    
    def track_request(self, duration: float, success: bool = True):
        """Track a request execution"""
        self._request_count += 1
        self._request_times.append(duration)
        
        if not success:
            self._error_count += 1
            self._last_error_time = datetime.now()
        
        # Keep only last N request times
        if len(self._request_times) > self._max_request_history:
            self._request_times.pop(0)
    
    def get_uptime_seconds(self) -> int:
        """Get server uptime in seconds"""
        return int(time.time() - self._start_time)
    
    def get_average_response_time_ms(self) -> int:
        """Get average response time in milliseconds"""
        if not self._request_times:
            return 0
        return int(sum(self._request_times) / len(self._request_times) * 1000)
    
    def get_request_count(self) -> int:
        """Get total request count"""
        return self._request_count
    
    def get_error_count(self) -> int:
        """Get total error count"""
        return self._error_count
    
    def record_error(self, error_type: str = "general"):
        """Record an error occurrence"""
        self._error_count += 1
        self._last_error_time = datetime.now()
        logger.debug("Error recorded: %s (total errors: %d)", error_type, self._error_count)
    
    def get_error_rate(self) -> float:
        """Get error rate as percentage"""
        if self._request_count == 0:
            return 0.0
        return (self._error_count / self._request_count) * 100
    
    def get_health_status(self) -> str:
        """Determine overall health status"""
        error_rate = self.get_error_rate()
        
        if error_rate > 50:
            return 'unhealthy'
        elif error_rate > 10:
            return 'degraded'
        else:
            return 'healthy'
    
    async def perform_health_check(self, ctx: Context) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            'server': self.get_health_status(),
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': self.get_uptime_seconds(),
            'request_count': self.get_request_count(),
            'error_count': self.get_error_count(),
            'error_rate_percent': round(self.get_error_rate(), 2),
            'database': 'unknown',
            'version': '3.0.0'
        }
        
        # Add response time if available
        avg_response_time = self.get_average_response_time_ms()
        if avg_response_time > 0:
            health['avg_response_time_ms'] = avg_response_time
        
        # Add last error time if any errors occurred
        if self._last_error_time:
            health['last_error_time'] = self._last_error_time.isoformat()
        
        # Test database connection
        try:
            conn = ctx.request_context.lifespan_context.get("conn")
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                health['database'] = 'connected'
            else:
                health['database'] = 'disconnected'
                if health['server'] == 'healthy':
                    health['server'] = 'degraded'
        except (ConnectionError, OSError, RuntimeError) as e:
            health['database'] = f'error: {str(e)}'
            health['server'] = 'unhealthy'
            self.track_request(0, success=False)
        
        return health
    
    async def get_health_check_json(self, ctx: Context) -> str:
        """Get health check as JSON string"""
        health = await self.perform_health_check(ctx)
        return json.dumps(health, indent=2)
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self._start_time = time.time()
        self._request_count = 0
        self._request_times.clear()
        self._error_count = 0
        self._last_error_time = None
        logger.info("Metrics reset")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        return {
            'uptime_seconds': self.get_uptime_seconds(),
            'total_requests': self.get_request_count(),
            'total_errors': self.get_error_count(),
            'error_rate_percent': round(self.get_error_rate(), 2),
            'avg_response_time_ms': self.get_average_response_time_ms(),
            'health_status': self.get_health_status(),
            'request_history_size': len(self._request_times)
        }
