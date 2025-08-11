#!/usr/bin/env python3
"""
ListTables tool for Azure SQL Database MCP Server
"""

from typing import List
from fastmcp import Context
from .base_tool import BaseTool


class ListTables(BaseTool):
    """Tool to list all tables in the Azure SQL Database"""
    
    def __init__(self):
        super().__init__(
            name="list_tables",
            description="List all tables in the database that can be queried."
        )
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        List all tables in the database.
        
        Returns:
            String containing list of available tables
        """
        try:
            conn = self.get_connection(ctx)
            
            def get_tables() -> List[str]:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        SELECT TABLE_NAME 
                        FROM INFORMATION_SCHEMA.TABLES 
                        WHERE TABLE_TYPE='BASE TABLE'
                        ORDER BY TABLE_NAME
                    """)
                    tables = [row[0] for row in cursor.fetchall()]
                    return tables
                finally:
                    cursor.close()
            
            tables = await self.execute_query(conn, get_tables)
            
            if not tables:
                return "No tables found in the database."
            
            return f"Available tables ({len(tables)}): {tables}"
            
        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
