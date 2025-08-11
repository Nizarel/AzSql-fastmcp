#!/usr/bin/env python3
"""
SSE Client Test for Azure SQL MCP Server
Tests the server using Server-Sent Events transport
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastmcp.client import Client, SSETransport

async def test_mcp_with_sse_client():
    """Test the MCP server using SSE transport"""
    print("🚀 SSE MCP Client Test Suite")
    print("=" * 50)
    
    # SSE Configuration
    host = "127.0.0.1"
    port = 8000
    sse_path = "/sse"
    message_path = "/message"
    
    # Create SSE transport
    sse_url = f"http://{host}:{port}{sse_path}"
    message_url = f"http://{host}:{port}{message_path}"
    
    print(f"SSE URL: {sse_url}")
    print(f"Message URL: {message_url}")
    
    try:
        # Create SSE transport - it only needs the base SSE URL
        transport = SSETransport(url=sse_url)
        
        # Create a FastMCP client with SSE transport
        async with Client(transport) as client:
            print("✅ Connected to MCP server via SSE transport")
            
            # Test 1: List available tools
            print("\n📋 TEST 1: List Available Tools via SSE")
            print("-" * 40)
            try:
                tools = await client.list_tools()
                print(f"Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  ✅ {tool.name}: {tool.description}")
            except Exception as e:
                print(f"❌ Error listing tools: {e}")
            
            # Test 2: Get database info
            print("\n🗄️ TEST 2: Database Info via SSE")
            print("-" * 40)
            try:
                result = await client.call_tool("database_info")
                print("Database Info Result:")
                for content in result:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
            except Exception as e:
                print(f"❌ Error getting database info: {e}")
            
            # Test 3: List tables
            print("\n📊 TEST 3: List Tables via SSE")
            print("-" * 40)
            try:
                result = await client.call_tool("list_tables")
                print("List Tables Result:")
                for content in result:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
            except Exception as e:
                print(f"❌ Error listing tables: {e}")
            
            # Test 4: Describe a table
            print("\n🔍 TEST 4: Describe Table via SSE")
            print("-" * 40)
            try:
                result = await client.call_tool("describe_table", {"table_name": "Article"})
                print("Describe Table Result:")
                for content in result:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
            except Exception as e:
                print(f"❌ Error describing table: {e}")
            
            # Test 5: Read data
            print("\n📖 TEST 5: Read Data via SSE")
            print("-" * 40)
            try:
                result = await client.call_tool("read_data", {
                    "query": "SELECT TOP 3 Designation, Tarif FROM Article WHERE Tarif IS NOT NULL ORDER BY Tarif DESC",
                    "limit": 3
                })
                print("Read Data Result:")
                for content in result:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
            except Exception as e:
                print(f"❌ Error reading data: {e}")
            
            # Test 6: List available tools from server
            print("\n🛠️ TEST 6: List Available Tools (Server Tool)")
            print("-" * 40)
            try:
                result = await client.call_tool("list_available_tools")
                print("Available Tools Result:")
                for content in result:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(content)
            except Exception as e:
                print(f"❌ Error listing available tools: {e}")
        
        print("\n✅ SSE MCP Client testing completed!")
        
    except Exception as e:
        print(f"❌ SSE Connection failed: {e}")
        print("Make sure the SSE server is running on http://127.0.0.1:8000")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_with_sse_client())
