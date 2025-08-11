# Azure SQL MCP Agentic Client Documentation

## Overview

The **Azure SQL MCP Agentic Client** is a comprehensive Python client library designed for building intelligent agentic solutions that interact with Azure SQL databases through the Model Context Protocol (MCP). It provides high-level abstractions for database operations, intelligent query building, and autonomous data analysis.

## Features

### 🤖 Intelligent Agent Capabilities
- **Database Exploration**: Automatically discover and understand database schemas
- **Natural Language Processing**: Convert business questions to SQL queries
- **Autonomous Analysis**: Generate insights and recommendations
- **Error Handling**: Robust error recovery and reporting
- **Performance Monitoring**: Track query performance and health metrics

### 🛠️ Core Functionality
- **All MCP Tools**: Access to 8 database tools (list tables, describe, read, insert, update, etc.)
- **Resources**: Real-time access to database schema, status, and metadata
- **Prompts**: Interactive assistance for SQL building and optimization
- **Batch Operations**: Execute multiple queries efficiently
- **Health Monitoring**: Comprehensive server and database health checks

## Quick Start

### Installation

```bash
# Install FastMCP client
pip install fastmcp

# Or install from requirements
pip install -r client_requirements.txt
```

### Basic Usage

```python
import asyncio
from agentic_sql_client import AgenticSQLClient

async def main():
    async with AgenticSQLClient() as client:
        # Get database information
        db_info = await client.get_database_info()
        print(f"Connected to: {db_info.database}")
        print(f"Tables: {db_info.tables}")
        
        # Execute a query
        result = await client.execute_query("SELECT TOP 5 * FROM Article")
        print(f"Retrieved {result.row_count} rows")
        
        # Get health status
        health = await client.health_check()
        print(f"Server status: {health['server']}")

# Run the example
asyncio.run(main())
```

## Advanced Usage

### Building Business Intelligence Agents

```python
from agentic_sql_client import AgenticSQLClient
from examples.agentic_examples import BusinessIntelligenceAgent

async def business_analysis():
    async with AgenticSQLClient() as client:
        # Initialize Business Intelligence Agent
        bi_agent = BusinessIntelligenceAgent(client)
        await bi_agent.initialize_context()
        
        # Analyze pricing trends
        analysis = await bi_agent.analyze_pricing_trends()
        print("Pricing Analysis:", analysis)
        
        # Answer business questions
        answer = await bi_agent.answer_business_question(
            "What are the most expensive products?"
        )
        print("Answer:", answer)

asyncio.run(business_analysis())
```

### Data Quality and Maintenance

```python
from examples.agentic_examples import DataMaintenanceAgent

async def data_maintenance():
    async with AgenticSQLClient() as client:
        maintenance_agent = DataMaintenanceAgent(client)
        
        # Perform comprehensive data quality check
        report = await maintenance_agent.perform_data_quality_check()
        
        print("Quality Report:")
        for check_type, results in report["checks"].items():
            print(f"  {check_type}: {len(results)} checks")
        
        for recommendation in report.get("recommendations", []):
            print(f"  📋 {recommendation}")

asyncio.run(data_maintenance())
```

## API Reference

### Core Classes

#### AgenticSQLClient

The main client class for interacting with the Azure SQL MCP Server.

```python
class AgenticSQLClient:
    def __init__(self, server_url: str = "https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/sse")
    
    # Context manager support
    async def __aenter__(self) -> 'AgenticSQLClient'
    async def __aexit__(self, exc_type, exc_val, exc_tb)
    
    # Core database operations
    async def get_database_info(self) -> DatabaseInfo
    async def get_table_schema(self, table_name: str, use_cache: bool = True) -> TableSchema
    async def execute_query(self, query: str, limit: int = 100) -> QueryResult
    async def insert_data(self, sql: str) -> Dict[str, Any]
    async def update_data(self, sql: str) -> Dict[str, Any]
    
    # Resource operations
    async def get_database_schema_resource(self) -> Dict[str, Any]
    async def get_database_status_resource(self) -> Dict[str, Any]
    async def get_tables_resource(self) -> Dict[str, Any]
    
    # Intelligent operations
    async def explore_database(self) -> Dict[str, Any]
    async def intelligent_query_suggestion(self, intent: str, table_name: str = None) -> List[str]
    async def execute_batch_queries(self, queries: List[str], stop_on_error: bool = False) -> List[QueryResult]
    
    # Health and monitoring
    async def health_check(self) -> Dict[str, Any]
    async def get_available_tools(self) -> List[Dict[str, str]]
    async def get_available_resources(self) -> List[Dict[str, str]]
```

