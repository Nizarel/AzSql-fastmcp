# Security Improvements for Azure SQL MCP Server

## 1. **Connection String Security**

````python
# ...existing code...

import os
from typing import Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class DatabaseConfig:
    """Database configuration class with environment variable support"""
    
    def __init__(self, 
                 server: Optional[str] = None,
                 database: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 driver: Optional[str] = None,
                 encrypt: Optional[str] = None,
                 trust_server_certificate: Optional[str] = None,
                 connection_timeout: Optional[int] = None,
                 load_dotenv_file: bool = True,
                 use_key_vault: bool = None):
        """
        Initialize database configuration with Azure Key Vault support.
        
        Args:
            use_key_vault: Whether to use Azure Key Vault for secrets (auto-detected if None)
        """
        # Load environment variables from .env file if requested
        if load_dotenv_file:
            load_dotenv()
        
        # Auto-detect Key Vault usage
        self.use_key_vault = use_key_vault if use_key_vault is not None else bool(os.getenv('AZURE_KEY_VAULT_NAME'))
        
        if self.use_key_vault:
            self._load_from_key_vault()
        else:
            self._load_from_env()
        
        # Ensure server has proper format
        if not self.server.startswith('tcp:'):
            self.server = f"tcp:{self.server}"
    
    def _load_from_key_vault(self):
        """Load secrets from Azure Key Vault"""
        vault_name = os.getenv('AZURE_KEY_VAULT_NAME')
        if not vault_name:
            raise ValueError("AZURE_KEY_VAULT_NAME environment variable is required when using Key Vault")
        
        key_vault_uri = f"https://{vault_name}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_uri, credential=credential)
        
        # Load secrets from Key Vault
        self.server = self._get_secret(client, 'AZURE-SQL-SERVER', os.getenv('AZURE_SQL_SERVER'))
        self.database = self._get_secret(client, 'AZURE-SQL-DATABASE', os.getenv('AZURE_SQL_DATABASE'))
        self.username = self._get_secret(client, 'AZURE-SQL-USERNAME', os.getenv('AZURE_SQL_USERNAME'))
        self.password = self._get_secret(client, 'AZURE-SQL-PASSWORD', os.getenv('AZURE_SQL_PASSWORD'))
        
        # Optional configuration with sensible defaults
        self.driver = os.getenv('AZURE_SQL_DRIVER', 'ODBC Driver 18 for SQL Server')
        self.encrypt = os.getenv('AZURE_SQL_ENCRYPT', 'yes')
        self.trust_server_certificate = os.getenv('AZURE_SQL_TRUST_SERVER_CERTIFICATE', 'no')
        self.connection_timeout = int(os.getenv('AZURE_SQL_CONNECTION_TIMEOUT', '30'))
    
    def _get_secret(self, client: SecretClient, secret_name: str, fallback: Optional[str]) -> str:
        """Get secret from Key Vault with fallback"""
        try:
            secret = client.get_secret(secret_name)
            return secret.value
        except Exception:
            if fallback:
                return fallback
            raise ValueError(f"Required secret '{secret_name}' not found in Key Vault and no fallback provided")
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        self.server = self._get_env_or_fail('AZURE_SQL_SERVER')
        self.database = self._get_env_or_fail('AZURE_SQL_DATABASE')
        self.username = self._get_env_or_fail('AZURE_SQL_USERNAME')
        self.password = self._get_env_or_fail('AZURE_SQL_PASSWORD')
        
        # Optional configuration with sensible defaults
        self.driver = os.getenv('AZURE_SQL_DRIVER', 'ODBC Driver 18 for SQL Server')
        self.encrypt = os.getenv('AZURE_SQL_ENCRYPT', 'yes')
        self.trust_server_certificate = os.getenv('AZURE_SQL_TRUST_SERVER_CERTIFICATE', 'no')
        self.connection_timeout = int(os.getenv('AZURE_SQL_CONNECTION_TIMEOUT', '30'))

# ...existing code...
````

## 2. **Input Validation and SQL Injection Prevention**

````python
#!/usr/bin/env python3
"""
Security Validator Module

Provides comprehensive input validation and SQL injection prevention.
"""

