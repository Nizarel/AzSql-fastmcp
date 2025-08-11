#!/usr/bin/env python3
"""
ExecuteStoredProcedure tool for Azure SQL Database MCP Server
"""

import json
from typing import Dict, Any, List
from fastmcp import Context
from .base_tool import BaseTool


class ExecuteStoredProcedure(BaseTool):
    """Tool to execute a stored procedure in the Azure SQL Database"""

    def __init__(self):
        super().__init__(
            name="execute_stored_procedure",
            description="Execute a stored procedure with optional parameters and return results."
        )

    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Execute a stored procedure with optional parameters.

        Args:
            procedure_name: Name of the stored procedure to execute
            parameters: Optional dictionary of parameter names and values
            schema: Optional schema name (default: dbo)
        """
        procedure_name = kwargs.get("procedure_name")
        parameters = kwargs.get("parameters", {})
        schema = kwargs.get("schema", "dbo")

        if not procedure_name:
            return "Error: procedure_name parameter is required"

        try:
            conn = self.get_connection(ctx)

            # Validate procedure exists
            def validate_procedure() -> bool:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM INFORMATION_SCHEMA.ROUTINES
                        WHERE ROUTINE_TYPE = 'PROCEDURE' AND ROUTINE_NAME = ? AND ROUTINE_SCHEMA = ?
                        """,
                        (procedure_name, schema),
                    )
                    row = cursor.fetchone()
                    return bool(row and row[0] > 0)
                finally:
                    cursor.close()

            exists = await self.execute_query(conn, validate_procedure)
            if not exists:
                return f"Error: Stored procedure '{schema}.{procedure_name}' not found"

            # Get parameter metadata
            def get_proc_params() -> List[Dict[str, Any]]:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """
                        SELECT PARAMETER_NAME, DATA_TYPE, PARAMETER_MODE, ORDINAL_POSITION
                        FROM INFORMATION_SCHEMA.PARAMETERS
                        WHERE SPECIFIC_SCHEMA = ? AND SPECIFIC_NAME = ?
                        ORDER BY ORDINAL_POSITION
                        """,
                        (schema, procedure_name),
                    )
                    rows = cursor.fetchall()
                    return [
                        {
                            "name": r[0],
                            "type": r[1],
                            "mode": r[2],
                            "position": r[3],
                        }
                        for r in rows
                    ]
                finally:
                    cursor.close()

            proc_params = await self.execute_query(conn, get_proc_params)

            def exec_proc() -> Dict[str, Any]:
                cursor = conn.cursor()
                try:
                    # Build EXEC statement with parameter binding
                    exec_sql = f"EXEC {schema}.{procedure_name}"
                    param_values: List[Any] = []

                    if parameters and proc_params:
                        valid_param_names = {p["name"] for p in proc_params if p["name"]}
                        invalid = set(parameters.keys()) - valid_param_names
                        if invalid:
                            return {
                                "success": False,
                                "error": f"Invalid parameter(s): {sorted(invalid)}. Valid: {sorted(valid_param_names)}",
                            }

                        assignments = []
                        for p in proc_params:
                            pname = p["name"]
                            if pname and pname in parameters:
                                assignments.append(f"{pname} = ?")
                                param_values.append(parameters[pname])

                        if assignments:
                            exec_sql += " " + ", ".join(assignments)

                    cursor.execute(exec_sql, param_values)

                    result_sets = []
                    while True:
                        if cursor.description:
                            cols = [c[0] for c in cursor.description]
                            rows = cursor.fetchall()
                            result_sets.append({
                                "columns": cols,
                                "rows": [dict(zip(cols, r)) for r in rows],
                                "row_count": len(rows),
                            })
                        if not cursor.nextset():
                            break

                    try:
                        conn.commit()
                    except Exception:
                        pass

                    return {"success": True, "result_sets": result_sets, "exec_sql": exec_sql}
                except Exception as e:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    return {"success": False, "error": str(e)}
                finally:
                    cursor.close()

            result = await self.execute_query(conn, exec_proc)

            if not result.get("success"):
                return f"Stored procedure execution failed: {result.get('error')}"

            # Format output succinctly
            out = []
            out.append(f"Executed {schema}.{procedure_name}")
            if parameters:
                out.append("Parameters: " + json.dumps(parameters))

            if not result["result_sets"]:
                out.append("(No result sets returned)")
                return "\n".join(out)

            for i, rs in enumerate(result["result_sets"], 1):
                out.append(f"Result set {i}: {rs['row_count']} rows")
                if rs["rows"]:
                    # Show first few rows compactly
                    sample = rs["rows"][:5]
                    cols = rs["columns"]
                    out.append(" | ".join(cols))
                    for row in sample:
                        out.append(" | ".join(str(row.get(c, ""))[:40] for c in cols))
                    if rs["row_count"] > 5:
                        out.append(f"... (+{rs['row_count']-5} more)")
            return "\n".join(out)

        except ConnectionError as e:
            return str(e)
        except Exception as e:
            return self.format_error(e)
