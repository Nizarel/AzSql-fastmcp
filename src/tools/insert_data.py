#!/usr/bin/env python3
"""
InsertData tool for Azure SQL Database MCP Server
"""

from typing import Dict, Any
from fastmcp import Context
from .base_tool import BaseTool


class InsertData(BaseTool):
    """Tool to insert data into the Azure SQL Database"""
    
    def __init__(self):
        super().__init__(
            name="insert_data",
            description="Execute INSERT statements to add new data to the database."
        )
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Execute an INSERT SQL statement.
        
        Args:
            sql: The INSERT SQL statement to execute (passed via kwargs)
            
        Returns:
            Result of the insert operation
        """
        sql = kwargs.get('sql')
        if not sql:
            return "Error: sql parameter is required"
        try:
            conn = self.get_connection(ctx)
            
            # Validate that this is an INSERT statement
            if not sql.strip().upper().startswith('INSERT'):
                return "Error: This tool only accepts INSERT statements. Use update_data for UPDATE or read_data for SELECT."
            
            def execute_insert() -> Dict[str, Any]:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql)
                    row_count = cursor.rowcount
                    
                    # Commit the transaction
                    conn.commit()
                    
                    return {
                        "success": True,
                        "rows_affected": row_count,
                        "message": f"INSERT operation completed successfully. {row_count} row(s) inserted."
                    }
                except Exception as e:
                    # Rollback in case of error
                    conn.rollback()
                    return {
                        "success": False,
                        "error": str(e)
                    }
                finally:
                    cursor.close()
            
            result = await self.execute_query(conn, execute_insert)
            
            if result["success"]:
                return result["message"]
            else:
                return f"Insert operation failed: {result['error']}"
            
        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