import re
import logging
from typing import List, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SQLOperationType(Enum):
    """SQL operation types for validation"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    TRUNCATE = "TRUNCATE"


class SecurityValidator:
    """Validates SQL queries and inputs for security threats"""
    
    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        r';\s*(DROP|DELETE|TRUNCATE|ALTER|CREATE)\s+',  # Multiple statements
        r'--[^\n]*',  # SQL comments
        r'/\*[\s\S]*?\*/',  # Multi-line comments
        r'xp_cmdshell',  # System commands
        r'sp_executesql',  # Dynamic SQL
        r'EXEC\s*\(',  # Execute statements
        r'EXECUTE\s*\(',  # Execute statements
        r'sys\.[\w]+',  # System tables
        r'INFORMATION_SCHEMA',  # Schema queries (restrict if needed)
        r'UNION\s+ALL\s+SELECT',  # Union attacks
        r'OR\s+1\s*=\s*1',  # Classic injection
        r'OR\s+\'1\'\s*=\s*\'1\'',  # Classic injection
        r'WAITFOR\s+DELAY',  # Time-based attacks
        r'BENCHMARK\s*\(',  # Performance attacks
        r'SLEEP\s*\(',  # Sleep attacks
    ]
    
    # Allowed operations by tool
    TOOL_PERMISSIONS = {
        'read_data': [SQLOperationType.SELECT],
        'insert_data': [SQLOperationType.INSERT],
        'update_data': [SQLOperationType.UPDATE, SQLOperationType.DELETE],
        'describe_table': [SQLOperationType.SELECT],
        'list_tables': [SQLOperationType.SELECT]
    }
    
    @classmethod
    def validate_table_name(cls, table_name: str) -> Tuple[bool, Optional[str]]:
        """Validate table name for security"""
        if not table_name:
            return False, "Table name cannot be empty"
        
        # Check length
        if len(table_name) > 128:  # SQL Server max identifier length
            return False, "Table name too long"
        
        # Allow only alphanumeric, underscore, and dot (for schema.table)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$', table_name):
            return False, "Invalid table name format"
        
        # Check for SQL injection patterns
        table_lower = table_name.lower()
        dangerous_keywords = ['drop', 'delete', 'truncate', 'exec', 'execute', '--', '/*', '*/']
        for keyword in dangerous_keywords:
            if keyword in table_lower:
                return False, f"Table name contains forbidden keyword: {keyword}"
        
        return True, None
    
    @classmethod
    def validate_column_names(cls, columns: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate column names for security"""
        for column in columns:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                return False, f"Invalid column name: {column}"
            
            if len(column) > 128:
                return False, f"Column name too long: {column}"
        
        return True, None
    
    @classmethod
    def validate_sql_query(cls, query: str, tool_name: str) -> Tuple[bool, Optional[str]]:
        """Validate SQL query for security threats"""
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        query_upper = query.upper().strip()
        
        # Determine query type
        query_type = cls._get_query_type(query_upper)
        if not query_type:
            return False, "Unable to determine query type"
        
        # Check tool permissions
        if tool_name in cls.TOOL_PERMISSIONS:
            allowed_types = cls.TOOL_PERMISSIONS[tool_name]
            if query_type not in allowed_types:
                return False, f"Operation {query_type.value} not allowed for tool {tool_name}"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE | re.MULTILINE):
                return False, f"Query contains forbidden pattern: {pattern}"
        
        # Additional checks for specific operations
        if query_type == SQLOperationType.DELETE:
            if 'WHERE' not in query_upper:
                return False, "DELETE statements must include a WHERE clause"
        
        if query_type == SQLOperationType.UPDATE:
            if 'WHERE' not in query_upper:
                return False, "UPDATE statements must include a WHERE clause"
        
        return True, None
    
    @classmethod
    def _get_query_type(cls, query_upper: str) -> Optional[SQLOperationType]:
        """Determine the type of SQL query"""
        for op_type in SQLOperationType:
            if query_upper.startswith(op_type.value):
                return op_type
        return None
    
    @classmethod
    def sanitize_value(cls, value: str) -> str:
        """Sanitize a value for SQL queries"""
        if value is None:
            return 'NULL'
        
        # Escape single quotes
        sanitized = str(value).replace("'", "''")
        
        # Remove any control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        return sanitized
    
    @classmethod
    def validate_limit(cls, limit: int) -> Tuple[bool, Optional[str]]:
        """Validate query limit"""
        if not isinstance(limit, int):
            return False, "Limit must be an integer"
        
        if limit < 1:
            return False, "Limit must be at least 1"
        
        if limit > 10000:  # Maximum allowed limit
            return False, "Limit cannot exceed 10000"
        
        return True, None
````

## 3. **Enhanced Authentication and Authorization**

````python
#!/usr/bin/env python3
"""
Authentication Middleware Module

Provides API key authentication and rate limiting for the MCP server.
"""

