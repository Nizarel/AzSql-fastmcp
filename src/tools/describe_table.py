#!/usr/bin/env python3
"""
DescribeTable tool for Azure SQL Database MCP Server
"""

from typing import List, Dict, Any
from fastmcp import Context
from .base_tool import BaseTool


class DescribeTable(BaseTool):
    """Tool to describe the structure of a specific table"""
    
    def __init__(self):
        super().__init__(
            name="describe_table",
            description="Get the structure and schema information of a specific table."
        )
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Get the structure of a specific table.
        
        Args:
            table_name: Name of the table to describe (passed via kwargs)
            
        Returns:
            Column information for the specified table
        """
        table_name = kwargs.get('table_name')
        if not table_name:
            return "Error: table_name parameter is required"
        try:
            conn = self.get_connection(ctx)
            
            def get_table_structure() -> List[Dict[str, Any]]:
                cursor = conn.cursor()
                try:
                    # Use parameterized query to prevent SQL injection
                    cursor.execute("""
                        SELECT 
                            COLUMN_NAME,
                            DATA_TYPE,
                            CHARACTER_MAXIMUM_LENGTH,
                            IS_NULLABLE,
                            COLUMN_DEFAULT,
                            ORDINAL_POSITION
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = ?
                        ORDER BY ORDINAL_POSITION
                    """, (table_name,))
                    
                    columns = []
                    for row in cursor.fetchall():
                        col_name, data_type, max_length, is_nullable, default_val, position = row
                        
                        # Format the column information
                        type_info = data_type
                        if max_length:
                            type_info = f"{data_type}({max_length})"
                        
                        column_info = {
                            "position": position,
                            "name": col_name,
                            "type": type_info,
                            "nullable": is_nullable == "YES",
                            "default": default_val
                        }
                        columns.append(column_info)
                    
                    return columns
                finally:
                    cursor.close()
            
            structure = await self.execute_query(conn, get_table_structure)
            
            if not structure:
                return f"Table '{table_name}' not found or has no columns."
            
            # Format the output
            result = [f"Structure of table '{table_name}':"]
            result.append("-" * 50)
            
            for col in structure:
                nullable_str = "NULL" if col["nullable"] else "NOT NULL"
                default_str = f" DEFAULT {col['default']}" if col["default"] else ""
                result.append(
                    f"{col['position']:2d}. {col['name']} ({col['type']}) {nullable_str}{default_str}"
                )
            
            return "\n".join(result)
            
        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