#### Data Classes

```python
@dataclass
class QueryResult:
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str] 
    row_count: int
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

@dataclass  
class TableSchema:
    name: str
    columns: List[Dict[str, Any]]
    row_count: Optional[int] = None

@dataclass
class DatabaseInfo:
    server: str
    database: str
    version: str
    tables: List[str]
    status: str
```

### Agent Classes

#### BusinessIntelligenceAgent

Specialized agent for business intelligence and data analysis.

```python
class BusinessIntelligenceAgent:
    def __init__(self, sql_client: AgenticSQLClient)
    
    async def initialize_context(self)
    async def analyze_pricing_trends(self) -> Dict[str, Any]
    async def answer_business_question(self, question: str) -> str
```

#### DataMaintenanceAgent

Agent for automated data quality checks and maintenance.

```python
class DataMaintenanceAgent:
    def __init__(self, sql_client: AgenticSQLClient)
    
    async def perform_data_quality_check(self) -> Dict[str, Any]
```

## Examples and Use Cases

### 1. Database Explorer Agent

```python
async def explore_database_intelligent():
    async with AgenticSQLClient() as client:
        # Comprehensive database exploration
        exploration = await client.explore_database()
        
        print("🔍 Database Exploration Results:")
        print(f"Database: {exploration['database_info'].database}")
        print(f"Tables: {len(exploration['database_info'].tables)}")
        
        # Sample data from each table
        for table, sample in exploration.get('sample_data', {}).items():
            print(f"\n📋 {table}:")
            print(f"  Columns: {sample.get('columns', [])}")
            print(f"  Sample rows: {sample.get('row_count', 0)}")
```

### 2. Natural Language Query Interface

```python
async def natural_language_queries():
    async with AgenticSQLClient() as client:
        questions = [
            "Show me the most expensive products",
            "How many products are in each region?", 
            "What categories do we have?",
            "Count total products"
        ]
        
        bi_agent = BusinessIntelligenceAgent(client)
        await bi_agent.initialize_context()
        
        for question in questions:
            answer = await bi_agent.answer_business_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}\n")
```

### 3. Automated Data Analysis

```python
async def automated_analysis():
    async with AgenticSQLClient() as client:
        bi_agent = BusinessIntelligenceAgent(client)
        await bi_agent.initialize_context()
        
        # Automated pricing analysis
        analysis = await bi_agent.analyze_pricing_trends()
        
        print("📈 Automated Analysis Results:")
        print(f"Total Products: {analysis['summary']['total_products']}")
        print(f"Average Price: {analysis['summary']['avg_price']:.2f}")
        
        print("\n🎯 AI Recommendations:")
        for recommendation in analysis.get('recommendations', []):
            print(f"  • {recommendation}")
```

### 4. Health Monitoring and Alerts

```python
async def monitor_system_health():
    async with AgenticSQLClient() as client:
        while True:  # Monitoring loop
            health = await client.health_check()
            
            print(f"🏥 Health Check: {health['server']} | {health['database']}")
            print(f"   Uptime: {health['uptime_seconds']}s")
            print(f"   Requests: {health['request_count']}")
            print(f"   Error Rate: {health['error_rate_percent']}%")
            
            # Alert on issues
            if health['error_rate_percent'] > 10:
                print("🚨 ALERT: High error rate detected!")
            
            await asyncio.sleep(30)  # Check every 30 seconds
```

## Configuration

### Environment Variables

```bash
# Server endpoint (default provided)
MCP_SERVER_URL=https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/sse

# Optional: Enable debug logging
LOG_LEVEL=DEBUG

# Optional: Connection timeout
CONNECTION_TIMEOUT=30
```

### Client Configuration

```python
# Custom server URL
client = AgenticSQLClient(
    server_url="https://your-custom-server.com/sse"
)

# Default configuration (uses deployed Azure Container Apps)
client = AgenticSQLClient()  # Uses default URL
```

## Production Deployment

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY client/ ./
COPY examples/ ./examples/

RUN pip install -r client_requirements.txt

