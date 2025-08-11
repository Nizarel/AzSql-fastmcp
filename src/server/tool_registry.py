#!/usr/bin/env python3
"""
Tool Registry Module

Handles registration and management of MCP tools with enhanced error handling.
"""

import logging
from typing import Dict, List
from fastmcp import FastMCP, Context
from tools import Tools

logger = logging.getLogger("azure_sql_tool_registry")


class ToolRegistry:
    """Manages MCP tool registration and execution"""
    
    def __init__(self, mcp: FastMCP, tools: Tools):
        """Initialize tool registry"""
        self.mcp = mcp
        self.tools = tools
        self._registered_tools: List[str] = []
        self._health_metrics = None
        
    def register_all_tools(self, health_metrics=None):
        """Register all MCP tools with enhanced error handling - ATOMIC REGISTRATION"""
        
        # Store health_metrics for use in health_check tool
        if health_metrics:
            self._health_metrics = health_metrics
        
        @self.mcp.tool()
        async def list_tables(ctx: Context) -> str:
            """List all tables in the database"""
            try:
                tool = self.tools.get_tool("list_tables")
                return await tool.safe_execute(ctx)
            except Exception as e:
                logger.error(f"Critical error in list_tables: {e}", exc_info=True)
                return f"❌ Critical error listing tables: {str(e)}"
        
        @self.mcp.tool()
        async def describe_table(ctx: Context, table_name: str) -> str:
            """Get table structure and metadata
            
            Args:
                table_name: Name of the table to describe
            """
            try:
                tool = self.tools.get_tool("describe_table")
                return await tool.safe_execute(ctx, table_name=table_name)
            except Exception as e:
                logger.error(f"Critical error in describe_table: {e}", exc_info=True)
                return f"❌ Critical error describing table: {str(e)}"
        
        @self.mcp.tool()
        async def read_data(ctx: Context, query: str = None, limit: int = 100) -> str:
            """Execute SELECT queries with optional limit
            
            Args:
                query: SQL SELECT query to execute (optional)
                limit: Maximum number of rows to return (default: 100)
            """
            try:
                tool = self.tools.get_tool("read_data")
                return await tool.safe_execute(ctx, query=query, limit=limit)
            except Exception as e:
                logger.error(f"Critical error in read_data: {e}", exc_info=True)
                return f"❌ Critical error reading data: {str(e)}"
        
        @self.mcp.tool()
        async def insert_data(ctx: Context, sql: str) -> str:
            """Execute INSERT statements
            
            Args:
                sql: INSERT SQL statement to execute
            """
            try:
                tool = self.tools.get_tool("insert_data")
                return await tool.safe_execute(ctx, sql=sql)
            except Exception as e:
                logger.error(f"Critical error in insert_data: {e}", exc_info=True)
                return f"❌ Critical error inserting data: {str(e)}"
        
        @self.mcp.tool()
        async def update_data(ctx: Context, sql: str) -> str:
            """Execute UPDATE/DELETE statements
            
            Args:
                sql: UPDATE or DELETE SQL statement to execute
            """
            try:
                tool = self.tools.get_tool("update_data")
                return await tool.safe_execute(ctx, sql=sql)
            except Exception as e:
                logger.error(f"Critical error in update_data: {e}", exc_info=True)
                return f"❌ Critical error updating data: {str(e)}"

        @self.mcp.tool()
        async def list_stored_procedures(ctx: Context) -> str:
            """List all stored procedures in the database"""
            try:
                tool = self.tools.get_tool("list_stored_procedures")
                return await tool.safe_execute(ctx)
            except Exception as e:
                logger.error(f"Critical error in list_stored_procedures: {e}", exc_info=True)
                return f"❌ Critical error listing stored procedures: {str(e)}"

        @self.mcp.tool()
        async def execute_stored_procedure(ctx: Context, procedure_name: str, parameters: str = None, schema: str = "dbo") -> str:
            """Execute a stored procedure with optional parameters

            Args:
                procedure_name: Name of the stored procedure to execute
                parameters: JSON string of parameter names and values (optional)
                schema: Schema name (default: dbo)
            """
            try:
                tool = self.tools.get_tool("execute_stored_procedure")
                parsed = {}
                if parameters:
                    try:
                        import json as _json
                        parsed = _json.loads(parameters)
                    except Exception:
                        return "❌ Error: parameters must be a valid JSON object string"
                return await tool.safe_execute(ctx, procedure_name=procedure_name, parameters=parsed, schema=schema)
            except Exception as e:
                logger.error(f"Critical error in execute_stored_procedure: {e}", exc_info=True)
                return f"❌ Critical error executing stored procedure: {str(e)}"
        
        @self.mcp.tool()
        async def database_info(ctx: Context) -> str:
            """Get comprehensive database information and connection status"""
            try:
                conn = ctx.request_context.lifespan_context.get("conn")
                if not conn:
                    return "❌ Database connection unavailable"
                
                factory = ctx.request_context.lifespan_context["factory"]
                config = ctx.request_context.lifespan_context["config"]
                
                info = await factory.test_connection(conn)
                
                # Get counts efficiently
                def get_counts():
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            SELECT 
                                (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE') AS tables,
                                (SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS) AS views
                        """)
                        return cursor.fetchone()
                    finally:
                        cursor.close()
                
                table_count, view_count = await factory.execute_query(conn, get_counts)
                
                return (
                    f"🗄️ Azure SQL Database\n"
                    f"Server: {config.server}\n"
                    f"Database: {info['database_name']}\n"
                    f"Version: {' '.join(info['server_version'].split()[0:4])}\n"
                    f"Tables: {table_count} | Views: {view_count}\n"
                    f"Status: ✅ Connected"
                )
                
            except Exception as e:
                logger.error(f"Database info error: {e}")
                return f"❌ Error: {str(e)}"
        
        @self.mcp.tool()
        async def health_check(ctx: Context) -> str:
            """Comprehensive health check for monitoring and diagnostics"""
            try:
                # Try to get health_metrics from context first, then fallback to stored instance
                health_metrics = ctx.request_context.lifespan_context.get("health_metrics") or self._health_metrics
                
                if health_metrics:
                    return await health_metrics.get_health_check_json(ctx)
                else:
                    # Fallback basic health check
                    conn = ctx.request_context.lifespan_context.get("conn")
                    if conn:
                        return '{"status": "healthy", "database": "connected", "timestamp": "' + str(ctx.request_context.lifespan_context.get("startup_time", "unknown")) + '"}'
                    else:
                        return '{"status": "unhealthy", "database": "disconnected", "error": "No database connection"}'
            except Exception as e:
                logger.error(f"Health check error: {e}")
                return f'{{"status": "unhealthy", "error": "{str(e)}"}}'
        
        @self.mcp.tool()
        async def list_available_tools(ctx: Context) -> str:
            """List all available tools with descriptions"""
            try:
                available_tools = self.tools.list_available_tools()
                tool_list = []
                
                for i, (name, description) in enumerate(available_tools.items(), 1):
                    tool_list.append(f"{i}. **{name}** - {description}")
                
                # Add the management tools
                management_tools = [
                    "database_info - Get database connection information",
                    "health_check - Perform server health check", 
                    "list_available_tools - List all available tools"
                ]
                
                for i, tool in enumerate(management_tools, len(tool_list) + 1):
                    tool_list.append(f"{i}. **{tool}")
                
                return "🛠️ **Available Tools**\n\n" + "\n".join(tool_list)
                
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return f"❌ Error listing tools: {str(e)}"
        
        # Track registered tools - ALL TOOLS REGISTERED ATOMICALLY
        self._registered_tools = [
            "list_tables", "describe_table", "read_data", "insert_data", 
            "update_data", "list_stored_procedures", "execute_stored_procedure",
            "database_info", "health_check", "list_available_tools"
        ]
        
        logger.info(f"✅ Registered {len(self._registered_tools)} tools atomically (including health_check)")
    
    def register_health_tool(self, health_metrics):
        """DEPRECATED: Health tool is now registered in register_all_tools() to prevent race conditions"""
        logger.warning("⚠️ register_health_tool() is deprecated - health_check is now registered atomically in register_all_tools()")
        # Store health_metrics for fallback
        self._health_metrics = health_metrics
    
    def get_registered_tools(self) -> List[str]:
        """Get list of registered tool names"""
        return self._registered_tools.copy()
    
    def get_tool_count(self) -> int:
        """Get number of registered tools"""
        return len(self._registered_tools)
    
    def get_tool_summary(self) -> Dict[str, List[str]]:
        """Get summary of registered tools by category"""
        return {
            "data_operations": ["list_tables", "describe_table", "read_data"],
            "data_modification": ["insert_data", "update_data"], 
            "stored_procedures": ["list_stored_procedures", "execute_stored_procedure"],
            "server_management": ["database_info", "health_check", "list_available_tools"]
        }
