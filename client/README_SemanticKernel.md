# 🤖 Semantic Kernel Revenue Performance Agent

Advanced revenue analysis agent powered by **Microsoft Semantic Kernel** and **FastMCP**, providing intelligent database interaction with planning, memory, and conversation capabilities.

## 🌟 Features

- **🧠 Intelligent Planning**: Automatic query decomposition for complex business questions
- **💬 Multi-turn Conversations**: Context-aware dialogue with memory retention
- **🔗 MCP Integration**: Seamless connection to FastMCP server for database operations
- **📊 Specialized Analysis**: Purpose-built tools for revenue and sales analysis
- **⚡ Performance Optimized**: Smart caching and query optimization
- **🛡️ Enterprise Ready**: Comprehensive error handling, logging, and monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Semantic Kernel Revenue Agent                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Agent Core                              │ │
│  │  • Conversation Management                              │ │
│  │  • Memory & Context                                     │ │
│  │  • Query Planning                                       │ │
│  │  • Plugin Registry                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               Semantic Kernel Plugins                   │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ Database        │  │ Revenue         │              │ │
│  │  │ Operations      │  │ Analysis        │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ Conversation    │  │ Time & Date     │              │ │
│  │  │ Summary         │  │ Functions       │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                FastMCP Integration                      │ │
│  │  • Enhanced SQL Client                                 │ │
│  │  • Plugin Adapter                                      │ │
│  │  • Result Formatting                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd AzSql_fastmcp/client

# Create virtual environment
python -m venv sk_revenue_agent
source sk_revenue_agent/bin/activate  # Linux/Mac
# or
sk_revenue_agent\Scripts\activate  # Windows

# Install dependencies
pip install -r sk_requirements.txt
```

### 2. Configuration

Create a `.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# MCP Server Configuration
MCP_SERVER_URL=https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/mcp/

# Agent Configuration
REVENUE_AGENT_NAME=SemanticKernelRevenueAgent
SK_LOG_LEVEL=INFO
SK_MAX_TOKENS=4000
SK_TEMPERATURE=0.1
```

### 3. Quick Test

```bash
# Run quick functionality test
python test_sk_revenue_agent.py quick

# Expected output:
# ⚡ Running Quick Test Suite
# Health Status: healthy
# ✅ Quick test PASSED
# Execution time: 2.34s
```

### 4. Interactive Demo

```bash
# Launch interactive demo
python demo_sk_revenue_agent.py

# Follow the guided prompts to explore capabilities
```

## 📖 Usage Examples

### Basic Usage

```python
import asyncio
from semantic_kernel_revenue_agent import create_revenue_agent_from_env

async def main():
    # Create and initialize agent
    agent = await create_revenue_agent_from_env()
    
    # Simple query
    result = await agent.process_query(
        "What are the top 5 products by revenue in Norte region?"
    )
    
    if result["success"]:
        print("Query Results:")
        print(result["result"])
        print(f"Execution time: {result['execution_time']:.2f}s")
    
    # Cleanup
    await agent.shutdown()

asyncio.run(main())
```

### Multi-turn Conversation

```python
async def conversation_example():
    agent = await create_revenue_agent_from_env()
    session_id = "conversation_001"
    
    # First query
    result1 = await agent.process_query(
        "What are the top products in Norte region?", 
        session_id
    )
    
    # Follow-up with context
    result2 = await agent.process_query(
        "How do they compare to Sur region?", 
        session_id
    )
    
    # Get conversation summary
    summary = await agent.get_conversation_summary(session_id)
    print(f"Conversation Summary: {summary}")
    
    await agent.shutdown()
```

### Custom Configuration

```python
from semantic_kernel_revenue_agent import AgentConfig, SemanticKernelRevenueAgent

async def custom_agent_example():
    # Custom configuration
    config = AgentConfig(
        azure_openai_api_key="your_key",
        azure_openai_endpoint="your_endpoint",
        azure_openai_deployment_name="gpt-4",
        mcp_server_url="your_mcp_server",
        temperature=0.2,  # More creative responses
        enable_planning=True,
        enable_memory=True
    )
    
    agent = SemanticKernelRevenueAgent(config)
    await agent.initialize()
    
    # Use the agent...
    
    await agent.shutdown()
```

## 🔧 Available Functions

### Database Operations
- `execute_query` - Execute SQL queries
- `list_tables` - Get available tables
- `describe_table` - Get table schema

### Revenue Analysis
- `get_best_selling_products` - Top products by region/time
- `analyze_category_revenue` - Revenue trends by category

### Conversation Management
- `process_query` - Main query processing
- `get_conversation_summary` - Session summary
- `health_check` - System health status

## 📊 Sample Queries

### Product Performance
```
What are the top 10 best-selling products by revenue in Norte region?
Show me the best-performing Coca-Cola products by volume in March 2025
Which products have the highest profit margins?
```

### Revenue Analysis
```
Analyze revenue trends by category for Norte region
Compare revenue performance between Norte and Sur regions
What's the total revenue by distribution channel?
```

### Business Intelligence
```
Explain why revenue might be declining in certain categories
What factors drive the success of top-performing products?
Identify potential opportunities for revenue growth
```

### Geographic Insights
```
Which regions have the highest revenue per customer?
Show me market performance by CEDI (distribution center)
Analyze price variations by geographic zone
```

## 🧪 Testing

### Run All Tests
```bash
python test_sk_revenue_agent.py

