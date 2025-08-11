#!/usr/bin/env python3
"""
SQL Connection Factory for Azure SQL Database MCP Server
Enhanced with connection pooling, retry logic, and managed identity support
"""

import pyodbc
import asyncio
import logging
import os
import struct
from typing import Dict, Any, Optional, Callable
from asyncio import Queue
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import TokenCredential

from .database_config import DatabaseConfig

logger = logging.getLogger(__name__)


class SqlConnectionFactory:
    """Factory class for creating and managing SQL database connections with pooling support"""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize the connection factory with database configuration"""
        self.config = config
        self._connection_pool = None
        self._pool_size = int(os.getenv('CONNECTION_POOL_SIZE', '0'))
        self._pool_initialized = False
        
    async def initialize_pool(self):
        """Initialize connection pool if configured"""
        if self._pool_size > 0 and not self._pool_initialized:
            self._connection_pool = Queue(maxsize=self._pool_size)
            for i in range(self._pool_size):
                try:
                    conn = await self.create_connection()
                    await self._connection_pool.put(conn)
                    logger.info(f"Pool connection {i+1}/{self._pool_size} created")
                except Exception as e:
                    logger.error(f"Failed to create pool connection {i+1}: {e}")
            
            self._pool_initialized = True
            logger.info(f"Connection pool initialized with {self._connection_pool.qsize()} connections")
    
    @asynccontextmanager
    async def get_pooled_connection(self):
        """Get connection from pool with automatic return"""
        if not self._connection_pool or self._pool_size == 0:
            # If pooling is not enabled, create a new connection
            conn = await self.create_connection()
            try:
                yield conn
            finally:
                await self.close_connection(conn)
        else:
            # Get from pool
            conn = await self._connection_pool.get()
            try:
                # Validate connection is still alive
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                yield conn
            except Exception as e:
                logger.warning(f"Pool connection invalid, creating new one: {e}")
                # Connection is dead, create a new one
                try:
                    conn.close()
                except:
                    pass
                conn = await self.create_connection()
                yield conn
            finally:
                # Return to pool
                try:
                    await self._connection_pool.put(conn)
                except:
                    # If we can't return it, close it
                    try:
                        conn.close()
                    except:
                        pass
    
    def _create_connection_string(self) -> str:
        """Create the connection string from configuration with authentication support"""
        base_connection_string = (
            f"DRIVER={{{self.config.driver}}};"
            f"SERVER={self.config.server};"  # Server already has tcp: prefix from config
            f"DATABASE={self.config.database};"
            f"Encrypt={self.config.encrypt};"
            f"TrustServerCertificate={self.config.trust_server_certificate};"
            f"Connection Timeout={self.config.connection_timeout};"
            "Application Name=Azure SQL MCP Server v4.0"
        )
        
        if self.config.authentication_type == 'sql':
            # Traditional SQL authentication
            return base_connection_string + f";UID={self.config.username};PWD={self.config.password}"
        else:
            # Managed identity authentication - don't include Authentication when using access token
            return base_connection_string
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def create_connection(self) -> pyodbc.Connection:
        """
        Create a new database connection with retry logic and authentication support.
        
        Returns:
            pyodbc.Connection: Active database connection
            
        Raises:
            ConnectionError: If connection cannot be established after retries
        """
        loop = asyncio.get_event_loop()
        
        def connect():
            try:
                conn_string = self._create_connection_string()
                logger.debug(f"Attempting database connection with auth type: {self.config.authentication_type}")
                
                if self.config.authentication_type in ['managed_identity', 'default_credential']:
                    # For managed identity, we need to get the token and use it in connection
                    token = asyncio.run(self._get_managed_identity_token())
                    if token:
                        # Create connection with token
                        token_struct = self._create_token_struct(token)
                        # Set up connection attributes for token authentication
                        attrs_before = {
                            1256: token_struct  # SQL_COPT_SS_ACCESS_TOKEN = 1256
                        }
                        conn = pyodbc.connect(conn_string, attrs_before=attrs_before)
                    else:
                        # Fallback to connection string based auth
                        conn = pyodbc.connect(conn_string)
                else:
                    # Traditional SQL authentication
                    conn = pyodbc.connect(conn_string)
                
                conn.timeout = self.config.connection_timeout
                conn.autocommit = True
                return conn
            except pyodbc.Error as e:
                logger.error(f"Database connection failed: {str(e)}")
                raise ConnectionError(f"Failed to connect to database: {str(e)}")
        
        try:
            # Run the blocking connection in thread pool
            connection = await loop.run_in_executor(None, connect)
            logger.info(f"Database connection established successfully using {self.config.authentication_type} authentication")
            return connection
        except Exception as e:
            logger.error(f"Connection creation failed after retries: {str(e)}")
            raise
    
    async def test_connection(self, conn: pyodbc.Connection) -> Dict[str, Any]:
        """
        Test the database connection and retrieve server information.
        
        Args:
            conn: Active database connection
            
        Returns:
            Dictionary containing database information
        """
        loop = asyncio.get_event_loop()
        
        def get_db_info():
            cursor = conn.cursor()
            try:
                # Get database name
                cursor.execute("SELECT DB_NAME()")
                db_name = cursor.fetchone()[0]
                
                # Get server version
                cursor.execute("SELECT @@VERSION")
                server_version = cursor.fetchone()[0]
                
                # Get additional Azure SQL info
                cursor.execute("""
                    SELECT 
                        SERVERPROPERTY('Edition') as edition,
                        SERVERPROPERTY('ProductLevel') as product_level,
                        SERVERPROPERTY('ResourceVersion') as resource_version
                """)
                azure_info = cursor.fetchone()
                
                return {
                    "database_name": db_name,
                    "server_version": server_version,
                    "edition": azure_info[0] if azure_info else "Unknown",
                    "product_level": azure_info[1] if azure_info else "Unknown",
                    "resource_version": azure_info[2] if azure_info else "Unknown"
                }
            finally:
                cursor.close()
        
        return await loop.run_in_executor(None, get_db_info)
    
    async def execute_query(self, conn: pyodbc.Connection, query_func: Callable) -> Any:
        """
        Execute a query function asynchronously.
        
        Args:
            conn: Database connection
            query_func: Function that executes the query
            
        Returns:
            Query results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, query_func)
    
    async def close_connection(self, conn: pyodbc.Connection) -> None:
        """
        Close a database connection.
        
        Args:
            conn: Connection to close
        """
        if conn:
            loop = asyncio.get_event_loop()
            
            def close():
                try:
                    conn.close()
                    logger.debug("Database connection closed")
                except Exception as e:
                    logger.error(f"Error closing connection: {str(e)}")
            
            await loop.run_in_executor(None, close)
    
    async def cleanup_pool(self):
        """Clean up all pooled connections"""
        if self._connection_pool and self._pool_initialized:
            logger.info("Cleaning up connection pool...")
            while not self._connection_pool.empty():
                try:
                    conn = await self._connection_pool.get_nowait()
                    await self.close_connection(conn)
                except:
                    pass
            self._pool_initialized = False
            logger.info("Connection pool cleaned up")
    
    async def _get_managed_identity_token(self) -> Optional[str]:
        """
        Get access token from managed identity for Azure SQL authentication.
        
        Returns:
            Access token string or None if not using managed identity
        """
        if self.config.authentication_type not in ['managed_identity', 'default_credential']:
            return None
        
        try:
            credential = self.config.get_credential()
            if credential:
                # Azure SQL Database resource URL
                scope = "https://database.windows.net/.default"
                token = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: credential.get_token(scope)
                )
                logger.info("Successfully acquired managed identity token")
                return token.token
        except Exception as e:
            logger.error(f"Failed to acquire managed identity token: {e}")
            raise ConnectionError(f"Managed identity authentication failed: {e}")
        
        return None

    def _create_token_struct(self, token: str) -> bytes:
        """
        Create the token structure required for SQL Server authentication.
        
        Args:
            token: Access token string
            
        Returns:
            Token structure as bytes
        """
        token_bytes = token.encode('utf-16-le')
        token_length = len(token_bytes)
        
        # Create the token structure for SQL Server
        # Format: token length (4 bytes) + token bytes
        token_struct = struct.pack(f'<I{token_length}s', token_length, token_bytes)
        return token_struct

    @staticmethod
    def list_available_drivers() -> list:
        """
        List available ODBC drivers on the system.
        
        Returns:
            List of available ODBC driver names
        """
        try:
            return pyodbc.drivers()
        except Exception as e:
            logger.error(f"Error listing ODBC drivers: {str(e)}")
            return []
    
    def __str__(self) -> str:
        """String representation of the factory"""
        return f"SqlConnectionFactory(config={self.config}, pool_size={self._pool_size})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"SqlConnectionFactory(config={repr(self.config)}, pool_size={self._pool_size})"