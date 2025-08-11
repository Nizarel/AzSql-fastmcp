"""
🤖 Semantic Kernel Revenue Performance Agent

Advanced revenue analysis agent powered by Microsoft Semantic Kernel and FastMCP.
Provides intelligent database interaction with planning, memory, and conversation capabilities.

Features:
- Intelligent query planning and execution
- Multi-turn conversation support
- Memory and context retention
- Specialized revenue analysis plugins
- Integration with Azure OpenAI
- Comprehensive health monitoring

Authors: Azure AI Assistant
Version: 1.0.0
Compatible with: Semantic Kernel 1.0+, FastMCP 2.9.2+
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
from dotenv import load_dotenv

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    from semantic_kernel.memory import VolatileMemoryStore
    from semantic_kernel.core_plugins import ConversationSummaryPlugin, TimePlugin
    from semantic_kernel.kernel import Kernel  # Explicit import for type annotation
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    print("\u274C Semantic Kernel not available. Install with: pip install semantic-kernel")
    SEMANTIC_KERNEL_AVAILABLE = False
    raise

from agentic_sql_client import AgenticSQLClient, SemanticKernelMCPAdapter, create_sk_enabled_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the Semantic Kernel Revenue Agent"""
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    azure_openai_api_version: str = "2024-02-15-preview"
    mcp_server_url: str = ""
    agent_name: str = "SemanticKernelRevenueAgent"
    agent_description: str = "AI-powered revenue and sales analysis agent"
    max_tokens: int = 4000
    temperature: float = 0.1
    log_level: str = "INFO"
    enable_memory: bool = True
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create configuration from environment variables"""
        return cls(
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            azure_openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            mcp_server_url=os.getenv("MCP_SERVER_URL", ""),
            agent_name=os.getenv("REVENUE_AGENT_NAME", "SemanticKernelRevenueAgent"),
            agent_description=os.getenv("REVENUE_AGENT_DESCRIPTION", "AI-powered revenue and sales analysis agent"),
            max_tokens=int(os.getenv("SK_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("SK_TEMPERATURE", "0.1")),
            log_level=os.getenv("SK_LOG_LEVEL", "INFO"),
            enable_memory=os.getenv("SK_ENABLE_MEMORY", "true").lower() == "true"
        )

class SemanticKernelRevenueAgent:
    """Revenue Performance Agent powered by Semantic Kernel and MCP"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.kernel: Kernel = sk.Kernel()  # Explicit type annotation
        self.mcp_client: Optional[AgenticSQLClient] = None
        self.mcp_adapter: Optional[SemanticKernelMCPAdapter] = None
        self.memory_store: Optional[VolatileMemoryStore] = None
        self.conversation_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.is_initialized = False
        
        # Set logging level
        logger.setLevel(getattr(logging, config.log_level.upper()))
        
        logger.info(f"🤖 Initializing {config.agent_name}")
    
    async def initialize(self) -> bool:
        """Initialize the agent with all components"""
        try:
            logger.info("🔧 Starting agent initialization...")
            
            # Validate configuration
            if not self._validate_config():
                return False
            
            # Configure Azure OpenAI service
            await self._setup_llm_service()
            
            # Initialize MCP client and adapter
            await self._setup_mcp_connection()
            
            # Register plugins
            await self._register_plugins()
            
            # Setup memory
            if self.config.enable_memory:
                self._setup_memory()
            
            self.is_initialized = True
            logger.info("✅ Agent initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            logger.exception("Initialization error details")
            return False
    
    def _validate_config(self) -> bool:
        """Validate agent configuration"""
        required_fields = [
            "azure_openai_api_key",
            "azure_openai_endpoint", 
            "azure_openai_deployment_name",
            "mcp_server_url"
        ]
        
        for field in required_fields:
            value = getattr(self.config, field)
            if not value or value.strip() == "":
                logger.error(f"❌ Required configuration field '{field}' is missing or empty")
                return False
        
        logger.info("✅ Configuration validation passed")
        return True
    
    async def _setup_llm_service(self):
        """Configure Azure OpenAI service for the kernel"""
        try:
            azure_openai = AzureChatCompletion(
                service_id="azure_openai_chat",
                deployment_name=self.config.azure_openai_deployment_name,
                endpoint=self.config.azure_openai_endpoint,
                api_key=self.config.azure_openai_api_key,
                api_version=self.config.azure_openai_api_version
            )
            
            self.kernel.add_service(azure_openai)
            logger.info("🔗 Azure OpenAI service configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Azure OpenAI service: {e}")
            raise
    
    async def _setup_mcp_connection(self):
        """Initialize MCP client connection and adapter"""
        try:
            self.mcp_client, self.mcp_adapter = await create_sk_enabled_client(
                self.config.mcp_server_url
            )
            
            if not self.mcp_adapter:
                logger.warning("⚠️ Semantic Kernel adapter not available")
                return
            
            logger.info("🔗 MCP connection and adapter established successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to establish MCP connection: {e}")
            raise
    
    async def _register_plugins(self):
        """Register all plugins with the kernel"""
        try:
            # Register core plugins as function dictionaries
            conversation_plugin = ConversationSummaryPlugin(self.kernel)
            self.kernel.import_plugin(conversation_plugin.to_dict(), "conversation")
            time_plugin = TimePlugin()
            self.kernel.import_plugin(time_plugin.to_dict(), "time")
            
            # Register MCP-based plugins if adapter is available
            if self.mcp_adapter:
                # Database operations plugin
                db_plugin = self.mcp_adapter.create_database_plugin()
                if db_plugin:
                    self.kernel.import_plugin(db_plugin, "database")
                    logger.info("🔌 Database plugin registered")
                
                # Revenue analysis plugin
                revenue_plugin = self.mcp_adapter.create_revenue_analysis_plugin()
                if revenue_plugin:
                    self.kernel.import_plugin(revenue_plugin, "revenue")
                    logger.info("🔌 Revenue analysis plugin registered")
            
            logger.info("✅ All plugins registered successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to register plugins: {e}")
            raise
    
    def _setup_memory(self):
        """Setup memory store for conversation context"""
        try:
            self.memory_store = VolatileMemoryStore()
            logger.info("🧠 Memory store configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup memory: {e}")
            raise
    
    async def process_query(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """Process user query with direct execution (planning removed for SK 1.34.0+)"""
        
        if not self.is_initialized:
            return {
                "success": False,
                "error": "Agent not initialized. Call initialize() first.",
                "execution_time": 0
            }
        
        start_time = datetime.now()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            logger.info(f"🔄 Processing query for session {session_id[:8]}...")
            
            # Get conversation context
            context = self._get_conversation_context(session_id)
            
            # Always use direct execution
            result = await self._execute_direct(user_query, context)
            
            # Store conversation history
            await self._store_conversation(session_id, user_query, result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "session_id": session_id,
                "timestamp": start_time.isoformat(),
                "used_planning": False
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Query processing failed: {e}")
            logger.exception("Query processing error details")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "session_id": session_id,
                "timestamp": start_time.isoformat()
            }
    
    def _get_conversation_context(self, session_id: str) -> str:
        """Get conversation context for the session"""
        if session_id not in self.conversation_memory:
            return ""
        
        # Get last 3 conversation exchanges for context
        recent_history = self.conversation_memory[session_id][-6:]  # Last 3 Q&A pairs
        
        context_parts = []
        for item in recent_history:
            if item["type"] == "query":
                context_parts.append(f"Previous question: {item['content']}")
            elif item["type"] == "response":
                # Truncate long responses for context
                response_preview = item["content"][:200] + "..." if len(item["content"]) > 200 else item["content"]
                context_parts.append(f"Previous answer: {response_preview}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def _execute_direct(self, user_query: str, context: str = "") -> str:
        """Execute simple queries directly without planning"""
        
        logger.info("⚡ Using direct execution for simple query")
        
        # Create enhanced prompt with context and available functions
        system_prompt = f"""
You are a revenue analysis expert with access to a comprehensive beverage sales database.

Available functions:
- database.execute_query: Execute SQL queries
- database.list_tables: Get list of available tables
- database.describe_table: Get table schema
- revenue.get_best_selling_products: Analyze top products by region/time
- revenue.analyze_category_revenue: Analyze revenue by product category

Database Schema Context:
- segmentacion: Sales transaction data (customer_id, material_id, calday, VentasCajasUnidad, net_revenue, bottles_sold_m)
- cliente: Customer information (customer_id, Canal_Comercial, Nombre_cliente, etc.)
- cliente_cedi: Customer-distribution center mapping (customer_id, Region, CEDI, Territorio)
- producto: Product catalog (Material, Producto, Categoria, Subcategoria)
- mercado: Geographic hierarchy (CEDIid, CEDI, Zona, Territorio)
- tiempo: Date dimension (Fecha, Year, NumMes, Q, Semana)

Key regions: Norte, Sur, Noreste, Occidente, Pacifico

{f"Previous conversation context: {context}" if context else ""}

User Query: {user_query}

Provide clear, actionable insights based on the data. Use appropriate functions to gather the needed information.
"""
        
        # Create and execute function
        function = self.kernel.create_function_from_prompt(
            prompt=system_prompt,
            function_name="process_revenue_query",
            description="Process revenue analysis query with database access"
        )
        
        result = await function.invoke_async()
        
        return result.result if hasattr(result, 'result') else str(result)
    
    async def _store_conversation(self, session_id: str, query: str, result: str):
        """Store conversation in memory for context"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        # Store query
        self.conversation_memory[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "type": "query",
            "content": query
        })
        
        # Store response
        self.conversation_memory[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "type": "response", 
            "content": result
        })
        
        # Keep only last 20 items (10 Q&A pairs)
        if len(self.conversation_memory[session_id]) > 20:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-20:]
        
        logger.debug(f"💾 Stored conversation for session {session_id[:8]}")
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """Get summary of conversation history"""
        if session_id not in self.conversation_memory:
            return "No conversation history found for this session."
        
        history = self.conversation_memory[session_id]
        
        if not history:
            return "No conversation history available."
        
        try:
            # Create conversation text for summarization
            conversation_text = ""
            for item in history:
                if item["type"] == "query":
                    conversation_text += f"User: {item['content']}\n"
                elif item["type"] == "response":
                    # Truncate very long responses for summary
                    content = item['content'][:500] + "..." if len(item['content']) > 500 else item['content']
                    conversation_text += f"Assistant: {content}\n"
            
            # Use conversation summary plugin
            if "conversation" in self.kernel.plugins:
                summary_function = self.kernel.plugins["conversation"].get("SummarizeConversation")
                if summary_function:
                    result = await summary_function.invoke_async(input=conversation_text)
                    return result.result if hasattr(result, 'result') else str(result)
                else:
                    return "Conversation summary function not available."
            else:
                # Fallback summary
                return f"Conversation with {len(history)//2} exchanges about revenue analysis and database queries."
                
        except Exception as e:
            logger.error(f"Failed to generate conversation summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "agent_initialized": self.is_initialized,
            "components": {}
        }
        
        try:
            # Check kernel status
            health_status["components"]["kernel"] = "healthy" if self.kernel else "unhealthy"
            
            # Check MCP connection
            if self.mcp_client and self.mcp_client._connection_verified:
                health_status["components"]["mcp_connection"] = "healthy"
                
                # Check database connection
                db_health = await self.mcp_client.health_check()
                health_status["components"]["database"] = db_health["overall_status"]
            else:
                health_status["components"]["mcp_connection"] = "unhealthy"
                health_status["components"]["database"] = "unhealthy"
            
            # Check memory
            if self.config.enable_memory:
                health_status["components"]["memory"] = "healthy" if self.memory_store else "unhealthy"
            
            # Check plugins
            plugin_count = len(self.kernel.plugins) if self.kernel.plugins else 0
            health_status["components"]["plugins"] = f"healthy ({plugin_count} plugins)"
            
            # Determine overall status
            component_statuses = [
                status for status in health_status["components"].values() 
                if isinstance(status, str) and status in ["healthy", "unhealthy", "degraded"]
            ]
            
            if all("healthy" in status for status in component_statuses):
                health_status["overall_status"] = "healthy"
            elif any("healthy" in status for status in component_statuses):
                health_status["overall_status"] = "degraded"
            else:
                health_status["overall_status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Health check failed: {e}")
            return health_status
    
    async def get_available_functions(self) -> Dict[str, List[str]]:
        """Get list of available functions by plugin"""
        functions_by_plugin = {}
        
        try:
            if self.kernel.plugins:
                for plugin_name, plugin in self.kernel.plugins.items():
                    function_names = []
                    if hasattr(plugin, 'functions') and plugin.functions:
                        function_names = list(plugin.functions.keys())
                    elif hasattr(plugin, '__dict__'):
                        # Get callable methods
                        function_names = [
                            name for name, method in plugin.__dict__.items()
                            if callable(method) and not name.startswith('_')
                        ]
                    
                    functions_by_plugin[plugin_name] = function_names
            
            return functions_by_plugin
            
        except Exception as e:
            logger.error(f"Failed to get available functions: {e}")
            return {}
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        try:
            logger.info("🔄 Shutting down agent...")
            
            # Disconnect MCP client
            if self.mcp_client:
                await self.mcp_client.disconnect()
            
            # Clear memory
            self.conversation_memory.clear()
            
            # Reset initialization flag
            self.is_initialized = False
            
            logger.info("✅ Agent shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory Functions

async def create_revenue_agent(config: Optional[AgentConfig] = None) -> SemanticKernelRevenueAgent:
    """Factory function to create and initialize the revenue agent"""
    
    if config is None:
        config = AgentConfig.from_env()
    
    agent = SemanticKernelRevenueAgent(config)
    
    if await agent.initialize():
        return agent
    else:
        raise RuntimeError("Failed to initialize Revenue Performance Agent")

async def create_revenue_agent_from_env() -> SemanticKernelRevenueAgent:
    """Create revenue agent using environment configuration"""
    return await create_revenue_agent()

# Main execution for testing
if __name__ == "__main__":
    import asyncio
    async def main():
        """Quick test of the agent"""
        try:
            print("\ud83d\ude80 Testing Semantic Kernel Revenue Agent")
            agent = await create_revenue_agent_from_env()
            # Health check
            health = await agent.health_check()
            print(f"Agent Status: {health['overall_status']}")
            # Simple test query
            result = await agent.process_query(
                "What are the top 5 products by revenue in Norte region?"
            )
            if result["success"]:
                print("\u2705 Test query successful")
                print(f"Execution time: {result['execution_time']:.2f}s")
            else:
                print(f"\u274C Test query failed: {result['error']}")
            await agent.shutdown()
        except Exception as e:
            print(f"\u274C Test failed: {e}")
    asyncio.run(main())
