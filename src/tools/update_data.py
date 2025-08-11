#!/usr/bin/env python3
"""
UpdateData tool for Azure SQL Database MCP Server
"""

from typing import Dict, Any
from fastmcp import Context
from .base_tool import BaseTool


class UpdateData(BaseTool):
    """Tool to update and delete data in the Azure SQL Database"""
    
    def __init__(self):
        super().__init__(
            name="update_data",
            description="Execute UPDATE and DELETE statements to modify data in the database."
        )
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Execute an UPDATE or DELETE SQL statement.
        
        Args:
            sql: The UPDATE or DELETE SQL statement to execute (passed via kwargs)
            
        Returns:
            Result of the update/delete operation
        """
        sql = kwargs.get('sql')
        if not sql:
            return "Error: sql parameter is required"
        try:
            conn = self.get_connection(ctx)
            
            # Validate that this is an UPDATE or DELETE statement
            sql_upper = sql.strip().upper()
            if not (sql_upper.startswith('UPDATE') or sql_upper.startswith('DELETE')):
                return "Error: This tool only accepts UPDATE and DELETE statements. Use insert_data for INSERT or read_data for SELECT."
            
            # Safety check for DELETE without WHERE clause
            if sql_upper.startswith('DELETE') and 'WHERE' not in sql_upper:
                return "Error: DELETE statements without WHERE clause are not allowed for safety. Please add a WHERE condition."
            
            def execute_update() -> Dict[str, Any]:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql)
                    row_count = cursor.rowcount
                    
                    # Commit the transaction
                    conn.commit()
                    
                    operation = "UPDATE" if sql_upper.startswith('UPDATE') else "DELETE"
                    return {
                        "success": True,
                        "rows_affected": row_count,
                        "message": f"{operation} operation completed successfully. {row_count} row(s) affected."
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
            
            result = await self.execute_query(conn, execute_update)
            
            if result["success"]:
                return result["message"]
            else:
                return f"Update/Delete operation failed: {result['error']}"
            
        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
