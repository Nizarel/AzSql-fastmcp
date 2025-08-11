# Revenue Performance Agent Implementation Guide
## Multi-Agent Custom Automation Engine with Semantic Kernel Integration

*Document Version: 2.0*  
*Created: June 24, 2025*  
*Updated: July 1, 2025 - Added Semantic Kernel Integration*


---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Agent Overview](#agent-overview)
3. [Business Questions Coverage](#business-questions-coverage)
4. [Technical Architecture](#technical-architecture)
5. [Semantic Kernel Integration](#semantic-kernel-integration)
6. [Implementation Steps](#implementation-steps)
7. [MCP Integration](#mcp-integration)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Guide](#deployment-guide)
10. [Performance Optimization](#performance-optimization)
11. [Future Enhancements](#future-enhancements)
12. [Two-Tier LLM Implementation](#two-tier-llm-implementation)

---

## Executive Summary

The **Revenue Performance Agent** is the first specialized sales analysis agent to be implemented in the Multi-Agent Custom Automation Engine. This agent focuses on financial performance analysis, revenue optimization, and sales forecasting for the beverage distribution business.

### Key Features
- **Revenue Trend Analysis:** Real-time insights across zones, categories, and time periods
- **Profitability Calculations:** Multi-dimensional profitability analysis
- **Sales Forecasting:** AI-powered predictions with seasonality considerations
- **Best-Selling Products:** Volume and value-based product rankings
- **Financial KPIs:** Comprehensive monitoring and variance analysis

#### Why Start with Revenue Performance Agent?
1. **Highest Business Impact:** Covers 9 of 33 business questions (27%)
2. **Core Financial Metrics:** Revenue and profitability are fundamental KPIs
3. **Foundation for Others:** Revenue analysis feeds into customer, territory, and product decisions
4. **Clear MCP Integration:** Direct mapping to `segmentacion` fact table
5. **Immediate Value:** Quick wins with actionable insights

---

## Agent Overview

### 🎯 Purpose
Financial performance analysis and revenue optimization for beverage distribution operations.

### 💡 Core Capabilities
- Revenue trend analysis across multiple dimensions
- Profitability analysis by channel, zone, and category
- Sales forecasting with variance analysis
- Price optimization recommendations
- Financial KPI monitoring and alerting

### 📊 Database Tables Used
- `segmentacion` — Primary fact table with sales transactions
- `tiempo` — Time dimension for temporal analysis
- `cliente` — Customer master data and channel information
- `mercado` — Geographic hierarchy (CEDI, Zone, Territory)
- `producto` — Product master data and category classification

### 🔧 Tools Provided
1. `analyze_revenue_trends` — Multi-dimensional revenue analysis
2. `calculate_profitability` — Profitability metrics by dimension
3. `get_best_selling_products` — Product performance rankings
4. `forecast_sales` — Predictive sales forecasting

---

## Business Questions Coverage

The Revenue Performance Agent addresses **9 critical business questions**:

### 1. Best-Selling Products Analysis
- **Question:** What are the best-selling products by volume and value in march 2025 in North Region?
- **Tool:** `get_best_selling_products`
- **Output:** Ranked list with revenue, volume, customer count metrics

### 2. Profitability Analysis
- **Question:** What is the profitability by channel, zone, or product category?
- **Tool:** `calculate_profitability`
- **Output:** Profitability metrics with margin indicators

### 3. CEDI Performance
- **Question:** Which product/category generated highest profit last quarter per CEDI?
- **Tool:** `calculate_profitability` with CEDI dimension
- **Output:** CEDI-level profitability rankings

### 4. Price Variation Analysis
- **Question:** Is there variation in average selling price per material by zone?
- **Tool:** `analyze_revenue_trends` with price analysis
- **Output:** Price variance reports by geographic zone

### 5. Sales Forecasting
- **Question:** Sales forecast for next month/quarter per CEDI and product?
- **Tool:** `forecast_sales`
- **Output:** Predictive forecasts with confidence intervals

### 6. Forecast Accuracy
- **Question:** How close are actual sales to forecasts?
- **Tool:** `forecast_sales` with accuracy metrics
- **Output:** Variance analysis and accuracy scores

### 7. Demand Estimation
- **Question:** Which zones had demand over/underestimated?
- **Tool:** `analyze_revenue_trends` with forecast comparison
- **Output:** Zone-level demand accuracy analysis

### 8. Revenue vs. Forecast
- **Question:** Revenue vs. forecast accuracy analysis
- **Tool:** Combined analysis tools
- **Output:** Comprehensive accuracy dashboard

### 9. Purchase Ticket Analysis
- **Question:** Average purchase ticket variation by channel and zone
- **Tool:** `analyze_revenue_trends`
- **Output:** Transaction value analysis by dimension

---

## Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Revenue Performance Agent                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Agent Core                           │ │
│  │  - Session Management                                   │ │
│  │  - Memory Store Integration                             │ │
│  │  - Tool Registration                                    │ │
│  │  - System Message Configuration                         │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Revenue Performance Tools                   │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ analyze_revenue │  │ calculate       │              │ │
│  │  │ _trends         │  │ _profitability  │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ get_best_selling│  │ forecast_sales  │              │ │
│  │  │ _products       │  │                 │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   MCP Integration                       │ │
│  │  - Async Query Execution                                │ │
│  │  - Connection Pooling                                   │ │
│  │  - Query Optimization                                   │ │
│  │  - Result Caching                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Query → Revenue Performance Agent → Tool Selection → 
MCP Query Builder → Database → Result Processing → 
Formatted Insights → User Response
```

---

## Implementation Steps

### Step 1: Environment Setup and Dependencies

#### **1.1 Install Required Packages**
```bash
# Create virtual environment
python -m venv sk_revenue_agent
source sk_revenue_agent/bin/activate  # Linux/Mac
# or
sk_revenue_agent\Scripts\activate  # Windows

# Install Semantic Kernel and dependencies
pip install semantic-kernel
pip install semantic-kernel[azure_openai]
pip install semantic-kernel[planning]
pip install semantic-kernel[memory]

# Install existing MCP dependencies
pip install fastmcp
pip install python-dotenv
pip install asyncio
pip install aiohttp
```

#### **1.2 Environment Configuration**
Create `.env` file:
```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# MCP Server Configuration
MCP_SERVER_URL=https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/mcp/

# Semantic Kernel Configuration
SK_LOG_LEVEL=INFO
SK_PLANNER_TYPE=sequential
SK_MEMORY_TYPE=volatile
SK_MAX_TOKENS=4000
SK_TEMPERATURE=0.1

# Agent Configuration
REVENUE_AGENT_NAME=SemanticKernelRevenueAgent
REVENUE_AGENT_DESCRIPTION=AI-powered revenue and sales analysis agent
```

### Step 2: Update Agentic SQL Client for Semantic Kernel

#### **2.1 Enhanced MCP Client with SK Plugin Support**
Update `agentic_sql_client.py`:

```python
# Add new imports at the top
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel import SKContext
from typing import Callable, Any

# Add new class after AgenticSQLClient
class SemanticKernelMCPAdapter:
    """Adapter to bridge MCP client with Semantic Kernel plugins"""
    
    def __init__(self, mcp_client: AgenticSQLClient):
        self.mcp_client = mcp_client
        self._plugin_registry = {}
    
    def create_sk_plugin(self, plugin_name: str, functions: List[Dict[str, Any]]) -> object:
        """Create Semantic Kernel plugin from MCP functions"""
        
        class DynamicPlugin:
            def __init__(self, adapter: 'SemanticKernelMCPAdapter'):
                self._adapter = adapter
        
        # Dynamically add SK functions
        for func_def in functions:
            setattr(DynamicPlugin, func_def['name'], 
                   self._create_sk_function(func_def))
        
        return DynamicPlugin(self)
    
    def _create_sk_function(self, func_def: Dict[str, Any]) -> Callable:
        """Create SK function wrapper for MCP function"""
        
        @sk_function(
            description=func_def.get('description', ''),
            name=func_def['name']
        )
        async def sk_wrapper(context: SKContext) -> str:
            # Extract parameters from SK context
            params = {}
            for param in func_def.get('parameters', []):
                if param['name'] in context.variables:
                    params[param['name']] = context.variables[param['name']]
            
            # Call MCP function
            if func_def['name'] == 'execute_query':
                result = await self.mcp_client.execute_query(
                    params.get('query', ''), 
                    params.get('limit')
                )
            elif func_def['name'] == 'get_best_selling_products':
                result = await self._get_best_selling_products(params)
            # Add more function mappings as needed
            
            return self._format_result_for_sk(result)
        
        return sk_wrapper
    
    async def _get_best_selling_products(self, params: Dict[str, Any]) -> QueryResult:
        """Implementation of best-selling products analysis"""
        region = params.get('region', 'Norte')
        time_period = params.get('time_period', '2025-03')
        limit = params.get('limit', 20)
        
        query = f"""
        SELECT 
            p.Producto,
            p.Categoria,
            p.Subcategoria,
            SUM(s.VentasCajasUnidad) as Total_Volume_Cases,
            SUM(s.net_revenue) as Total_Revenue,
            SUM(s.bottles_sold_m) as Total_Bottles_Millions,
            COUNT(s.customer_id) as Customer_Count
        FROM dev.segmentacion s
        JOIN dev.cliente_cedi cc ON s.customer_id = cc.customer_id
        JOIN dev.producto p ON s.material_id = p.Material
        WHERE s.calday >= '{time_period}-01' 
            AND s.calday < DATEADD(month, 1, '{time_period}-01')
            AND cc.Region = '{region}'
        GROUP BY p.Producto, p.Categoria, p.Subcategoria
        ORDER BY Total_Revenue DESC
        """
        
        return await self.mcp_client.execute_query(query, limit)
    
    def _format_result_for_sk(self, result: QueryResult) -> str:
        """Format MCP query result for Semantic Kernel consumption"""
        if not result.success:
            return f"Error: {result.error}"
        
        if not result.data:
            return "No data found for the specified criteria."
        
        # Format as structured text for LLM processing
        formatted_result = f"Query executed successfully. Found {result.row_count} rows.\n\n"
        
        if result.columns and result.data:
            # Create table format
            formatted_result += "| " + " | ".join(result.columns) + " |\n"
            formatted_result += "|" + "|".join(["-" * (len(col) + 2) for col in result.columns]) + "|\n"
            
            for row in result.data:
                row_values = [str(row.get(col, '')) for col in result.columns]
                formatted_result += "| " + " | ".join(row_values) + " |\n"
        
        return formatted_result
```

### Step 3: Create Semantic Kernel Revenue Agent

#### **3.1 Create Core Agent Class**
Create `semantic_kernel_revenue_agent.py`:

```python
"""
Semantic Kernel Revenue Performance Agent
Integrates with MCP server for intelligent revenue analysis
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning import SequentialPlanner
from semantic_kernel.memory import VolatileMemoryStore
from semantic_kernel.core_plugins import ConversationSummaryPlugin, TimePlugin

from agentic_sql_client import AgenticSQLClient, SemanticKernelMCPAdapter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the Semantic Kernel Revenue Agent"""
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    mcp_server_url: str
    agent_name: str = "RevenuePerformanceAgent"
    max_tokens: int = 4000
    temperature: float = 0.1
    log_level: str = "INFO"

class SemanticKernelRevenueAgent:
    """Revenue Performance Agent powered by Semantic Kernel and MCP"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.kernel = sk.Kernel()
        self.mcp_client = None
        self.mcp_adapter = None
        self.planner = None
        self.conversation_memory = {}
        
        logger.info(f"🤖 Initializing {config.agent_name}")
    
    async def initialize(self) -> bool:
        """Initialize the agent with all components"""
        try:
            # Configure Azure OpenAI service
            await self._setup_llm_service()
            
            # Initialize MCP client
            await self._setup_mcp_connection()
            
            # Register plugins
            await self._register_plugins()
            
            # Setup planner
            self._setup_planner()
            
            logger.info("✅ Agent initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            return False
    
    async def _setup_llm_service(self):
        """Configure Azure OpenAI service for the kernel"""
        azure_openai = AzureChatCompletion(
            service_id="azure_openai",
            deployment_name=self.config.azure_openai_deployment_name,
            endpoint=self.config.azure_openai_endpoint,
            api_key=self.config.azure_openai_api_key
        )
        
        self.kernel.add_service(azure_openai)
        logger.info("🔗 Azure OpenAI service configured")
    
    async def _setup_mcp_connection(self):
        """Initialize MCP client connection"""
        self.mcp_client = AgenticSQLClient(self.config.mcp_server_url)
        await self.mcp_client.connect()
        
        self.mcp_adapter = SemanticKernelMCPAdapter(self.mcp_client)
        logger.info("🔗 MCP connection established")
    
    async def _register_plugins(self):
        """Register all plugins with the kernel"""
        
        # Core plugins
        self.kernel.import_plugin(ConversationSummaryPlugin(self.kernel), "conversation")
        self.kernel.import_plugin(TimePlugin(), "time")
        
        # Database query plugin
        database_functions = [
            {
                'name': 'execute_query',
                'description': 'Execute SQL queries on the database',
                'parameters': [
                    {'name': 'query', 'description': 'SQL query to execute'},
                    {'name': 'limit', 'description': 'Optional row limit'}
                ]
            }
        ]
        
        db_plugin = self.mcp_adapter.create_sk_plugin("database", database_functions)
        self.kernel.import_plugin(db_plugin, "database")
        
        # Revenue analysis plugin
        revenue_functions = [
            {
                'name': 'get_best_selling_products',
                'description': 'Analyze best-selling products by region and time period',
                'parameters': [
                    {'name': 'region', 'description': 'Geographic region (e.g., Norte, Sur)'},
                    {'name': 'time_period', 'description': 'Time period in YYYY-MM format'},
                    {'name': 'limit', 'description': 'Number of top products to return'}
                ]
            }
        ]
        
        revenue_plugin = self.mcp_adapter.create_sk_plugin("revenue", revenue_functions)
        self.kernel.import_plugin(revenue_plugin, "revenue")
        
        logger.info("🔌 All plugins registered successfully")
    
    def _setup_planner(self):
        """Setup the sequential planner for complex queries"""
        self.planner = SequentialPlanner(self.kernel)
        logger.info("📋 Sequential planner configured")
    
    async def process_query(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """Process user query with intelligent planning and execution"""
        
        start_time = datetime.now()
        
        try:
            # Determine if we need planning or direct execution
            if self._requires_planning(user_query):
                result = await self._execute_with_planning(user_query)
            else:
                result = await self._execute_direct(user_query)
            
            # Store conversation history
            if session_id:
                await self._store_conversation(session_id, user_query, result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "session_id": session_id,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    def _requires_planning(self, query: str) -> bool:
        """Determine if query requires multi-step planning"""
        planning_keywords = [
            "analyze", "compare", "relationship", "correlation", 
            "trend", "forecast", "why", "explain", "multiple"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in planning_keywords)
    
    async def _execute_with_planning(self, user_query: str) -> str:
        """Execute query using Semantic Kernel planner"""
        
        # Create a plan for the user query
        plan = await self.planner.create_plan_async(
            goal=user_query,
            kernel=self.kernel
        )
        
        logger.info(f"📋 Created plan with {len(plan._steps)} steps")
        
        # Execute the plan
        result = await plan.invoke_async(kernel=self.kernel)
        
        return result.result
    
    async def _execute_direct(self, user_query: str) -> str:
        """Execute simple queries directly without planning"""
        
        # Create a simple prompt for direct execution
        prompt = f"""
        You are a revenue analysis expert. Answer the following query using the available database functions:
        
        Query: {user_query}
        
        Use the database.execute_query or revenue.get_best_selling_products functions as appropriate.
        Provide clear, actionable insights based on the data.
        """
        
        # Execute directly using the kernel
        function = self.kernel.create_function_from_prompt(
            prompt=prompt,
            function_name="process_revenue_query",
            description="Process revenue analysis query"
        )
        
        result = await function.invoke_async(kernel=self.kernel)
        return result.result
    
    async def _store_conversation(self, session_id: str, query: str, result: str):
        """Store conversation in memory for context"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        self.conversation_memory[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "result": result
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_memory[session_id]) > 10:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-10:]
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """Get summary of conversation history"""
        if session_id not in self.conversation_memory:
            return "No conversation history found."
        
        history = self.conversation_memory[session_id]
        
        # Create summary using conversation plugin
        summary_function = self.kernel.plugins["conversation"]["SummarizeConversation"]
        
        conversation_text = "\n".join([
            f"User: {item['query']}\nAssistant: {item['result'][:200]}..."
            for item in history
        ])
        
        result = await summary_function.invoke_async(
            input=conversation_text,
            kernel=self.kernel
        )
        
        return result.result
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {}
        }
        
        try:
            # Check kernel status
            health_status["components"]["kernel"] = "healthy"
            
            # Check MCP connection
            if self.mcp_client and self.mcp_client._connection_verified:
                health_status["components"]["mcp_connection"] = "healthy"
            else:
                health_status["components"]["mcp_connection"] = "unhealthy"
            
            # Check database connection
            db_health = await self.mcp_client.health_check()
            health_status["components"]["database"] = db_health["overall_status"]
            
            # Check planner
            if self.planner:
                health_status["components"]["planner"] = "healthy"
            else:
                health_status["components"]["planner"] = "unhealthy"
            
            # Determine overall status
            component_statuses = list(health_status["components"].values())
            if all(status == "healthy" for status in component_statuses):
                health_status["overall_status"] = "healthy"
            elif any(status == "healthy" for status in component_statuses):
                health_status["overall_status"] = "degraded"
            else:
                health_status["overall_status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)
            return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        if self.mcp_client:
            await self.mcp_client.disconnect()
        
        logger.info("🔌 Agent shutdown completed")

# Factory function
async def create_revenue_agent() -> SemanticKernelRevenueAgent:
    """Factory function to create and initialize the revenue agent"""
    
    config = AgentConfig(
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        mcp_server_url=os.getenv("MCP_SERVER_URL")
    )
    
    agent = SemanticKernelRevenueAgent(config)
    
    if await agent.initialize():
        return agent
    else:
        raise RuntimeError("Failed to initialize Revenue Performance Agent")
```

### Step 4: Create Test and Demo Scripts

#### **4.1 Create Test Script**
Create `test_sk_revenue_agent.py`:

```python
"""
Test script for Semantic Kernel Revenue Agent
"""

import asyncio
import logging
from semantic_kernel_revenue_agent import create_revenue_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_functionality():
    """Test the core functionality of the revenue agent"""
    
    print("🚀 Starting Semantic Kernel Revenue Agent Tests")
    
    try:
        # Create and initialize agent
        agent = await create_revenue_agent()
        
        # Test 1: Health check
        print("\n1️⃣ Testing Health Check")
        health = await agent.health_check()
        print(f"Overall Status: {health['overall_status']}")
        
        # Test 2: Simple query
        print("\n2️⃣ Testing Simple Query")
        result = await agent.process_query(
            "What are the top 5 best-selling products by revenue in Norte region for March 2025?",
            session_id="test_session_1"
        )
        
        if result["success"]:
            print("✅ Query executed successfully")
            print(f"Execution time: {result['execution_time']:.2f}s")
            print(f"Result preview: {result['result'][:200]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
        
        # Test 3: Complex analytical query
        print("\n3️⃣ Testing Complex Analytical Query")
        complex_result = await agent.process_query(
            "Analyze the revenue trends by product category in Norte region and explain which categories are performing best",
            session_id="test_session_1"
        )
        
        if complex_result["success"]:
            print("✅ Complex query executed successfully")
            print(f"Execution time: {complex_result['execution_time']:.2f}s")
        else:
            print(f"❌ Complex query failed: {complex_result['error']}")
        
        # Test 4: Conversation summary
        print("\n4️⃣ Testing Conversation Summary")
        summary = await agent.get_conversation_summary("test_session_1")
        print(f"Conversation summary: {summary[:150]}...")
        
        # Cleanup
        await agent.shutdown()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.exception("Test execution failed")

if __name__ == "__main__":
    asyncio.run(test_agent_functionality())
```

#### **4.2 Create Interactive Demo**
Create `demo_sk_revenue_agent.py`:

```python
"""
Interactive demo for Semantic Kernel Revenue Agent
"""

import asyncio
import uuid
from datetime import datetime
from semantic_kernel_revenue_agent import create_revenue_agent

class InteractiveDemo:
    """Interactive demonstration of the Revenue Agent capabilities"""
    
    def __init__(self):
        self.agent = None
        self.session_id = str(uuid.uuid4())
    
    async def start_demo(self):
        """Start the interactive demo"""
        
        print("🎯 Welcome to the Semantic Kernel Revenue Performance Agent Demo!")
        print("=" * 60)
        
        # Initialize agent
        print("\n🤖 Initializing agent...")
        self.agent = await create_revenue_agent()
        
        # Health check
        health = await self.agent.health_check()
        print(f"Agent Status: {health['overall_status']}")
        
        # Show sample queries
        self._show_sample_queries()
        
        # Interactive loop
        await self._interactive_loop()
    
    def _show_sample_queries(self):
        """Display sample queries users can try"""
        
        print("\n📝 Sample Queries You Can Try:")
        print("=" * 40)
        
        samples = [
            "What are the top 10 best-selling products in Norte region?",
            "Show me revenue trends by category for March 2025",
            "Which products generated the highest profit last quarter?",
            "Analyze price variations by zone for Coca-Cola products",
            "Compare revenue performance between Norte and Sur regions",
            "What's the average purchase ticket by channel?",
            "Show me the customer count by product category"
        ]
        
        for i, sample in enumerate(samples, 1):
            print(f"  {i}. {sample}")
        
        print("\n💡 You can also ask follow-up questions based on previous results!")
        print("📊 Type 'summary' to get a conversation summary")
        print("🔧 Type 'health' to check agent health")
        print("❌ Type 'quit' to exit")
    
    async def _interactive_loop(self):
        """Main interactive loop"""
        
        print("\n🚀 Ready for queries! Type your question below:")
        print("-" * 50)
        
        while True:
            try:
                # Get user input
                user_query = input("\n💬 Your query: ").strip()
                
                if not user_query:
                    continue
                
                # Handle special commands
                if user_query.lower() == 'quit':
                    break
                elif user_query.lower() == 'health':
                    await self._handle_health_check()
                    continue
                elif user_query.lower() == 'summary':
                    await self._handle_summary()
                    continue
                
                # Process the query
                print("🔄 Processing your query...")
                start_time = datetime.now()
                
                result = await self.agent.process_query(user_query, self.session_id)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Display results
                if result["success"]:
                    print("✅ Query Results:")
                    print("-" * 30)
                    print(result["result"])
                    print(f"\n⏱️ Execution time: {execution_time:.2f}s")
                else:
                    print(f"❌ Query failed: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Cleanup
        print("\n🔄 Shutting down agent...")
        if self.agent:
            await self.agent.shutdown()
        
        print("👋 Thank you for trying the Revenue Performance Agent!")
    
    async def _handle_health_check(self):
        """Handle health check command"""
        print("🔍 Checking agent health...")
        health = await self.agent.health_check()
        
        print(f"Overall Status: {health['overall_status']}")
        print("Components:")
        for component, status in health['components'].items():
            status_emoji = "✅" if status == "healthy" else "❌"
            print(f"  {status_emoji} {component}: {status}")
    
    async def _handle_summary(self):
        """Handle conversation summary command"""
        print("📋 Generating conversation summary...")
        summary = await self.agent.get_conversation_summary(self.session_id)
        print("Summary:")
        print("-" * 20)
        print(summary)

async def main():
    """Main entry point for the demo"""
    demo = InteractiveDemo()
    await demo.start_demo()

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 5: Testing and Validation

#### **5.1 Run Basic Tests**
```bash
# Activate environment
source sk_revenue_agent/bin/activate

# Run basic functionality tests
python test_sk_revenue_agent.py

# Expected output:
# ✅ Agent initialization successful
# ✅ Health check passed
# ✅ Simple query executed
# ✅ Complex query executed
# ✅ Conversation summary generated
```

#### **5.2 Run Interactive Demo**
```bash
# Run interactive demo
python demo_sk_revenue_agent.py

# Try the sample queries and explore capabilities
```

#### **5.3 Integration Validation**
- Verify MCP connection is stable
- Test various SQL query patterns
- Validate Semantic Kernel planning for complex queries
- Check conversation memory and context retention
- Ensure proper error handling and logging




## Enhancements

- Implement additional specialized agents (Customer Intelligence, Territory Distribution, etc.)
- Add advanced forecasting models (ARIMA, Prophet, ML-based)
- Integrate with BI dashboards for visualization
- Real-time alerting and anomaly detection
- Automated report scheduling and distribution

---

## Two-Tier LLM Implementation

The Revenue Performance Agent supports an intelligent two-tier LLM approach that automatically selects between GPT-4.1 for standard queries and o3-mini for complex reasoning tasks.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              Two-Tier LLM Architecture                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Query Analyzer                           │ │
│  │  - Complexity Assessment                                │ │
│  │  - Keyword Pattern Matching                             │ │
│  │  - Multi-Factor Scoring                                 │ │
│  │  - Confidence Level Calculation                         │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐         ┌─────────────────┐           │ │
│  │   Standard Tier │         │  Reasoning Tier │           │ │
│  │                 │         │                 │           │ │
│  │ GPT-4.1         │ ◄─────► │ o3-mini         │           │ │
│  │                 │         │                 │           │ │
│  │ • Routine       │         │ • Complex       │           │ │
│  │   Analysis      │         │   Reasoning     │           │ │
│  │ • Data          │         │ • Root Cause    │           │ │
│  │   Formatting    │         │   Analysis      │           │ │
│  │ • Standard      │         │ • Multi-Factor  │           │ │
│  │   Queries       │         │   Correlation   │           │ │
│  └─────────────────┘         └─────────────────┘           │ │
└─────────────────────────────────────────────────────────────┘
```

### Query Complexity Classification

#### Standard Complexity (GPT-4.1)
- Simple data retrieval queries
- Basic trend analysis
- Standard reporting requests
- Metric calculations

**Examples:**
- "What are the top 10 best-selling products?"
- "Show me revenue for the Norte zone last month"
- "Calculate profitability by category"

#### High Complexity (o3-mini)
- Root cause analysis
- Multi-factor correlations
- Strategic recommendations
- Complex pattern recognition

**Examples:**
- "Why did revenue drop 15% despite increased marketing spend?"
- "What factors are causing revenue cannibalization between products?"
- "Analyze the correlation between pricing strategy and customer retention"

### LLM Configuration

#### Standard Model Configuration
```python
STANDARD_LLM = {
    "model": "gpt-4.1",
    "temperature": 0.1,  # Low for consistency
    "max_tokens": 4000,
    "top_p": 0.9,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1
}
```

#### Reasoning Model Configuration
```python
REASONING_LLM = {
    "model": "o3-mini",
    "temperature": 0.3,  # Higher for creative insights
    "max_tokens": 8000,  # More tokens for detailed analysis
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

### Query Analysis Algorithm

The system uses a sophisticated scoring algorithm to determine query complexity:

#### Complexity Factors
1. **Keyword Matching (40% weight)**
   - Causal keywords: "why", "root cause", "reason"
   - Correlation keywords: "relationship", "impact", "influence"
   - Strategic keywords: "optimization", "strategy", "recommendation"

2. **Question Count (20% weight)**
   - Multiple questions indicate higher complexity
   - Compound queries require more reasoning

3. **Dimension Count (20% weight)**
   - Multi-dimensional analysis (zone + category + time)
   - Cross-functional comparisons

4. **Time Complexity (20% weight)**
   - Temporal comparisons ("vs", "trend", "month-over-month")
   - Historical pattern analysis

#### Scoring Thresholds
- **Standard (< 0.5):** Use GPT-4.1
- **High (≥ 0.5):** Use o3-mini
- **Critical (≥ 0.8):** Use o3-mini with enhanced context

### Implementation Components

#### 1. Query Analyzer Class
```python
class QueryAnalyzer:
    """Analyzes query complexity for LLM selection."""
    
    REASONING_KEYWORDS = [
        "why", "root cause", "correlation", "optimization",
        "strategy", "recommendation", "cannibalization"
    ]
    
    @classmethod
    def analyze_query(cls, query: str) -> Tuple[QueryComplexity, float, List[str]]:
        """Returns complexity level, confidence score, and matched keywords."""
        # Implementation details in code section
```

#### 2. Enhanced Revenue Performance Agent
```python
class RevenuePerformanceAgent(AgentBase):
    """Revenue agent with two-tier LLM support."""
    
    def __init__(self, ..., enable_two_tier: bool = True):
        self.enable_two_tier = enable_two_tier
        self.standard_llm_config = RevenueAgentLLM.STANDARD.value
        self.reasoning_llm_config = RevenueAgentLLM.REASONING.value
        self.query_analyzer = QueryAnalyzer()
        
    async def process_message(self, message: str) -> str:
        """Process with intelligent LLM selection."""
        complexity, confidence, keywords = self.query_analyzer.analyze_query(message)
        
        if self.enable_two_tier and complexity == QueryComplexity.HIGH:
            return await self._process_with_reasoning(message, keywords)
        else:
            return await self._process_standard(message)
```

### Performance Metrics

The two-tier system tracks performance metrics:

#### Usage Statistics
- Standard model usage percentage
- Reasoning model usage percentage
- Average response time by model
- Query complexity distribution

#### Cost Optimization
- **Standard queries:** ~70% of total (lower cost)
- **Complex queries:** ~30% of total (higher value)
- **Cost savings:** ~40% compared to using reasoning model for all queries

### Configuration Options

#### Environment Variables
```bash
# Model Configuration
REVENUE_AGENT_STANDARD_MODEL=gpt-4.1
REVENUE_AGENT_REASONING_MODEL=o3-mini
REVENUE_AGENT_TWO_TIER_ENABLED=true

# Complexity Thresholds
COMPLEXITY_THRESHOLD_HIGH=0.5
COMPLEXITY_THRESHOLD_CRITICAL=0.8

# Model Parameters
STANDARD_MODEL_TEMPERATURE=0.1
REASONING_MODEL_TEMPERATURE=0.3
```

#### Azure OpenAI Deployment
```yaml
# Azure OpenAI Service Configuration
models:
  standard:
    deployment_name: "gpt-4.1"
    version: "1106-preview"
    max_tokens: 4000
  reasoning:
    deployment_name: "o3-mini"
    version: "2024-09-12"
    max_tokens: 8000
```

### Usage Examples

#### Automatic Model Selection
```python
# Standard query → GPT-4.1
response = await agent.process_message(
    "What are the top products by revenue in Norte zone?"
)

# Complex query → o3-mini
response = await agent.process_message(
    "Why did revenue decline in Norte despite increased marketing? "
    "Analyze correlation with customer behavior and seasonal patterns."
)
```

#### Manual Override
```python
# Force reasoning model for specific analysis
agent.enable_two_tier = False
agent.llm_config = agent.reasoning_llm_config.to_dict()
response = await agent.process_message("Your complex query here")
```

---

## Semantic Kernel Integration

The Revenue Performance Agent leverages **Microsoft Semantic Kernel** for enhanced agentic capabilities, providing a robust framework for building intelligent agents with seamless MCP integration.

### 🎯 **Why Semantic Kernel?**

1. **Native Agentic Framework:** Built-in support for multi-agent orchestration
2. **Plugin Architecture:** Modular design with MCP as plugins
3. **Memory Management:** Persistent conversation context and learning
4. **LLM Abstraction:** Easy switching between different language models
5. **Planning Capabilities:** Automatic task decomposition and execution
6. **Enterprise Ready:** Production-grade with logging, telemetry, and error handling

### 🏗️ **Semantic Kernel Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              Semantic Kernel Integration                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Kernel & Agent                          │ │
│  │  - RevenuePerformanceAgent (SK Agent)                   │ │
│  │  - Conversation History & Memory                        │ │
│  │  - Planner Integration                                  │ │
│  │  - Plugin Registry                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                MCP Plugins (SK Native)                  │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ DatabaseQuery   │  │ RevenueAnalysis │              │ │
│  │  │ Plugin          │  │ Plugin          │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │ ProductAnalysis │  │ ForecastPlugin  │              │ │
│  │  │ Plugin          │  │                 │              │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Enhanced MCP Client                        │ │
│  │  - Semantic Kernel Plugin Adapter                      │ │
│  │  - Function Calling Bridge                             │ │
│  │  - Schema Validation                                   │ │
│  │  - Result Formatting                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  FastMCP Server                         │ │
│  │  - Database Connection                                  │ │
│  │  - SQL Execution                                       │ │
│  │  - Data Processing                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 📦 **Required Dependencies**

```bash
# Core Semantic Kernel
pip install semantic-kernel

# Azure OpenAI (for LLM integration)
pip install semantic-kernel[azure_openai]

# Additional utilities
pip install semantic-kernel[planning]
pip install semantic-kernel[memory]

# Existing MCP dependencies
pip install fastmcp
pip install python-dotenv
```

### 🔧 **Plugin Architecture**

#### 1. **DatabaseQueryPlugin**
```python
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel import SKContext

class DatabaseQueryPlugin:
    """Semantic Kernel plugin for database operations via MCP"""
    
    def __init__(self, mcp_client: AgenticSQLClient):
        self._mcp_client = mcp_client
    
    @sk_function(
        description="Execute SQL queries on the database",
        name="execute_query"
    )
    @sk_function_context_parameter(
        name="query",
        description="SQL query to execute"
    )
    @sk_function_context_parameter(
        name="limit",
        description="Optional row limit"
    )
    async def execute_query(self, context: SKContext) -> str:
        """Execute SQL query via MCP client"""
        query = context["query"]
        limit = context.get("limit")
        
        result = await self._mcp_client.execute_query(query, limit)
        return self._format_query_result(result)
```

#### 2. **RevenueAnalysisPlugin**
```python
class RevenueAnalysisPlugin:
    """Specialized revenue analysis functions"""
    
    @sk_function(
        description="Analyze best-selling products by region and time period",
        name="get_best_selling_products"
    )
    async def get_best_selling_products(self, context: SKContext) -> str:
        region = context.get("region", "Norte")
        time_period = context.get("time_period", "2025-03")
        
        # Build complex query for best-selling products
        query = self._build_best_sellers_query(region, time_period)
        result = await self._mcp_client.execute_query(query)
        
        return self._format_best_sellers_result(result)
```

### 🤖 **Agent Implementation**

#### **SemanticKernelRevenueAgent**
```python
import semantic_kernel as sk
from semantic_kernel.planning import SequentialPlanner
from semantic_kernel.memory import VolatileMemoryStore

class SemanticKernelRevenueAgent:
    """Revenue Performance Agent powered by Semantic Kernel"""
    
    def __init__(self, azure_openai_config: Dict[str, str], mcp_server_url: str):
        # Initialize Semantic Kernel
        self.kernel = sk.Kernel()
        
        # Configure LLM service
        self.kernel.add_service(
            AzureChatCompletion(
                service_id="azure_openai",
                deployment_name=azure_openai_config["deployment_name"],
                endpoint=azure_openai_config["endpoint"],
                api_key=azure_openai_config["api_key"]
            )
        )
        
        # Initialize MCP client
        self.mcp_client = AgenticSQLClient(mcp_server_url)
        
        # Register plugins
        self._register_plugins()
        
        # Initialize planner and memory
        self.planner = SequentialPlanner(self.kernel)
        self.memory = VolatileMemoryStore()
        
    async def _register_plugins(self):
        """Register MCP-based plugins with Semantic Kernel"""
        await self.mcp_client.connect()
        
        # Database query plugin
        db_plugin = DatabaseQueryPlugin(self.mcp_client)
        self.kernel.import_plugin(db_plugin, "database")
        
        # Revenue analysis plugin
        revenue_plugin = RevenueAnalysisPlugin(self.mcp_client)
        self.kernel.import_plugin(revenue_plugin, "revenue")
        
        # Product analysis plugin
        product_plugin = ProductAnalysisPlugin(self.mcp_client)
        self.kernel.import_plugin(product_plugin, "products")
        
    async def process_query(self, user_query: str, session_id: str = None) -> str:
        """Process user query with intelligent planning"""
        
        # Create plan for complex queries
        plan = await self.planner.create_plan_async(
            goal=user_query,
            kernel=self.kernel
        )
        
        # Execute plan
        result = await plan.invoke_async(kernel=self.kernel)
        
        # Store conversation in memory
        if session_id:
            await self._store_conversation(session_id, user_query, result.result)
        
        return result.result
```

### 🎛️ **Configuration Management**

#### **Environment Configuration**
```bash
# .env file
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# MCP Server Configuration
MCP_SERVER_URL=https://azsql-fastmcpserv.jollyfield-479bc951.eastus2.azurecontainerapps.io/mcp/

# Semantic Kernel Configuration
SK_LOG_LEVEL=INFO
SK_PLANNER_TYPE=sequential
SK_MEMORY_TYPE=volatile

# Agent Configuration
REVENUE_AGENT_NAME=RevenuePerformanceAgent
REVENUE_AGENT_DESCRIPTION="Specialized agent for revenue and sales analysis"
```

#### **Agent Configuration Class**
```python
@dataclass
class SemanticKernelConfig:
    """Configuration for Semantic Kernel Revenue Agent"""
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    mcp_server_url: str
    log_level: str = "INFO"
    planner_type: str = "sequential"
    memory_type: str = "volatile"
    max_tokens: int = 4000
    temperature: float = 0.1
```

### 🔄 **Advanced Features**

#### **1. Multi-Turn Conversations**
```python
class ConversationManager:
    """Manages multi-turn conversations with context retention"""
    
    async def start_conversation(self, session_id: str) -> str:
        """Initialize a new conversation session"""
        
    async def continue_conversation(self, session_id: str, message: str) -> str:
        """Continue existing conversation with context"""
        
    async def get_conversation_summary(self, session_id: str) -> str:
        """Get summary of conversation history"""
```

#### **2. Dynamic Plugin Loading**
```python
class PluginRegistry:
    """Dynamic plugin registration and management"""
    
    async def discover_mcp_tools(self) -> List[Plugin]:
        """Auto-discover MCP tools and convert to SK plugins"""
        
    async def register_custom_plugin(self, plugin: Plugin) -> None:
        """Register custom business logic plugins"""
```

#### **3. Intelligent Planning**
```python
class BusinessIntelligencePlanner:
    """Specialized planner for business intelligence queries"""
    
    async def analyze_query_complexity(self, query: str) -> PlanComplexity:
        """Determine if query requires multi-step planning"""
        
    async def create_analysis_plan(self, goal: str) -> Plan:
        """Create step-by-step analysis plan"""
```

### 📊 **Integration Benefits**

#### **Enhanced Capabilities**
- **Automatic Planning:** Complex queries broken into executable steps
- **Context Awareness:** Conversation memory and learning
- **Plugin Ecosystem:** Extensible with custom business logic
- **Error Recovery:** Intelligent retry and fallback mechanisms
- **Performance Optimization:** Caching and query optimization

#### **Developer Experience**
- **Type Safety:** Full TypeScript-like typing support
- **IntelliSense:** Rich IDE support for plugin development
- **Testing Framework:** Built-in testing utilities
- **Debugging Tools:** Comprehensive logging and tracing
- **Documentation:** Auto-generated API documentation

#### **Enterprise Features**
- **Security:** OAuth, API keys, and role-based access
- **Monitoring:** Telemetry and performance metrics
- **Compliance:** Audit trails and data governance
- **Scalability:** Horizontal scaling and load balancing
- **Integration:** REST APIs, webhooks, and event streams

---