# Expected output:
# 🧪 Starting Comprehensive Revenue Agent Tests
# ✅ Agent Initialization - PASSED
# ✅ Health Check - PASSED
# ✅ Database Connection - PASSED
# ... (more tests)
# 🎯 Overall Result: PASS
```

### Test Categories
- **Initialization**: Agent setup and configuration
- **Health Check**: System status validation
- **Database Connection**: MCP connectivity
- **Simple Queries**: Basic functionality
- **Complex Queries**: Planning and execution
- **Conversation**: Multi-turn dialogue
- **Error Handling**: Graceful error management
- **Performance**: Execution time benchmarks

## 🎛️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Required |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | Required |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | `gpt-4` |
| `MCP_SERVER_URL` | FastMCP server URL | Required |
| `SK_LOG_LEVEL` | Logging level | `INFO` |
| `SK_MAX_TOKENS` | Maximum response tokens | `4000` |
| `SK_TEMPERATURE` | Model temperature | `0.1` |
| `SK_ENABLE_PLANNING` | Enable planning | `true` |
| `SK_ENABLE_MEMORY` | Enable memory | `true` |

### Agent Configuration

```python
@dataclass
class AgentConfig:
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    mcp_server_url: str
    agent_name: str = "SemanticKernelRevenueAgent"
    max_tokens: int = 4000
    temperature: float = 0.1
    enable_planning: bool = True
    enable_memory: bool = True
```

## 🔍 Monitoring and Debugging

### Health Check
```python
health = await agent.health_check()
print(f"Overall Status: {health['overall_status']}")

# Component-level status
for component, status in health['components'].items():
    print(f"{component}: {status}")
```

### Logging
```python
import logging

# Enable debug logging
logging.getLogger('semantic_kernel_revenue_agent').setLevel(logging.DEBUG)

# View detailed execution logs
```

### Performance Metrics
```python
result = await agent.process_query("Your query here")

print(f"Execution time: {result['execution_time']:.2f}s")
print(f"Used planning: {result['used_planning']}")
print(f"Session ID: {result['session_id']}")
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Agent Initialization Fails
```
❌ Agent initialization failed: Required configuration field 'azure_openai_api_key' is missing
```
**Solution**: Check your `.env` file and ensure all required fields are set.

#### 2. MCP Connection Issues
```
❌ Failed to establish MCP connection: Connection refused
```
**Solution**: Verify the MCP server URL and ensure the server is running.

#### 3. Azure OpenAI Authentication
```
❌ Failed to configure Azure OpenAI service: Unauthorized
```
**Solution**: Verify your API key and endpoint are correct.

#### 4. Planning Errors
```
❌ Query processing failed: Plan execution failed
```
**Solution**: Try disabling planning with `enable_planning=False` or simplify the query.

### Debug Mode

```bash
# Enable verbose logging
export SK_LOG_LEVEL=DEBUG

# Run with debug output
python demo_sk_revenue_agent.py
```

### Health Diagnostics

```bash
# Check agent health
python -c "
import asyncio
from semantic_kernel_revenue_agent import create_revenue_agent_from_env

async def check():
    agent = await create_revenue_agent_from_env()
    health = await agent.health_check()
    print(f'Status: {health[\"overall_status\"]}')
    await agent.shutdown()

asyncio.run(check())
"
```

## 🔄 Updates and Maintenance

### Update Dependencies
```bash
pip install -r sk_requirements.txt --upgrade
```

### Configuration Validation
```bash
python -c "
from semantic_kernel_revenue_agent import AgentConfig
config = AgentConfig.from_env()
print('✅ Configuration valid')
"
```

## 📈 Performance Optimization

### Best Practices
1. **Use Session IDs**: Enable conversation context
2. **Cache Results**: Leverage built-in result caching
3. **Optimize Queries**: Use specific date ranges and filters
4. **Monitor Usage**: Track execution times and planning usage

### Scaling Considerations
- **Connection Pooling**: MCP client manages connections efficiently
- **Memory Management**: Conversation history is automatically pruned
- **Query Optimization**: Complex queries are automatically planned
- **Error Recovery**: Built-in retry and fallback mechanisms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r sk_requirements.txt
pip install pytest pytest-asyncio pytest-mock

# Run tests
python test_sk_revenue_agent.py

# Run demo
python demo_sk_revenue_agent.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section above
2. Review the test results for system validation
3. Enable debug logging for detailed error information
4. Consult the Semantic Kernel documentation for advanced features

---

**Ready to analyze your revenue data with AI? Start with the quick test and explore the interactive demo!** 🚀
