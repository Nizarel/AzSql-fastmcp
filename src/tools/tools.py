#!/usr/bin/env python3
"""
Tools management module for Azure SQL Database MCP Server
"""

import logging
from typing import Dict
from fastmcp import Context
from .base_tool import BaseTool
from .list_tables import ListTables
from .describe_table import DescribeTable
from .read_data import ReadData
from .insert_data import InsertData
from .update_data import UpdateData
from .list_stored_procedures import ListStoredProcedures
from .execute_stored_procedure import ExecuteStoredProcedure


logger = logging.getLogger("azure_sql_tools")


class Tools:
    """Main tools manager class that handles all database operations"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
    # imports moved to module level to avoid indentation issues
        
        # Register individual tools
        tools_to_register = [
            ListTables(),
            DescribeTable(),
            ReadData(),
            InsertData(),
            UpdateData(),
            ListStoredProcedures(),
            ExecuteStoredProcedure()
        ]
        
        for tool in tools_to_register:
            self.tools[tool.name] = tool
            logger.debug(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found. Available tools: {list(self.tools.keys())}")
        return self.tools[name]
    
    def list_available_tools(self) -> Dict[str, str]:
        """Get a dictionary of all available tools and their descriptions"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    async def execute_tool(self, tool_name: str, ctx: Context, **kwargs) -> str:
        """Execute a specific tool"""
        try:
            tool = self.get_tool(tool_name)
            return await tool.execute(ctx, **kwargs)
        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    # Convenience methods for direct tool access
    async def list_tables(self, ctx: Context) -> str:
        """List all tables in the database"""
        return await self.execute_tool("list_tables", ctx)
    
    async def describe_table(self, ctx: Context, table_name: str) -> str:
        """Describe the structure of a table"""
        return await self.execute_tool("describe_table", ctx, table_name=table_name)
    
    async def read_data(self, ctx: Context, query: str = None, limit: int = 100) -> str:
        """Read data from the database"""
        return await self.execute_tool("read_data", ctx, query=query, limit=limit)
    
    async def insert_data(self, ctx: Context, sql: str) -> str:
        """Insert data into the database"""
        return await self.execute_tool("insert_data", ctx, sql=sql)
    
    async def update_data(self, ctx: Context, sql: str) -> str:
        """Update or delete data in the database"""
        return await self.execute_tool("update_data", ctx, sql=sql)

    async def list_stored_procedures(self, ctx: Context) -> str:
        """List all stored procedures in the database"""
        return await self.execute_tool("list_stored_procedures", ctx)

    async def execute_stored_procedure(self, ctx: Context, procedure_name: str, parameters: dict = None, schema: str = "dbo") -> str:
        """Execute a stored procedure with optional parameters"""
        return await self.execute_tool(
            "execute_stored_procedure", ctx,
            procedure_name=procedure_name,
            parameters=parameters or {},
            schema=schema,
        )
