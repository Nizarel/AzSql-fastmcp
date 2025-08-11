# Azure SQL MCP Server - Modular Architecture

## Overview

The Azure SQL MCP Server has been refactored into a modular architecture to improve maintainability, scalability, and testability. The new design separates concerns into dedicated modules, making the codebase more organized and easier to extend.

## Architecture Components

### 1. **Server Package** (`src/server/`)

The main server package contains all the modular components:

```
src/server/
├── __init__.py          # Package exports
├── core.py              # Main server orchestration
├── config.py            # Server configuration management
├── metrics.py           # Health monitoring and metrics
├── tool_registry.py     # MCP tool registration
├── resource_manager.py  # MCP resource management
└── prompt_manager.py    # MCP prompt management
```

### 2. **Core Components**

#### **ServerCore** (`core.py`)
- **Purpose**: Main orchestration class that manages all components
- **Responsibilities**:
  - Initialize and coordinate all modules
  - Manage FastMCP instance and lifecycle
  - Handle database connection with retry logic
  - Coordinate component registration
  - Manage server startup and shutdown

#### **ServerConfig** (`config.py`)
- **Purpose**: Centralized server configuration management
- **Features**:
  - SSE transport configuration
  - Performance and pool settings
  - Environment variable management
  - Configuration validation
  - Server metadata management

#### **HealthMetrics** (`metrics.py`)
- **Purpose**: Health monitoring and performance tracking
- **Features**:
  - Request count and timing tracking
  - Error rate monitoring
  - Health status determination
  - Comprehensive health checks
  - Performance metrics collection

#### **ToolRegistry** (`tool_registry.py`)
- **Purpose**: MCP tool registration and management
- **Features**:
  - Centralized tool registration
  - Enhanced error handling for all tools
  - Tool categorization and summary
  - Health check tool integration

#### **ResourceManager** (`resource_manager.py`)
- **Purpose**: MCP resource registration and data exposure
- **Features**:
  - Database schema resource
  - Real-time status resource
  - Table listing resource
  - Comprehensive metadata exposure

#### **PromptManager** (`prompt_manager.py`)
- **Purpose**: MCP prompt registration for interactive operations
- **Features**:
  - SQL query builder prompts
  - Performance analysis guides
  - Migration assistance prompts
  - Troubleshooting guides

## Benefits of Modular Architecture

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Easier to understand and maintain individual components
- Reduced coupling between different functionalities

### 2. **Enhanced Testability**
- Individual modules can be tested in isolation
- Mock dependencies easily for unit testing
- Clear interfaces between components

### 3. **Improved Scalability**
- Easy to add new tools, resources, or prompts
- Modular components can be extended independently
- Clear extension points for future features

### 4. **Better Error Handling**
- Centralized error handling in each module
- Consistent error reporting across components
- Enhanced debugging capabilities

### 5. **Configuration Management**
- Centralized configuration with validation
- Environment-specific settings
- Easy to modify server behavior

## Usage Examples

### Basic Server Startup
```python
from server.core import ServerCore

# Initialize and run server
server = ServerCore()
server.run()  # Synchronous
# or
await server.run_async()  # Asynchronous
```

### Individual Component Usage
```python
from server.config import ServerConfig
from server.metrics import HealthMetrics
from server.tool_registry import ToolRegistry

# Use individual components
config = ServerConfig()
metrics = HealthMetrics()
# ... etc
```

### Server Summary
```python
server = ServerCore()
summary = server.get_server_summary()
print(summary)
```

## Component Interactions

```
┌─────────────┐
│ ServerCore  │ ◄─── Main orchestrator
└─────┬───────┘
      │
      ├── ServerConfig      (Configuration)
      ├── HealthMetrics     (Monitoring)
      ├── ToolRegistry      (MCP Tools)
      ├── ResourceManager   (MCP Resources)
      ├── PromptManager     (MCP Prompts)
      ├── Tools             (Business Logic)
      └── ConnectionFactory (Database)
```

## Migration from Legacy Code

