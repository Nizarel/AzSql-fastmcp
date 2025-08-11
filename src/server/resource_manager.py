#!/usr/bin/env python3
"""
Resource Manager Module

Handles registration and management of MCP resources for database schemas and status.
"""

import json
import logging
from datetime import datetime
from fastmcp import FastMCP
from connection import SqlConnectionFactory

logger = logging.getLogger("azure_sql_resource_manager")


class ResourceManager:
    """Manages MCP resource registration and data exposure"""
    
    def __init__(self, mcp: FastMCP, connection_factory: SqlConnectionFactory):
        """Initialize resource manager"""
        self.mcp = mcp
        self.connection_factory = connection_factory
        self._registered_resources = []
        
    def register_all_resources(self):
        """Register all MCP resources for database schemas and status"""
        
        @self.mcp.resource("database://schema")
        async def get_database_schema() -> str:
            """Expose complete database schema as a resource
            
            Returns comprehensive schema information including tables, columns,
            data types, and constraints in JSON format.
            """
            try:
                conn = await self.connection_factory.create_connection()
                cursor = conn.cursor()
                
                # Get comprehensive schema information
                cursor.execute("""
                    SELECT 
                        t.TABLE_NAME,
                        c.COLUMN_NAME,
                        c.DATA_TYPE,
                        c.IS_NULLABLE,
                        c.CHARACTER_MAXIMUM_LENGTH,
                        c.NUMERIC_PRECISION,
                        c.NUMERIC_SCALE,
                        c.ORDINAL_POSITION,
                        c.COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.TABLES t
                    JOIN INFORMATION_SCHEMA.COLUMNS c 
                        ON t.TABLE_NAME = c.TABLE_NAME
                    WHERE t.TABLE_TYPE = 'BASE TABLE'
                    ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
                """)
                
                schema = {}
                for row in cursor:
                    table = row[0]
                    if table not in schema:
                        schema[table] = {"columns": [], "metadata": {}}
                    
                    column_info = {
                        'name': row[1],
                        'type': row[2],
                        'nullable': row[3] == 'YES',
                        'position': row[7]
                    }
                    
                    # Add optional properties
                    if row[4]:  # max_length
                        column_info['max_length'] = row[4]
                    if row[5]:  # numeric_precision
                        column_info['precision'] = row[5]
                    if row[6]:  # numeric_scale
                        column_info['scale'] = row[6]
                    if row[8]:  # default_value
                        column_info['default'] = row[8]
                    
                    schema[table]["columns"].append(column_info)
                
                # Get table metadata (row counts, etc.)
                for table_name in schema.keys():
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                        row_count = cursor.fetchone()[0]
                        schema[table_name]["metadata"]["row_count"] = row_count
                    except Exception as e:
                        schema[table_name]["metadata"]["row_count_error"] = str(e)
                
                cursor.close()
                await self.connection_factory.close_connection(conn)
                
                # Add metadata
                schema_result = {
                    "generated_at": datetime.now().isoformat(),
                    "table_count": len(schema),
                    "tables": schema
                }
                
                return json.dumps(schema_result, indent=2)
                
            except Exception as e:
                logger.error(f"Error getting schema: {e}")
                return json.dumps({
                    "error": str(e),
                    "generated_at": datetime.now().isoformat()
                })
        
        @self.mcp.resource("database://status")
        async def get_database_status() -> str:
            """Real-time database connection status and performance metrics
            
            Returns current connection information, database metrics,
            and system status in JSON format.
            """
            try:
                conn = await self.connection_factory.create_connection()
                info = await self.connection_factory.test_connection(conn)
                
                # Get additional metrics
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        DB_NAME() as current_database,
                        SUSER_NAME() as current_user,
                        @@VERSION as version_info,
                        @@SERVERNAME as server_name
                """)
                metrics = cursor.fetchone()
                
                # Get database size information
                cursor.execute("""
                    SELECT 
                        SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS bigint) * 8192.) / 1024 / 1024 as size_mb
                    FROM sys.database_files
                    WHERE type IN (0,1)
                """)
                size_result = cursor.fetchone()
                db_size_mb = size_result[0] if size_result and size_result[0] else 0
                
                cursor.close()
                await self.connection_factory.close_connection(conn)
                
                status_result = {
                    'status': 'connected',
                    'timestamp': datetime.now().isoformat(),
                    'connection_info': {
                        'database': info['database_name'],
                        'server': metrics[3] if metrics else 'unknown',
                        'current_user': metrics[1] if metrics else 'unknown'
                    },
                    'version_info': {
                        'server_version': info['server_version'],
                        'full_version': metrics[2] if metrics else info['server_version']
                    },
                    'database_metrics': {
                        'size_mb': round(db_size_mb, 2),
                        'connection_test': 'passed'
                    }
                }
                
                return json.dumps(status_result, indent=2)
                
            except Exception as e:
                logger.error(f"Error getting database status: {e}")
                return json.dumps({
                    'status': 'disconnected',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'connection_test': 'failed'
                }, indent=2)
        
        @self.mcp.resource("database://tables")
        async def get_table_list() -> str:
            """Get a simple list of all tables with basic information
            
            Returns a lightweight JSON list of tables with row counts
            and basic metadata for quick reference.
            """
            try:
                conn = await self.connection_factory.create_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        TABLE_NAME,
                        TABLE_TYPE
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE IN ('BASE TABLE', 'VIEW')
                    ORDER BY TABLE_TYPE, TABLE_NAME
                """)
                
                tables = []
                for row in cursor:
                    table_info = {
                        'name': row[0],
                        'type': row[1]
                    }
                    
                    # Get row count for base tables only
                    if row[1] == 'BASE TABLE':
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM [{row[0]}]")
                            table_info['row_count'] = cursor.fetchone()[0]
                        except:
                            table_info['row_count'] = 'unknown'
                    
                    tables.append(table_info)
                
                cursor.close()
                await self.connection_factory.close_connection(conn)
                
                result = {
                    'generated_at': datetime.now().isoformat(),
                    'total_objects': len(tables),
                    'tables': [t for t in tables if t['type'] == 'BASE TABLE'],
                    'views': [t for t in tables if t['type'] == 'VIEW']
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                logger.error(f"Error getting table list: {e}")
                return json.dumps({
                    'error': str(e),
                    'generated_at': datetime.now().isoformat()
                })
        
        # Track registered resources
        self._registered_resources = [
            "database://schema",
            "database://status", 
            "database://tables"
        ]
        
        logger.info(f"✅ Registered {len(self._registered_resources)} resources")
    
    def get_registered_resources(self) -> list:
        """Get list of registered resource URIs"""
        return self._registered_resources.copy()
    
    def get_resource_count(self) -> int:
        """Get number of registered resources"""
        return len(self._registered_resources)
    
    def get_resource_summary(self) -> dict:
        """Get summary of available resources"""
        return {
            "total_resources": len(self._registered_resources),
            "resources": {
                "database://schema": "Complete database schema with all tables and columns",
                "database://status": "Real-time database connection and performance status",
                "database://tables": "Simple list of tables and views with row counts"
            }
        }
