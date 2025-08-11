#!/usr/bin/env python3
"""
Connection Health Monitor Module

Provides comprehensive connection health monitoring and recovery mechanisms
to prevent ClosedResourceError and similar connection issues in production.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("azure_sql_connection_monitor")


class ConnectionState(Enum):
    """Connection state enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CLOSED = "closed"
    UNKNOWN = "unknown"


@dataclass
class ConnectionHealth:
    """Connection health information"""
    state: ConnectionState
    last_check: float
    response_time_ms: float
    error_count: int
    last_error: Optional[str] = None
    recovery_attempts: int = 0


class ConnectionHealthMonitor:
    """Monitors and manages connection health for long-running deployments"""
    
    def __init__(self, check_interval: int = 60, max_errors: int = 5):
        """
        Initialize connection health monitor
        
        Args:
            check_interval: Seconds between health checks
            max_errors: Maximum errors before marking connection as unhealthy
        """
        self.check_interval = check_interval
        self.max_errors = max_errors
        self.connection_health: Dict[str, ConnectionHealth] = {}
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        
        logger.info("Connection health monitor initialized (check_interval=%ds, max_errors=%d)", 
                   check_interval, max_errors)
    
    async def start_monitoring(self, connection_id: str, connection_factory) -> None:
        """Start monitoring a connection"""
        if connection_id in self._monitoring_tasks:
            logger.warning("Already monitoring connection: %s", connection_id)
            return
        
        # Initialize health record
        self.connection_health[connection_id] = ConnectionHealth(
            state=ConnectionState.UNKNOWN,
            last_check=0,
            response_time_ms=0,
            error_count=0
        )
        
        # Start monitoring task
        task = asyncio.create_task(
            self._monitor_connection(connection_id, connection_factory)
        )
        self._monitoring_tasks[connection_id] = task
        
        logger.info("Started monitoring connection: %s", connection_id)
    
    async def stop_monitoring(self, connection_id: str) -> None:
        """Stop monitoring a connection"""
        if connection_id in self._monitoring_tasks:
            self._monitoring_tasks[connection_id].cancel()
            try:
                await self._monitoring_tasks[connection_id]
            except asyncio.CancelledError:
                pass
            del self._monitoring_tasks[connection_id]
            
        if connection_id in self.connection_health:
            del self.connection_health[connection_id]
            
        logger.info("Stopped monitoring connection: %s", connection_id)
    
    async def _monitor_connection(self, connection_id: str, connection_factory) -> None:
        """Monitor a single connection"""
        logger.info("Starting connection monitoring for: %s", connection_id)
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.check_interval)
                await self._check_connection_health(connection_id, connection_factory)
            except asyncio.CancelledError:
                logger.info("Connection monitoring cancelled for: %s", connection_id)
                break
            except Exception as e:
                logger.error("Error in connection monitoring for %s: %s", connection_id, e)
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _check_connection_health(self, connection_id: str, connection_factory) -> None:
        """Perform health check on a connection"""
        start_time = time.time()
        health = self.connection_health[connection_id]
        
        try:
            # Create a test connection
            conn = await connection_factory.create_connection()
            
            # Perform simple health check query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            
            # Close test connection
            await connection_factory.close_connection(conn)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Update health status
            health.state = ConnectionState.HEALTHY
            health.last_check = time.time()
            health.response_time_ms = response_time
            health.error_count = max(0, health.error_count - 1)  # Gradual recovery
            health.last_error = None
            
            logger.debug("Health check passed for %s (%.1fms)", connection_id, response_time)
            
        except Exception as e:
            error_msg = str(e)
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Update health status
            health.error_count += 1
            health.last_check = time.time()
            health.response_time_ms = response_time
            health.last_error = error_msg
            
            # Determine new state based on error count
            if health.error_count >= self.max_errors:
                health.state = ConnectionState.UNHEALTHY
            elif health.error_count >= self.max_errors // 2:
                health.state = ConnectionState.DEGRADED
            else:
                health.state = ConnectionState.HEALTHY
            
            logger.warning("Health check failed for %s (errors: %d/%d): %s", 
                         connection_id, health.error_count, self.max_errors, error_msg)
    
    def get_connection_health(self, connection_id: str) -> Optional[ConnectionHealth]:
        """Get health information for a connection"""
        return self.connection_health.get(connection_id)
    
    def is_connection_healthy(self, connection_id: str) -> bool:
        """Check if a connection is healthy"""
        health = self.get_connection_health(connection_id)
        if not health:
            return False
        return health.state in [ConnectionState.HEALTHY, ConnectionState.DEGRADED]
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all monitored connections"""
        return {
            conn_id: {
                "state": health.state.value,
                "last_check": health.last_check,
                "response_time_ms": health.response_time_ms,
                "error_count": health.error_count,
                "last_error": health.last_error,
                "is_healthy": health.state in [ConnectionState.HEALTHY, ConnectionState.DEGRADED]
            }
            for conn_id, health in self.connection_health.items()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the health monitor"""
        logger.info("Shutting down connection health monitor...")
        self._shutdown_event.set()
        
        # Cancel all monitoring tasks
        for connection_id in list(self._monitoring_tasks.keys()):
            await self.stop_monitoring(connection_id)
        
        logger.info("Connection health monitor shutdown complete")


class ConnectionRecoveryManager:
    """Manages connection recovery and retry logic"""
    
    def __init__(self, max_retry_attempts: int = 3, base_delay: float = 2.0):
        """
        Initialize connection recovery manager
        
        Args:
            max_retry_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries (exponential backoff)
        """
        self.max_retry_attempts = max_retry_attempts
        self.base_delay = base_delay
        self._recovery_stats = {}
        
        logger.info("Connection recovery manager initialized (max_retries=%d, base_delay=%.1fs)", 
                   max_retry_attempts, base_delay)
    
    async def recover_connection(self, connection_factory, connection_id: str = "default") -> bool:
        """
        Attempt to recover a failed connection with exponential backoff
        
        Returns:
            True if recovery successful, False otherwise
        """
        logger.info("Attempting connection recovery for: %s", connection_id)
        
        for attempt in range(1, self.max_retry_attempts + 1):
            try:
                delay = self.base_delay * (2 ** (attempt - 1))  # Exponential backoff
                
                if attempt > 1:
                    logger.info("Recovery attempt %d/%d for %s (waiting %.1fs)", 
                              attempt, self.max_retry_attempts, connection_id, delay)
                    await asyncio.sleep(delay)
                
                # Test connection creation
                conn = await connection_factory.create_connection()
                
                # Test with simple query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                # Close test connection
                await connection_factory.close_connection(conn)
                
                logger.info("✅ Connection recovery successful for %s (attempt %d)", 
                          connection_id, attempt)
                
                # Update recovery stats
                self._recovery_stats[connection_id] = {
                    "last_recovery": time.time(),
                    "attempts_used": attempt,
                    "success": True
                }
                
                return True
                
            except Exception as e:
                logger.warning("Recovery attempt %d/%d failed for %s: %s", 
                             attempt, self.max_retry_attempts, connection_id, str(e))
                
                if attempt == self.max_retry_attempts:
                    logger.error("❌ Connection recovery failed for %s after %d attempts", 
                               connection_id, self.max_retry_attempts)
                    
                    # Update recovery stats
                    self._recovery_stats[connection_id] = {
                        "last_recovery": time.time(),
                        "attempts_used": attempt,
                        "success": False
                    }
                    
                    return False
        
        return False
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get connection recovery statistics"""
        return self._recovery_stats.copy()
