#!/usr/bin/env python3
"""
Azure SQL Database MCP Server

A production-ready MCP server for Azure SQL Database operations.
Enhanced with FastMCP 2.10.4 features using optimized streaming HTTP transport.

Author: Azure SQL MCP Server
Version: 3.2.0 (Enhanced Production Resilience - ClosedResourceError Fix)
Compatible with: FastMCP 2.10.4

✅ Production Fixes v3.2.0:
   - Enhanced connection health monitoring
   - ClosedResourceError prevention and handling
   - Connection recovery with exponential backoff
   - Request context validation
   - Graceful error handling for closed streams
   - Comprehensive connection state management
   - Production deployment resilience
   - FastMCP 2.10.4 optimized streaming transport
   - Enhanced caching and serialization
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Add current directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.core import ServerCore

# Load environment and configure logging
load_dotenv()
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("azure_sql_mcp_server")


class AzureSQLMCPServer:
    """Production Azure SQL MCP Server with Enhanced Modular Architecture using Streaming HTTP"""
    
    def __init__(self):
        """Initialize server with modular architecture"""
        logger.info("🚀 Initializing Azure SQL MCP Server v3.2 (Production Resilience)")
        
        # Initialize the core server which handles all components
        self.server_core = ServerCore()
        
        logger.info("✅ Server initialization complete")
        logger.info("📋 Server Summary:")
        logger.info("   🛠️  Tools: %d", self.server_core.tool_registry.get_tool_count())
        logger.info("   📦 Resources: %d", self.server_core.resource_manager.get_resource_count())
        logger.info("   💬 Prompts: %d", self.server_core.prompt_manager.get_prompt_count())
        logger.info("   ✅ Features: Streaming HTTP,")
        logger.info("        Enhanced Error Handling,")
        logger.info("        Connection Health Monitoring,")
        logger.info("        ClosedResourceError Prevention,")
        logger.info("        Connection Recovery,")
        logger.info("        Request Metrics")
    
    def run(self):
        """Start the streaming HTTP server"""
        self.server_core.run()
    
    async def run_async(self):
        """Start the streaming HTTP server asynchronously"""
        await self.server_core.run_async()
    
    def get_server_summary(self) -> dict:
        """Get comprehensive server summary"""
        return self.server_core.get_server_summary()


def main():
    """Entry point"""
    AzureSQLMCPServer().run()


if __name__ == "__main__":
    main()