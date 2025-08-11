#!/usr/bin/env python3
"""
ReadData tool for Azure SQL Database MCP Server
"""

from typing import Dict, Any
from fastmcp import Context
from .base_tool import BaseTool


class ReadData(BaseTool):
    """Tool to read/query data from the Azure SQL Database"""
    
    def __init__(self):
        super().__init__(
            name="read_data",
            description="Execute SELECT queries to read data from the database."
        )
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Execute a SELECT query to read data from the database.
        
        Args:
            query: The SQL SELECT query to execute (passed via kwargs)
            limit: Maximum number of rows to return (passed via kwargs, default: 100)
            
        Returns:
            The query results as a formatted string
        """
        query = kwargs.get('query')
        limit = kwargs.get('limit', 100)
        try:
            conn = self.get_connection(ctx)
            
            # Use default query if none provided
            if not query:
                query = "SELECT name FROM sys.tables ORDER BY name"
            
            # Add LIMIT if not present in query and it's a SELECT statement
            if query.strip().upper().startswith('SELECT') and 'TOP' not in query.upper() and limit > 0:
                # Insert TOP clause after SELECT
                parts = query.split(' ', 1)
                if len(parts) > 1:
                    query = f"SELECT TOP {limit} {parts[1]}"
            
            def execute_select_query() -> Dict[str, Any]:
                cursor = conn.cursor()
                try:
                    cursor.execute(query)
                    
                    if cursor.description:  # Check if the query returns results
                        columns = [column[0] for column in cursor.description]
                        results = []
                        for row in cursor.fetchall():
                            results.append(dict(zip(columns, row)))
                        
                        return {
                            "success": True,
                            "results": results,
                            "columns": columns,
                            "row_count": len(results)
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Query did not return any results. Use execute_nonquery for INSERT/UPDATE/DELETE operations."
                        }
                except Exception as e:
                    return {"success": False, "error": str(e)}
                finally:
                    cursor.close()
            
            result = await self.execute_query(conn, execute_select_query)
            
            if not result["success"]:
                return f"Query error: {result['error']}"
            
            # Format the results
            if not result["results"]:
                return "Query executed successfully but returned no rows."
            
            # Create a formatted table output
            formatted_output = []
            formatted_output.append(f"Query Results ({result['row_count']} rows):")
            formatted_output.append("=" * 50)
            
            # Add column headers
            columns = result["columns"]
            header = " | ".join(f"{col:15}" for col in columns)
            formatted_output.append(header)
            formatted_output.append("-" * len(header))
            
            # Add data rows (limit to first 20 for readability)
            display_limit = min(20, len(result["results"]))
            for i, row in enumerate(result["results"][:display_limit]):
                row_str = " | ".join(f"{str(row.get(col, ''))[:15]:15}" for col in columns)
                formatted_output.append(row_str)
            
            if len(result["results"]) > display_limit:
                formatted_output.append(f"... and {len(result['results']) - display_limit} more rows")
            
            return "\n".join(formatted_output)
            
        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