CMD ["python", "your_agent_app.py"]
```

### Azure Container Apps

```bash
# Build and deploy your agent
az containerapp create \
  --name my-sql-agent \
  --resource-group rg-MyAgents \
  --environment cae-MyAgents \
  --image myregistry.azurecr.io/sql-agent:latest \
  --cpu 0.5 --memory 1Gi \
  --env-vars MCP_SERVER_URL="https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/sse"
```

## Best Practices

### 1. Error Handling

```python
async def robust_query_execution():
    async with AgenticSQLClient() as client:
        try:
            result = await client.execute_query("SELECT * FROM Article")
            if result.success:
                print(f"Success: {result.row_count} rows")
            else:
                print(f"Query failed: {result.error}")
        except Exception as e:
            print(f"Connection error: {e}")
```

### 2. Batch Processing

```python
async def efficient_batch_processing():
    async with AgenticSQLClient() as client:
        queries = [
            "SELECT COUNT(*) FROM Article",
            "SELECT COUNT(*) FROM Region", 
            "SELECT COUNT(*) FROM CategorieArticles"
        ]
        
        results = await client.execute_batch_queries(
            queries, 
            stop_on_error=False
        )
        
        for i, result in enumerate(results):
            print(f"Query {i+1}: {result.row_count if result.success else result.error}")
```

### 3. Schema Caching

```python
async def optimize_with_caching():
    async with AgenticSQLClient() as client:
        # First call - fetches and caches schema
        schema1 = await client.get_table_schema("Article", use_cache=True)
        
        # Second call - uses cached schema (faster)
        schema2 = await client.get_table_schema("Article", use_cache=True)
        
        # Force refresh
        schema3 = await client.get_table_schema("Article", use_cache=False)
```

## Integration Examples

### FastAPI Web Service

```python
from fastapi import FastAPI
from agentic_sql_client import AgenticSQLClient

app = FastAPI()
client = AgenticSQLClient()

@app.on_event("startup")
async def startup():
    await client.connect()

@app.on_event("shutdown") 
async def shutdown():
    await client.disconnect()

@app.get("/query")
async def execute_query(q: str):
    result = await client.execute_query(q)
    return {
        "success": result.success,
        "data": result.data,
        "row_count": result.row_count
    }

@app.get("/health")
async def health_check():
    return await client.health_check()
```

### Jupyter Notebook Integration

```python
# Cell 1: Setup
import asyncio
from agentic_sql_client import AgenticSQLClient
from examples.agentic_examples import BusinessIntelligenceAgent

# Cell 2: Connect and explore
client = AgenticSQLClient()
await client.connect()

db_info = await client.get_database_info()
print(f"Connected to: {db_info.database}")
print(f"Tables: {db_info.tables}")

# Cell 3: Business Intelligence
bi_agent = BusinessIntelligenceAgent(client)
await bi_agent.initialize_context()

pricing_analysis = await bi_agent.analyze_pricing_trends()
print("Pricing Summary:", pricing_analysis['summary'])

# Cell 4: Cleanup
await client.disconnect()
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```python
   # Check server status
   curl https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/sse
   ```

2. **Response Format Issues**
   ```python
   # Enable debug logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Query Timeouts**
   ```python
   # Use smaller limits for large datasets
   result = await client.execute_query("SELECT * FROM Article", limit=10)
   ```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async with AgenticSQLClient() as client:
    # All HTTP requests and responses will be logged
    result = await client.execute_query("SELECT TOP 1 * FROM Article")
```

## Contributing

The agentic client is designed to be extensible. You can:

1. **Add Custom Agents**
   ```python
   class MyCustomAgent:
       def __init__(self, sql_client: AgenticSQLClient):
           self.sql_client = sql_client
       
       async def my_custom_analysis(self):
           # Your custom logic here
           pass
   ```

2. **Extend Query Intelligence**
   ```python
   class SmartQueryBuilder(AgenticSQLClient):
       async def build_smart_query(self, intent: str) -> str:
           # Enhanced query building logic
           pass
   ```

3. **Add Custom Resources**
   ```python
   async def get_custom_metrics(client: AgenticSQLClient):
       # Access custom MCP resources
       result = await client.client.read_resource("custom://metrics")
       return result
   ```

## License

This agentic client is designed for use with the Azure SQL MCP Server and follows the same licensing terms.

---

🤖 **Ready to build intelligent database agents!** Start with the examples above and customize for your specific use cases.