import time
import hmac
import hashlib
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication and rate limiting middleware"""
    
    def __init__(self, app, api_keys: Optional[Dict[str, str]] = None, 
                 rate_limit: int = 100, rate_window: int = 60):
        """
        Initialize auth middleware
        
        Args:
            api_keys: Dictionary of API key -> client name (if None, auth is disabled)
            rate_limit: Max requests per window
            rate_window: Time window in seconds
        """
        super().__init__(app)
        self.api_keys = api_keys or {}
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.request_counts = defaultdict(list)
        self.enabled = bool(self.api_keys)
        
        if self.enabled:
            logger.info("Authentication middleware enabled with %d API keys", len(self.api_keys))
        else:
            logger.warning("Authentication middleware disabled - no API keys configured")
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication and rate limiting"""
        # Skip auth for health and metrics endpoints
        if request.url.path in ['/health', '/metrics']:
            return await call_next(request)
        
        # Authenticate if enabled
        if self.enabled:
            auth_result = await self._authenticate(request)
            if not auth_result[0]:
                return JSONResponse(
                    status_code=401,
                    content={"error": auth_result[1]}
                )
            
            # Add client info to request state
            request.state.client_name = auth_result[2]
        
        # Apply rate limiting
        client_id = self._get_client_id(request)
        if not self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # Process request
        response = await call_next(request)
        return response
    
    async def _authenticate(self, request: Request) -> Tuple[bool, str, Optional[str]]:
        """Authenticate request using API key"""
        # Check for API key in header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            # Check Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
        
        if not api_key:
            return False, "API key required", None
        
        # Validate API key (constant-time comparison)
        for stored_key, client_name in self.api_keys.items():
            if hmac.compare_digest(api_key, stored_key):
                return True, "Authenticated", client_name
        
        return False, "Invalid API key", None
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Use authenticated client name if available
        if hasattr(request.state, 'client_name'):
            return request.state.client_name
        
        # Fall back to IP address
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        cutoff = now - self.rate_window
        
        # Clean old requests
        self.request_counts[client_id] = [
            timestamp for timestamp in self.request_counts[client_id]
            if timestamp > cutoff
        ]
        
        # Check limit
        if len(self.request_counts[client_id]) >= self.rate_limit:
            return False
        
        # Record request
        self.request_counts[client_id].append(now)
        return True
````

## 4. **Update Server Core with Security Enhancements**

````python
# ...existing code...

import os
import sys
import json
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastmcp import FastMCP
from tenacity import retry, stop_after_attempt, wait_exponential
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# ...existing imports...

from .auth_middleware import AuthMiddleware

logger = logging.getLogger("azure_sql_server_core")


class ServerCore:
    """Core server class that manages all components and lifecycle with streaming HTTP"""
    
    def __init__(self):
        """Initialize server core with all components"""
        # ...existing code...
        
        # Load API keys from environment or file
        self._load_api_keys()
        
        # Initialize FastMCP with streaming HTTP features (FastMCP 2.9.2+)
        http_config = self.server_config.get_http_config()
        self.mcp = FastMCP(
            name=self.server_config.server_name,
            lifespan=self._lifespan
        )
        
        # Add security middleware
        self._add_security_middleware()
        
        # ...existing code...
    
    def _load_api_keys(self):
        """Load API keys for authentication"""
        self.api_keys = {}
        
        # Load from environment variable (JSON format)
        api_keys_json = os.getenv('MCP_API_KEYS')
        if api_keys_json:
            try:
                self.api_keys = json.loads(api_keys_json)
                logger.info("Loaded %d API keys from environment", len(self.api_keys))
            except json.JSONDecodeError:
                logger.error("Failed to parse MCP_API_KEYS JSON")
        
        # Load from file if specified
        api_keys_file = os.getenv('MCP_API_KEYS_FILE')
        if api_keys_file and os.path.exists(api_keys_file):
            try:
                with open(api_keys_file, 'r') as f:
                    file_keys = json.load(f)
                    self.api_keys.update(file_keys)
                    logger.info("Loaded %d API keys from file", len(file_keys))
            except Exception as e:
                logger.error("Failed to load API keys from file: %s", e)
    
    def _add_security_middleware(self):
        """Add security middleware to the application"""
        # Authentication middleware
        rate_limit = int(os.getenv('MCP_RATE_LIMIT', '100'))
        rate_window = int(os.getenv('MCP_RATE_WINDOW', '60'))
        
        self.mcp.app.add_middleware(
            AuthMiddleware,
            api_keys=self.api_keys,
            rate_limit=rate_limit,
            rate_window=rate_window
        )
        
        # CORS middleware with restricted origins
        allowed_origins = os.getenv('MCP_ALLOWED_ORIGINS', '').split(',')
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        
        if allowed_origins:
            self.mcp.app.add_middleware(
                CORSMiddleware,
                allow_origins=allowed_origins,
                allow_credentials=True,
                allow_methods=["GET", "POST"],
                allow_headers=["X-API-Key", "Authorization", "Content-Type"],
            )
            logger.info("CORS enabled for origins: %s", allowed_origins)
        
        # Trusted host middleware
        allowed_hosts = os.getenv('MCP_ALLOWED_HOSTS', '').split(',')
        allowed_hosts = [host.strip() for host in allowed_hosts if host.strip()]
        
        if allowed_hosts:
            self.mcp.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=allowed_hosts
            )
            logger.info("Trusted hosts: %s", allowed_hosts)

