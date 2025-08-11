#!/usr/bin/env python3
"""
Server Configuration Module

Handles server-specific configuration including streaming HTTP settings,
performance tuning, and environment setup for FastMCP 2.9.2+.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger("azure_sql_server_config")


class ServerConfig:
    """Server configuration management for streaming HTTP transport"""
    
    def __init__(self):
        """Initialize server configuration"""
        # Streaming HTTP Configuration (replaces SSE)
        self.host = os.getenv('MCP_HTTP_HOST', '127.0.0.1')
        self.port = int(os.getenv('MCP_HTTP_PORT', '8000'))
        
        # HTTP transport paths - using FastMCP 2.9.2+ defaults
        self.api_path = os.getenv('MCP_API_PATH', '/mcp')  # Default endpoint for streamable HTTP
        self.health_path = os.getenv('MCP_HEALTH_PATH', '/health')
        self.metrics_path = os.getenv('MCP_METRICS_PATH', '/metrics')
        
        # Streaming configuration
        self.enable_streaming = os.getenv('MCP_ENABLE_STREAMING', 'true').lower() == 'true'
        self.stream_timeout = int(os.getenv('MCP_STREAM_TIMEOUT', '300'))  # 5 minutes
        self.max_stream_size = int(os.getenv('MCP_MAX_STREAM_SIZE', '10485760'))  # 10MB
        
        # Performance Configuration
        self.connection_pool_size = int(os.getenv('CONNECTION_POOL_SIZE', '0'))
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Request tracking configuration
        self.max_request_history = int(os.getenv('MAX_REQUEST_HISTORY', '100'))
        
        # FastMCP 2.9.2+ advanced features
        self.enable_compression = os.getenv('MCP_ENABLE_COMPRESSION', 'true').lower() == 'true'
        self.enable_cors = os.getenv('MCP_ENABLE_CORS', 'true').lower() == 'true'
        self.max_concurrent_requests = int(os.getenv('MCP_MAX_CONCURRENT_REQUESTS', '100'))
        self.json_response = os.getenv('MCP_JSON_RESPONSE', 'false').lower() == 'true'
        self.stateless_http = os.getenv('MCP_STATELESS_HTTP', 'false').lower() == 'true'
        self.debug_mode = os.getenv('MCP_DEBUG_MODE', 'false').lower() == 'true'
        
        # Connection resilience and error handling configuration
        self.connection_timeout = int(os.getenv('MCP_CONNECTION_TIMEOUT', '30'))  # 30 seconds
        self.request_timeout = int(os.getenv('MCP_REQUEST_TIMEOUT', '120'))  # 2 minutes
        self.connection_retry_attempts = int(os.getenv('MCP_CONNECTION_RETRY_ATTEMPTS', '3'))
        self.connection_retry_delay = float(os.getenv('MCP_CONNECTION_RETRY_DELAY', '2.0'))  # seconds
        self.enable_connection_pooling = os.getenv('MCP_ENABLE_CONNECTION_POOLING', 'true').lower() == 'true'
        self.heartbeat_interval = int(os.getenv('MCP_HEARTBEAT_INTERVAL', '60'))  # seconds
        self.graceful_shutdown_timeout = int(os.getenv('MCP_GRACEFUL_SHUTDOWN_TIMEOUT', '30'))  # seconds
        
        # Error recovery configuration
        self.enable_error_recovery = os.getenv('MCP_ENABLE_ERROR_RECOVERY', 'true').lower() == 'true'
        self.max_error_rate = float(os.getenv('MCP_MAX_ERROR_RATE', '0.1'))  # 10% error rate threshold
        self.error_recovery_cooldown = int(os.getenv('MCP_ERROR_RECOVERY_COOLDOWN', '300'))  # 5 minutes
        
        # Server metadata
        self.server_name = "Azure SQL Database MCP Server v3.2"
        self.server_version = "3.2.0"
        
        logger.info("Server config initialized: %s:%d%s", self.host, self.port, self.api_path)
        logger.info("Streaming enabled: %s", self.enable_streaming)
    
    def get_http_config(self) -> Dict[str, Any]:
        """Get HTTP transport configuration for FastMCP 2.9.2+ with enhanced resilience"""
        return {
            'host': self.host,
            'port': self.port,
            'api_path': self.api_path,
            'health_path': self.health_path,
            'metrics_path': self.metrics_path,
            'enable_streaming': self.enable_streaming,
            'stream_timeout': self.stream_timeout,
            'max_stream_size': self.max_stream_size,
            'enable_compression': self.enable_compression,
            'enable_cors': self.enable_cors,
            'max_concurrent_requests': self.max_concurrent_requests,
            'json_response': self.json_response,
            'stateless_http': self.stateless_http,
            'debug_mode': self.debug_mode,
            # Enhanced resilience settings
            'connection_timeout': self.connection_timeout,
            'request_timeout': self.request_timeout,
            'connection_retry_attempts': self.connection_retry_attempts,
            'connection_retry_delay': self.connection_retry_delay,
            'enable_connection_pooling': self.enable_connection_pooling,
            'heartbeat_interval': self.heartbeat_interval,
            'graceful_shutdown_timeout': self.graceful_shutdown_timeout,
            'enable_error_recovery': self.enable_error_recovery,
            'max_error_rate': self.max_error_rate,
            'error_recovery_cooldown': self.error_recovery_cooldown
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-related configuration"""
        return {
            'connection_pool_size': self.connection_pool_size,
            'test_mode': self.test_mode,
            'max_request_history': self.max_request_history,
            'max_concurrent_requests': self.max_concurrent_requests,
            'stream_timeout': self.stream_timeout,
            'max_stream_size': self.max_stream_size,
            'json_response': self.json_response,
            'stateless_http': self.stateless_http,
            'debug_mode': self.debug_mode
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server metadata"""
        return {
            'name': self.server_name,
            'version': self.server_version,
            'host': self.host,
            'port': self.port,
            'transport': 'streaming_http',
            'api_endpoint': f"http://{self.host}:{self.port}{self.api_path}",
            'health_endpoint': f"http://{self.host}:{self.port}{self.health_path}",
            'metrics_endpoint': f"http://{self.host}:{self.port}{self.metrics_path}",
            'streaming_enabled': self.enable_streaming,
            'features': {
                'compression': self.enable_compression,
                'cors': self.enable_cors,
                'json_response': self.json_response,
                'stateless_http': self.stateless_http,
                'debug_mode': self.debug_mode
            }
        }
    
    def validate_config(self) -> bool:
        """Validate server configuration"""
        try:
            # Validate port range
            if not (1 <= self.port <= 65535):
                raise ValueError(f"Invalid port: {self.port}")
            
            # Validate paths
            if not self.api_path.startswith('/'):
                raise ValueError(f"API path must start with '/': {self.api_path}")
            
            if not self.health_path.startswith('/'):
                raise ValueError(f"Health path must start with '/': {self.health_path}")
            
            if not self.metrics_path.startswith('/'):
                raise ValueError(f"Metrics path must start with '/': {self.metrics_path}")
            
            # Validate pool size
            if self.connection_pool_size < 0:
                raise ValueError(f"Connection pool size cannot be negative: {self.connection_pool_size}")
            
            # Validate streaming settings
            if self.stream_timeout <= 0:
                raise ValueError(f"Stream timeout must be positive: {self.stream_timeout}")
            
            if self.max_stream_size <= 0:
                raise ValueError(f"Max stream size must be positive: {self.max_stream_size}")
            
            if self.max_concurrent_requests <= 0:
                raise ValueError(f"Max concurrent requests must be positive: {self.max_concurrent_requests}")
            
            # Validate additional FastMCP 2.9.2+ features
            if not isinstance(self.json_response, bool):
                raise ValueError(f"JSON response must be boolean: {self.json_response}")
            
            if not isinstance(self.stateless_http, bool):
                raise ValueError(f"Stateless HTTP must be boolean: {self.stateless_http}")
            
            if not isinstance(self.debug_mode, bool):
                raise ValueError(f"Debug mode must be boolean: {self.debug_mode}")
            
            # Validate connection resilience and error handling settings
            if self.connection_timeout <= 0:
                raise ValueError(f"Connection timeout must be positive: {self.connection_timeout}")
            
            if self.request_timeout <= 0:
                raise ValueError(f"Request timeout must be positive: {self.request_timeout}")
            
            if self.connection_retry_attempts < 0:
                raise ValueError(f"Connection retry attempts cannot be negative: {self.connection_retry_attempts}")
            
            if self.connection_retry_delay < 0:
                raise ValueError(f"Connection retry delay cannot be negative: {self.connection_retry_delay}")
            
            if self.heartbeat_interval <= 0:
                raise ValueError(f"Heartbeat interval must be positive: {self.heartbeat_interval}")
            
            if self.graceful_shutdown_timeout <= 0:
                raise ValueError(f"Graceful shutdown timeout must be positive: {self.graceful_shutdown_timeout}")
            
            if not isinstance(self.enable_connection_pooling, bool):
                raise ValueError(f"Enable connection pooling must be boolean: {self.enable_connection_pooling}")
            
            if not isinstance(self.enable_error_recovery, bool):
                raise ValueError(f"Enable error recovery must be boolean: {self.enable_error_recovery}")
            
            return True
            
        except ValueError as e:
            logger.error("Configuration validation failed: %s", e)
            return False
