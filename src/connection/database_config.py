#!/usr/bin/env python3
"""
Database Configuration for Azure SQL Database MCP Server
Enhanced with Managed Identity Support
"""

import os
from typing import Optional, Literal
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import TokenCredential


AuthenticationType = Literal["sql", "managed_identity", "default_credential"]


class DatabaseConfig:
    """Database configuration class with enhanced authentication support"""
    
    def __init__(self, 
                 server: Optional[str] = None,
                 database: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 driver: Optional[str] = None,
                 encrypt: Optional[str] = None,
                 trust_server_certificate: Optional[str] = None,
                 connection_timeout: Optional[int] = None,
                 authentication_type: Optional[AuthenticationType] = None,
                 managed_identity_client_id: Optional[str] = None,
                 load_dotenv_file: bool = True):
        """
        Initialize database configuration with support for multiple authentication methods.
        
        Args:
            server: Azure SQL Server hostname (optional)
            database: Database name (optional)
            username: Username (optional, not used for managed identity)
            password: Password (optional, not used for managed identity)
            driver: ODBC driver name (optional)
            encrypt: Encryption setting (optional)
            trust_server_certificate: Trust server certificate setting (optional)
            connection_timeout: Connection timeout in seconds (optional)
            authentication_type: Type of authentication to use
            managed_identity_client_id: Client ID for user-assigned managed identity
            load_dotenv_file: Whether to load .env file automatically (default: True)
        """
        # Load environment variables from .env file if requested
        if load_dotenv_file:
            load_dotenv()
        
        # Basic configuration
        self.server = server or self._get_env_or_fail('AZURE_SQL_SERVER')
        self.database = database or self._get_env_or_fail('AZURE_SQL_DATABASE')
        
        # Authentication configuration
        self.authentication_type = authentication_type or os.getenv('AZURE_SQL_AUTH_TYPE', 'sql')
        self.managed_identity_client_id = managed_identity_client_id or os.getenv('AZURE_MANAGED_IDENTITY_CLIENT_ID')
        
        # SQL Authentication credentials (only required for SQL auth)
        if self.authentication_type == 'sql':
            self.username = username or self._get_env_or_fail('AZURE_SQL_USERNAME')
            self.password = password or self._get_env_or_fail('AZURE_SQL_PASSWORD')
        else:
            self.username = username or os.getenv('AZURE_SQL_USERNAME')
            self.password = password or os.getenv('AZURE_SQL_PASSWORD')
        
        # Optional configuration with sensible defaults
        self.driver = driver or os.getenv('AZURE_SQL_DRIVER', 'ODBC Driver 18 for SQL Server')
        self.encrypt = encrypt or os.getenv('AZURE_SQL_ENCRYPT', 'yes')
        self.trust_server_certificate = trust_server_certificate or os.getenv('AZURE_SQL_TRUST_SERVER_CERTIFICATE', 'no')
        self.connection_timeout = connection_timeout or int(os.getenv('AZURE_SQL_CONNECTION_TIMEOUT', '30'))
        
        # Ensure server has proper format
        if not self.server.startswith('tcp:'):
            self.server = f"tcp:{self.server}"
    
    def _get_env_or_fail(self, env_key: str) -> str:
        """
        Get environment variable or raise an error if not found.
        
        Args:
            env_key: Environment variable name
            
        Returns:
            Environment variable value
            
        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(env_key)
        if not value:
            raise ValueError(
                f"Required environment variable '{env_key}' is not set. "
                f"Please check your .env file or environment variables."
            )
        return value
    
    
    def get_credential(self) -> Optional[TokenCredential]:
        """Get the appropriate Azure credential based on authentication type"""
        if self.authentication_type == 'managed_identity':
            if self.managed_identity_client_id:
                # User-assigned managed identity
                return ManagedIdentityCredential(client_id=self.managed_identity_client_id)
            else:
                # System-assigned managed identity
                return ManagedIdentityCredential()
        elif self.authentication_type == 'default_credential':
            # Use DefaultAzureCredential for development scenarios
            return DefaultAzureCredential()
        else:
            # SQL authentication doesn't use credentials
            return None
    
    def get_connection_string(self) -> str:
        """Get the formatted ODBC connection string based on authentication type"""
        base_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Encrypt={self.encrypt};"
            f"TrustServerCertificate={self.trust_server_certificate};"
            f"Connection Timeout={self.connection_timeout};"
        )
        
        if self.authentication_type == 'sql':
            # Traditional SQL authentication
            return base_string + f"UID={self.username};PWD={self.password};"
        else:
            # Managed identity or default credential authentication - no auth string when using access token
            return base_string
    
    def get_masked_connection_string(self) -> str:
        """Get connection string with masked password for logging"""
        base_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Encrypt={self.encrypt};"
            f"TrustServerCertificate={self.trust_server_certificate};"
            f"Connection Timeout={self.connection_timeout};"
        )
        
        if self.authentication_type == 'sql':
            return base_string + f"UID={self.username};PWD=***MASKED***;"
        else:
            return base_string
    
    def validate(self) -> bool:
        """Validate that all required configuration is present based on authentication type"""
        # Basic validation
        basic_valid = all([
            self.server and self.server.strip(),
            self.database and self.database.strip(),
            self.driver and self.driver.strip()
        ])
        
        if not basic_valid:
            return False
        
        # Authentication-specific validation
        if self.authentication_type == 'sql':
            return all([
                self.username and self.username.strip(),
                self.password and self.password.strip()
            ])
        elif self.authentication_type in ['managed_identity', 'default_credential']:
            # For managed identity, we don't need username/password
            return True
        else:
            return False
    
    def get_config_summary(self) -> dict:
        """Get a summary of the current configuration (without sensitive data)"""
        return {
            "server": self.server,
            "database": self.database,
            "authentication_type": self.authentication_type,
            "username": self.username if self.authentication_type == 'sql' else None,
            "managed_identity_client_id": self.managed_identity_client_id,
            "driver": self.driver,
            "encrypt": self.encrypt,
            "trust_server_certificate": self.trust_server_certificate,
            "connection_timeout": self.connection_timeout,
            "password_set": bool(self.password) if self.authentication_type == 'sql' else False
        }
    
    def __str__(self) -> str:
        """String representation with masked password"""
        if self.authentication_type == 'sql':
            return f"DatabaseConfig(server={self.server}, database={self.database}, username={self.username}, auth=SQL)"
        else:
            return f"DatabaseConfig(server={self.server}, database={self.database}, auth={self.authentication_type})"
    
    def __repr__(self) -> str:
        """Detailed string representation with masked password"""
        if self.authentication_type == 'sql':
            return (
                f"DatabaseConfig("
                f"server='{self.server}', "
                f"database='{self.database}', "
                f"username='{self.username}', "
                f"driver='{self.driver}', "
                f"auth='sql', "
                f"password='***MASKED***')"
            )
        else:
            return (
                f"DatabaseConfig("
                f"server='{self.server}', "
                f"database='{self.database}', "
                f"driver='{self.driver}', "
                f"auth='{self.authentication_type}', "
                f"client_id='{self.managed_identity_client_id}')"
            )
