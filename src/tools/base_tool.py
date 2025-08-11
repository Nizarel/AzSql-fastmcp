#!/usr/bin/env python3
"""
Base tool class for Azure SQL Database MCP tools
Enhanced with connection management and error handling for production deployments.
"""

import logging
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from fastmcp import Context

logger = logging.getLogger("azure_sql_tools")


class BaseTool(ABC):
    """Base class for all Azure SQL Database tools with enhanced error handling"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._last_connection_check = 0
        self._connection_check_interval = 30  # seconds
    
    def _validate_context(self, ctx: Context) -> bool:
        """Validate that the context is still valid and not closed"""
        try:
            # Check if request context exists and is accessible
            if not hasattr(ctx, 'request_context') or ctx.request_context is None:
                logger.warning("Tool %s: Request context is None", self.name)
                return False
            
            # Check if lifespan context exists
            if not hasattr(ctx.request_context, 'lifespan_context') or ctx.request_context.lifespan_context is None:
                logger.warning("Tool %s: Lifespan context is None", self.name)
                return False
            
            return True
        except (AttributeError, TypeError) as e:
            logger.warning("Tool %s: Context validation failed: %s", self.name, e)
            return False
    
    def get_connection(self, ctx: Context):
        """Get database connection from context with validation"""
        try:
            # Validate context first
            if not self._validate_context(ctx):
                raise ConnectionError("Request context is invalid or closed")
            
            conn = ctx.request_context.lifespan_context.get("conn")
            if conn is None:
                # Try to get connection factory for fresh connection
                factory = self.get_connection_factory(ctx)
                if factory:
                    logger.info(f"Tool {self.name}: Creating new database connection")
                    # Note: This will be synchronous, we'll need async version
                    raise ConnectionError("Primary database connection is not available. Server may be starting up.")
                else:
                    raise ConnectionError("Database connection and factory are not available. Check server logs for details.")
            
            # Check connection health periodically
            current_time = time.time()
            if current_time - self._last_connection_check > self._connection_check_interval:
                self._check_connection_health(conn)
                self._last_connection_check = current_time
            
            return conn
        except Exception as e:
            logger.error(f"Tool {self.name}: Failed to get connection: {e}")
            raise ConnectionError(f"Database connection error: {str(e)}")
    
    def _check_connection_health(self, conn) -> bool:
        """Check if database connection is still healthy"""
        try:
            # Simple health check query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            logger.warning(f"Tool {self.name}: Connection health check failed: {e}")
            return False
    
    def get_connection_factory(self, ctx: Context):
        """Get connection factory from context with validation"""
        try:
            if not self._validate_context(ctx):
                return None
            
            factory = ctx.request_context.lifespan_context.get("factory")
            if factory is None:
                logger.warning(f"Tool {self.name}: Connection factory is not available")
                return None
            return factory
        except Exception as e:
            logger.warning(f"Tool {self.name}: Failed to get connection factory: {e}")
            return None
    
    async def execute_query(self, conn, query_func) -> Any:
        """Execute a database query in a non-blocking way with enhanced error handling"""
        try:
            loop = asyncio.get_event_loop()
            
            # Execute with timeout to prevent hanging
            result = await asyncio.wait_for(
                loop.run_in_executor(None, query_func),
                timeout=30.0  # 30 second timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Tool {self.name}: Query execution timed out after 30 seconds")
            return {"success": False, "error": "Query execution timed out"}
        except Exception as e:
            logger.error(f"Tool {self.name}: Query execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def safe_execute(self, ctx: Context, **kwargs) -> str:
        """Safe wrapper for tool execution with comprehensive error handling"""
        try:
            # Validate context before execution
            if not self._validate_context(ctx):
                return "❌ Error: Request context is invalid or connection was closed by client"
            
            # Execute the actual tool logic
            result = await self.execute(ctx, **kwargs)
            return result
            
        except ConnectionError as e:
            error_msg = f"❌ Database connection error in {self.name}: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except asyncio.TimeoutError:
            error_msg = "❌ Operation timed out in %s" % self.name
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = "❌ Unexpected error in %s: %s" % (self.name, str(e))
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    @abstractmethod
    async def execute(self, ctx: Context, **kwargs) -> str:
        """Execute the tool logic - to be implemented by subclasses"""
        pass
    
    def format_error(self, error: Exception) -> str:
        """Format error message consistently with enhanced details"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Special handling for connection-related errors
        if "ClosedResourceError" in error_type or "closed" in error_msg.lower():
            logger.warning("Tool %s: Client connection was closed: %s", self.name, error_msg)
            return "❌ Connection was closed by client. Operation cancelled."
        
        logger.error("Tool %s: %s: %s", self.name, error_type, error_msg)
        return "❌ Error in %s: %s" % (self.name, error_msg)
