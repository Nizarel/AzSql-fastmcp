
## Environment Variables for azsql-xyzmcpserv2

**Database Configuration:**
- `AZURE_SQL_SERVER`: xyzmcpserv2.database.windows.net
- `AZURE_SQL_DATABASE`: xyzmcpserv2db-dev
- `AZURE_SQL_DRIVER`: ODBC Driver 18 for SQL Server
- `AZURE_SQL_ENCRYPT`: yes
- `AZURE_SQL_TRUST_SERVER_CERTIFICATE`: no
- `AZURE_SQL_CONNECTION_TIMEOUT`: 120
- `AZURE_SQL_AUTH_TYPE`: managed_identity
- `AZURE_MANAGED_IDENTITY_CLIENT_ID`: xxxx

**Application Configuration:**
- `LOG_LEVEL`: INFO
- `CONNECTION_POOL_SIZE`: 0
- `TEST_MODE`: false

**MCP Server Configuration:**
- `MCP_TRANSPORT`: http
- `MCP_HTTP_HOST`: 0.0.0.0
- `MCP_HTTP_PORT`: 8080
- `MCP_API_PATH`: /mcp
- `MCP_ENABLE_COMPRESSION`: true
- `MCP_ENABLE_CORS`: true
- `MCP_MAX_CONCURRENT_REQUESTS`: 30
- `MCP_JSON_RESPONSE`: true
- `MCP_STATELESS_HTTP`: true
- `MCP_DEBUG_MODE`: true
- `MCP_HEALTH_PATH`: /health
- `MCP_METRICS_PATH`: /metrics
