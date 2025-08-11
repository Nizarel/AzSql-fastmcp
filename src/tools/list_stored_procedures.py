#!/usr/bin/env python3
"""
ListStoredProcedures tool for Azure SQL Database MCP Server
"""

from typing import List
from fastmcp import Context
from .base_tool import BaseTool


class ListStoredProcedures(BaseTool):
    """Tool to list all stored procedures in the Azure SQL Database"""

    def __init__(self):
        super().__init__(
            name="list_stored_procedures",
            description="List all stored procedures in the database with schema."
        )

    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        List all stored procedures in the database.

        Returns:
            String containing list of available stored procedures
        """
        try:
            conn = self.get_connection(ctx)

            def get_procedures() -> List[str]:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT ROUTINE_SCHEMA, ROUTINE_NAME
                        FROM INFORMATION_SCHEMA.ROUTINES
                        WHERE ROUTINE_TYPE = 'PROCEDURE'
                        ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME
                        """
                    )
                    procs = [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]
                    return procs
                finally:
                    cursor.close()

            procedures = await self.execute_query(conn, get_procedures)

            if not procedures:
                return "No stored procedures found in the database."

            return f"Available stored procedures ({len(procedures)}): {procedures}"

        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