### What Changed
1. **Monolithic `AzureSQLMCPServer`** → **Modular `ServerCore`**
2. **Inline tool registration** → **Dedicated `ToolRegistry`**
3. **Mixed configuration** → **Centralized `ServerConfig`**
4. **Basic health checks** → **Comprehensive `HealthMetrics`**
5. **Inline resources/prompts** → **Dedicated managers**

### Backward Compatibility
- The main `server.py` interface remains the same
- Environment variables and configuration stay the same
- All existing functionality is preserved
- API endpoints and behavior unchanged

## Extension Points

### Adding New Tools
```python
# In tool_registry.py
@self.mcp.tool()
async def new_tool(ctx: Context, param: str) -> str:
    """New tool description"""
    try:
        # Tool implementation
        return result
    except Exception as e:
        logger.error(f"Error in new_tool: {e}")
        return f"❌ Error: {str(e)}"
```

### Adding New Resources
```python
# In resource_manager.py
@self.mcp.resource("database://new_resource")
async def get_new_resource() -> str:
    """New resource description"""
    # Resource implementation
    return json.dumps(data, indent=2)
```

### Adding New Prompts
```python
# In prompt_manager.py
@self.mcp.prompt("new_prompt")
async def new_prompt(param: str = None) -> str:
    """New prompt description"""
    # Prompt implementation
    return prompt_content
```

## Configuration Options

### Environment Variables
```bash
# Server Configuration
MCP_SSE_HOST=127.0.0.1
MCP_SSE_PORT=8000
MCP_SSE_PATH=/sse
MCP_MESSAGE_PATH=/message

# Performance Configuration
CONNECTION_POOL_SIZE=5
MAX_REQUEST_HISTORY=100
TEST_MODE=false

# Logging
LOG_LEVEL=INFO
```

### Server Configuration Methods
```python
config = ServerConfig()

# Get configurations
sse_config = config.get_sse_config()
perf_config = config.get_performance_config()
server_info = config.get_server_info()

# Validate configuration
is_valid = config.validate_config()
```

## Monitoring and Health

### Health Metrics
```python
metrics = HealthMetrics()

# Track requests
metrics.track_request(duration=0.5, success=True)

# Get metrics
uptime = metrics.get_uptime_seconds()
avg_time = metrics.get_average_response_time_ms()
error_rate = metrics.get_error_rate()
health_status = metrics.get_health_status()

# Perform health check
health_data = await metrics.perform_health_check(ctx)
```

### Available Health Endpoints
- **Tool**: `health_check` - JSON health status
- **Resource**: `database://status` - Database connection status
- **Metrics**: Request counting, timing, error tracking

## Best Practices

### 1. **Module Organization**
- Keep modules focused on single responsibilities
- Use clear, descriptive module and class names
- Document public interfaces thoroughly

### 2. **Error Handling**
- Use consistent error handling patterns
- Log errors with appropriate levels
- Return user-friendly error messages

### 3. **Configuration**
- Use environment variables for configuration
- Validate configuration on startup
- Provide sensible defaults

### 4. **Testing**
- Test modules independently
- Use dependency injection for testability
- Mock external dependencies

### 5. **Documentation**
- Document all public methods and classes
- Provide usage examples
- Keep architecture documentation current

## Future Enhancements

### Planned Improvements
1. **Plugin System**: Dynamic tool/resource loading
2. **Middleware Support**: Request/response processing pipeline
3. **Caching Layer**: Result caching for performance
4. **Event System**: Component communication via events
5. **Configuration UI**: Web-based configuration interface

### Extension Opportunities
1. **Multiple Database Support**: PostgreSQL, MySQL adapters
2. **Authentication Modules**: OAuth, JWT, API key support
3. **Monitoring Integrations**: Prometheus, Grafana support
4. **Backup/Restore Tools**: Automated backup management
5. **Schema Migration Tools**: Database evolution support

## Conclusion

The modular architecture provides a solid foundation for the Azure SQL MCP Server, making it more maintainable, testable, and extensible. Each component has clear responsibilities and interfaces, enabling independent development and testing while maintaining the cohesive functionality of the overall system.
