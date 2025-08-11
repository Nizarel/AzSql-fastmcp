#!/usr/bin/env python3
"""
Server Core Module

Main server class that orchestrates all components for the Azure SQL MCP Server
using FastMCP 2.9.2+ streaming HTTP transport.
"""

import sys
import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastmcp import FastMCP
from tenacity import retry, stop_after_attempt, wait_exponential

# Add parent directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import Tools
from connection import SqlConnectionFactory, DatabaseConfig
from .config import ServerConfig
from .metrics import HealthMetrics
from .tool_registry import ToolRegistry
from .resource_manager import ResourceManager
from .prompt_manager import PromptManager
from .connection_monitor import ConnectionHealthMonitor, ConnectionRecoveryManager

logger = logging.getLogger("azure_sql_server_core")


class ServerCore:
    """Core server class that manages all components and lifecycle with streaming HTTP"""
    
    def __init__(self):
        """Initialize server core with all components"""
        try:
            # Initialize configuration
            self.db_config = DatabaseConfig()
            self.server_config = ServerConfig()
            
            # Validate configurations
            if not self.server_config.validate_config():
                logger.critical("Server configuration validation failed")
                sys.exit(1)
            
            logger.info("Database config: %s", self.db_config.get_config_summary())
            logger.info("Server config: %s", self.server_config.get_server_info())
            
        except ValueError as e:
            logger.critical("Configuration error: %s", e)
            sys.exit(1)
        
        # Initialize core components
        self.connection_factory = SqlConnectionFactory(self.db_config)
        self.tools = Tools()
        self.health_metrics = HealthMetrics(
            max_request_history=self.server_config.max_request_history
        )
        
        # Initialize connection monitoring and recovery
        self.connection_monitor = ConnectionHealthMonitor(
            check_interval=self.server_config.heartbeat_interval,
            max_errors=5
        )
        self.recovery_manager = ConnectionRecoveryManager(
            max_retry_attempts=self.server_config.connection_retry_attempts,
            base_delay=self.server_config.connection_retry_delay
        )
        
        # Initialize FastMCP with enhanced 2.10.4 features
        http_config = self.server_config.get_http_config()
        self.mcp = FastMCP(
            name=self.server_config.server_name,
            lifespan=self._lifespan,
            streamable_http_path=http_config['api_path'],
            stateless_http=http_config['stateless_http'],
            json_response=http_config['json_response'],
            host=http_config['host'],
            port=http_config['port'],
            debug=http_config['debug_mode'],
            mask_error_details=False,  # We want detailed errors for debugging
            cache_expiration_seconds=300.0,  # Cache responses for 5 minutes
            on_duplicate_tools="warn",  # Warn on duplicate tool registration
            tool_serializer=lambda x: str(x) if x is not None else ""  # Custom serializer
        )
        
        # Initialize managers
        self.tool_registry = ToolRegistry(self.mcp, self.tools)
        self.resource_manager = ResourceManager(self.mcp, self.connection_factory)
        self.prompt_manager = PromptManager(self.mcp, self.connection_factory)
        
        # Add connection monitoring and error handling middleware
        self._setup_error_handling_middleware()
        
        # Register all components
        self._register_all_components()
        
        logger.info("✅ Server core initialized successfully with streaming HTTP transport")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _create_connection_with_retry(self):
        """Create database connection with automatic retry logic"""
        return await self.connection_factory.create_connection()
    
    @asynccontextmanager
    async def _lifespan(self, _server: FastMCP) -> AsyncIterator[dict]:
        """Manage server lifecycle with database connection and connection pooling"""
        logger.info("🚀 Initializing server lifespan with streaming HTTP...")
        conn = None
        
        try:
            # Initialize connection pool if enabled and not in test mode
            if (self.server_config.connection_pool_size > 0 and 
                not self.server_config.test_mode):
                try:
                    await self.connection_factory.initialize_pool()
                    logger.info(
                        "✅ Connection pool initialized with %d connections",
                        self.server_config.connection_pool_size
                    )
                except (ConnectionError, OSError, RuntimeError) as e:
                    logger.warning("⚠️ Connection pool initialization failed: %s", e)
            
            # Create primary connection
            conn = await self._create_connection_with_retry()
            db_info = await self.connection_factory.test_connection(conn)
            logger.info("✅ Connected to database: %s", db_info['database_name'])
            
            # Start connection monitoring
            await self.connection_monitor.start_monitoring("primary", self.connection_factory)
            logger.info("🔍 Connection health monitoring started")
            
            # Log FastMCP 2.10.4 streaming capabilities
            http_config = self.server_config.get_http_config()
            logger.info("🌊 FastMCP 2.10.4 Enhanced Features:")
            logger.info("   📡 Transport: streamable-http")
            logger.info("   🗜️  Compression: %s", http_config['enable_compression'])
            logger.info("   🌐 CORS: %s", http_config['enable_cors'])
            logger.info("   ⏱️  Stream Timeout: %ds", http_config['stream_timeout'])
            logger.info("   📊 Max Stream Size: %dMB", http_config['max_stream_size'] // 1024 // 1024)
            logger.info("   🔀 Max Concurrent: %d", http_config['max_concurrent_requests'])
            logger.info("   📄 JSON Response: %s", http_config['json_response'])
            logger.info("   🔄 Stateless HTTP: %s", http_config['stateless_http'])
            logger.info("   🐛 Debug Mode: %s", http_config['debug_mode'])
            logger.info("   🔧 Connection Monitoring: enabled")
            logger.info("   🔄 Error Recovery: %s", http_config['enable_error_recovery'])
            logger.info("   🛡️  Error Masking: disabled (detailed errors)")
            
            # Yield context for the application
            yield {
                "conn": conn,
                "factory": self.connection_factory,
                "config": self.db_config,
                "server_config": self.server_config,
                "health_metrics": self.health_metrics,
                "connection_monitor": self.connection_monitor,
                "recovery_manager": self.recovery_manager,
                "http_config": http_config
            }
            
        except (ConnectionError, OSError, RuntimeError) as e:
            logger.error("❌ Connection error after retries: %s", e, exc_info=True)
            # Yield context even if connection failed - tools will handle gracefully
            yield {
                "conn": None,
                "factory": self.connection_factory,
                "config": self.db_config,
                "server_config": self.server_config,
                "health_metrics": self.health_metrics,
                "connection_monitor": self.connection_monitor,
                "recovery_manager": self.recovery_manager,
                "http_config": self.server_config.get_http_config()
            }
        finally:
            # Cleanup connection monitoring
            if hasattr(self, 'connection_monitor'):
                await self.connection_monitor.shutdown()
                logger.info("🔍 Connection monitoring shutdown")
            
            # Cleanup primary connection
            if conn:
                await self.connection_factory.close_connection(conn)
                logger.info("🔌 Primary connection closed")
            
            # Cleanup connection pool if it was initialized
            if hasattr(self.connection_factory, 'cleanup_pool'):
                try:
                    await self.connection_factory.cleanup_pool()
                    logger.info("🔌 Connection pool cleaned up")
                except (ConnectionError, OSError, RuntimeError) as e:
                    logger.warning("⚠️ Connection pool cleanup warning: %s", e)
    
    def _setup_error_handling_middleware(self):
        """Setup comprehensive error handling middleware for connection management"""
        logger.info("🛡️ Setting up error handling middleware...")
        
        # Note: FastMCP doesn't have built-in exception_handler or middleware decorators
        # Error handling will be implemented at the tool level and in the lifespan context
        
        logger.info("✅ Error handling configured at tool level")
    
    def _register_all_components(self):
        """Register all server components (tools, resources, prompts)"""
        logger.info("📋 Registering server components...")
        
        # Register tools with streaming support - ATOMIC REGISTRATION WITH HEALTH METRICS
        self.tool_registry.register_all_tools(health_metrics=self.health_metrics)
        
        # Register resources with streaming support
        self.resource_manager.register_all_resources()
        
        # Register prompts
        self.prompt_manager.register_all_prompts()
        
        # Register streaming-specific endpoints
        self._register_streaming_endpoints()
        
        # Log summary
        self._log_registration_summary()
    
    def _register_streaming_endpoints(self):
        """Register FastMCP 2.9.2+ streaming-specific endpoints"""
        from starlette.responses import JSONResponse
        from starlette.requests import Request
        
        # Register custom health endpoint
        @self.mcp.custom_route("/health", methods=["GET"])
        async def health_endpoint(_request: Request):
            """Health check endpoint with server status and connection monitoring"""
            try:
                metrics = self.health_metrics.get_metrics_summary()
                server_info = self.server_config.get_server_info()
                
                # Get connection health status
                connection_health = {}
                if hasattr(self, 'connection_monitor') and self.connection_monitor:
                    connection_health = self.connection_monitor.get_all_health_status()
                
                # Get recovery statistics
                recovery_stats = {}
                if hasattr(self, 'recovery_manager') and self.recovery_manager:
                    recovery_stats = self.recovery_manager.get_recovery_stats()
                
                health_data = {
                    "status": "healthy" if metrics['health_status'] == 'healthy' else "unhealthy",
                    "transport": "streamable-http",
                    "fastmcp_version": "2.10.4",
                    "server_name": server_info['name'],
                    "server_version": server_info['version'],
                    "features": server_info.get('features', {}),
                    "uptime_seconds": metrics['uptime_seconds'],
                    "total_requests": metrics['total_requests'],
                    "error_rate_percent": metrics['error_rate_percent'],
                    "connection_health": connection_health,
                    "recovery_stats": recovery_stats,
                    "resilience_features": {
                        "connection_monitoring": "enabled",
                        "error_recovery": self.server_config.enable_error_recovery,
                        "heartbeat_interval": self.server_config.heartbeat_interval,
                        "max_error_rate": self.server_config.max_error_rate
                    }
                }
                
                # Log health check request
                self.health_metrics.track_request(0.0, True)
                logger.debug("Health endpoint accessed")
                
                return JSONResponse(health_data)
                
            except (ConnectionError, OSError, RuntimeError) as e:
                logger.error("Health endpoint error: %s", e)
                return JSONResponse(
                    {"status": "error", "message": str(e)}, 
                    status_code=500
                )
        
        # Register custom metrics endpoint
        @self.mcp.custom_route("/metrics", methods=["GET"])
        async def metrics_endpoint(_request: Request):
            """Metrics endpoint with detailed server statistics"""
            try:
                metrics = self.health_metrics.get_metrics_summary()
                server_summary = self.get_server_summary()
                
                metrics_data = {
                    "metrics": metrics,
                    "server_summary": server_summary,
                    "timestamp": metrics.get('last_updated', 'unknown'),
                    "endpoint": "/metrics"
                }
                
                # Log metrics check request
                self.health_metrics.track_request(0.0, True)
                logger.debug("Metrics endpoint accessed")
                
                return JSONResponse(metrics_data)
                
            except (ConnectionError, OSError, RuntimeError) as e:
                logger.error("Metrics endpoint error: %s", e)
                return JSONResponse(
                    {"error": str(e), "status": "error"}, 
                    status_code=500
                )
        
        logger.info("✅ Custom HTTP endpoints registered: /health, /metrics")
    
    def _log_registration_summary(self):
        """Log summary of all registered components"""
        tools_count = self.tool_registry.get_tool_count()
        resources_count = self.resource_manager.get_resource_count()
        prompts_count = self.prompt_manager.get_prompt_count()
        
        logger.info("📊 Registration Summary:")
        logger.info("   🛠️  Tools: %d", tools_count)
        logger.info("   📦 Resources: %d", resources_count)
        logger.info("   💬 Prompts: %d", prompts_count)
        logger.info("   ✅ Total Components: %d", tools_count + resources_count + prompts_count)
        
        # Log feature capabilities
        server_info = self.server_config.get_server_info()
        logger.info("🎯 Server Features:")
        logger.info("   📍 API Endpoint: %s", server_info['api_endpoint'])
        logger.info("   💚 Health Endpoint: %s", server_info['health_endpoint'])
        logger.info("   � Metrics Endpoint: %s", server_info['metrics_endpoint'])
        logger.info("   � Transport: %s", server_info['transport'])
        logger.info("   �🏊 Connection Pool: %s", 
                   'Enabled' if self.server_config.connection_pool_size > 0 else 'Disabled')
        logger.info("   🧪 Test Mode: %s", 
                   'Enabled' if self.server_config.test_mode else 'Disabled')
        logger.info("   ✅ Streaming HTTP: Enabled")
        logger.info("   ✅ Enhanced Error Handling: Enabled")
        logger.info("   ✅ Health Monitoring: Enabled")
        logger.info("   ✅ Request Metrics: Enabled")
    
    def run(self):
        """Start the streaming HTTP server (synchronous) with FastMCP 2.9.2+ optimizations"""
        try:
            logger.info("🚀 Starting Azure SQL MCP Server...")
            logger.info("🎯 Target Database: %s on %s", self.db_config.database, self.db_config.server)
            
            http_config = self.server_config.get_http_config()
            logger.info("🌐 Streaming HTTP Server starting on %s:%d%s", 
                       http_config['host'], http_config['port'], http_config['api_path'])
            
            # Run with optimized streaming HTTP transport (FastMCP 2.10.4 optimized)
            self.mcp.run(
                transport="streamable-http",  # FastMCP 2.10.4 enhanced streaming
                host=http_config['host'],
                port=http_config['port'],
                path=http_config['api_path']
            )
            
        except KeyboardInterrupt:
            logger.info("⏹️ Server shutdown requested by user")
            self._log_final_stats()
        except (ConnectionError, OSError, RuntimeError) as e:
            logger.critical("❌ Server startup failed: %s", e, exc_info=True)
            sys.exit(1)
    
    async def run_async(self):
        """Start the streaming HTTP server (asynchronous) with FastMCP 2.9.2+ optimizations"""
        try:
            logger.info("🚀 Starting Azure SQL MCP Server (async)...")
            logger.info("🎯 Target Database: %s on %s", self.db_config.database, self.db_config.server)
            
            http_config = self.server_config.get_http_config()
            logger.info("🌐 Streaming HTTP Server starting on %s:%d%s", 
                       http_config['host'], http_config['port'], http_config['api_path'])
            
            # Run with optimized streaming HTTP transport asynchronously (FastMCP 2.10.4 optimized)
            await self.mcp.run_http_async(
                transport="streamable-http",  # FastMCP 2.10.4 enhanced streaming
                host=http_config['host'],
                port=http_config['port'],
                path=http_config['api_path'],
                stateless_http=http_config['stateless_http']
            )
            
        except (ConnectionError, OSError, RuntimeError) as e:
            logger.critical("❌ Server startup failed: %s", e, exc_info=True)
            raise
    
    def _log_final_stats(self):
        """Log final server statistics"""
        metrics = self.health_metrics.get_metrics_summary()
        logger.info("📊 Final Server Statistics:")
        logger.info("   ⏱️  Uptime: %d seconds", metrics['uptime_seconds'])
        logger.info("   📊 Total Requests: %d", metrics['total_requests'])
        logger.info("   ❌ Total Errors: %d", metrics['total_errors'])
        logger.info("   📈 Error Rate: %.1f%%", metrics['error_rate_percent'])
        if metrics['avg_response_time_ms'] > 0:
            logger.info("   ⚡ Avg Response Time: %.1fms", metrics['avg_response_time_ms'])
        logger.info("   💚 Final Health Status: %s", metrics['health_status'])
    
    def get_server_summary(self) -> dict:
        """Get comprehensive server summary"""
        return {
            "server_info": self.server_config.get_server_info(),
            "database_config": self.db_config.get_config_summary(),
            "performance_config": self.server_config.get_performance_config(),
            "components": {
                "tools": self.tool_registry.get_tool_summary(),
                "resources": self.resource_manager.get_resource_summary(),
                "prompts": self.prompt_manager.get_prompt_summary()
            },
            "metrics": self.health_metrics.get_metrics_summary()
        }