# ...existing code...
````

## 5. **Secure the Read Data Tool**

````python
# ...existing code...

from tools.security_validator import SecurityValidator

class ReadDataTool(BaseTool):
    async def execute(self, ctx: Context, query: str = None, limit: int = 100) -> str:
        """Execute SELECT queries with enhanced security validation"""
        conn = ctx.request_context.lifespan_context.get("conn")
        if not conn:
            return "❌ Database connection unavailable"
        
        factory = ctx.request_context.lifespan_context["factory"]
        
        # Validate limit
        is_valid, error = SecurityValidator.validate_limit(limit)
        if not is_valid:
            return f"❌ Invalid limit: {error}"
        
        if query:
            # Validate custom query
            is_valid, error = SecurityValidator.validate_sql_query(query, 'read_data')
            if not is_valid:
                return f"❌ Query validation failed: {error}"
            
            # Ensure it's a SELECT query
            if not query.strip().upper().startswith('SELECT'):
                return "❌ Only SELECT queries are allowed"
            
            # Apply limit if not already present
            if 'TOP' not in query.upper() and 'LIMIT' not in query.upper():
                query = query.replace('SELECT', f'SELECT TOP {limit}', 1)
        else:
            # List all tables if no query provided
            query = """
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """
        
        # ...existing code...
````

## 6. **Environment Configuration for Azure Container Apps**

Create a secure environment configuration:

````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: azsql-mcp-server
spec:
  template:
    spec:
      containers:
      - name: mcp-server
        image: myregistry.azurecr.io/azsql-mcp:latest
        env:
        # Use Key Vault for secrets
        - name: AZURE_KEY_VAULT_NAME
          value: "mcp-keyvault"
        
        # Security settings
        - name: MCP_ALLOWED_ORIGINS
          value: "https://myapp.azurewebsites.net,https://myotherapp.com"
        - name: MCP_ALLOWED_HOSTS
          value: "azsql-fastmcpserv2.jollyfield-479bc951.eastus2.azurecontainerapps.io"
        - name: MCP_RATE_LIMIT
          value: "100"
        - name: MCP_RATE_WINDOW
          value: "60"
        
        # Force secure connections
        - name: AZURE_SQL_ENCRYPT
          value: "yes"
        - name: AZURE_SQL_TRUST_SERVER_CERTIFICATE
          value: "no"
        
        # Disable debug mode
        - name: MCP_DEBUG_MODE
          value: "false"
        - name: LOG_LEVEL
          value: "WARNING"
        
        # API Keys (better to use Key Vault)
        - name: MCP_API_KEYS
          valueFrom:
            secretKeyRef:
              name: mcp-api-keys
              key: api-keys-json
````

## 7. **Update Requirements**

````txt
# ...existing requirements...

# Security enhancements
azure-identity>=1.15.0
azure-keyvault-secrets>=4.7.0
cryptography>=41.0.0
````

## 8. **Security Best Practices Checklist**

### **Container App Configuration:**
- ✅ Enable HTTPS only
- ✅ Configure IP restrictions
- ✅ Use managed identity for Azure resources
- ✅ Enable container app firewall
- ✅ Configure minimum TLS version (1.2+)

### **Database Security:**
- ✅ Use Azure AD authentication when possible
- ✅ Enable Azure SQL firewall rules
- ✅ Use private endpoints
- ✅ Enable Advanced Threat Protection
- ✅ Regular security assessments

### **Application Security:**
- ✅ API key authentication
- ✅ Rate limiting
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ Secure error handling
- ✅ Audit logging

### **Deployment Security:**
- ✅ Use Azure Key Vault for secrets
- ✅ Container image scanning
- ✅ Regular security updates
- ✅ Network isolation
- ✅ Monitor security alerts

These security enhancements will significantly improve the security posture of your Azure SQL MCP Server. Make sure to test thoroughly in a development environment before deploying to production.