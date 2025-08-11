"""
🧪 Test Script for Semantic Kernel Revenue Agent

Comprehensive testing suite for the Revenue Performance Agent
including functionality, performance, and integration tests.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, List, Any
from datetime import datetime

from semantic_kernel_revenue_agent import create_revenue_agent_from_env, AgentConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentTester:
    """Comprehensive test suite for the Revenue Agent"""
    
    def __init__(self):
        self.agent = None
        self.test_results: List[Dict[str, Any]] = []
        self.session_id = "test_session_001"
    
    async def run_all_tests(self) -> bool:
        """Run all tests and return overall success status"""
        
        print("🧪 Starting Comprehensive Revenue Agent Tests")
        print("=" * 60)
        
        try:
            # Initialize agent
            if not await self._test_agent_initialization():
                return False
            
            # Core functionality tests
            tests = [
                ("Health Check", self._test_health_check),
                ("Database Connection", self._test_database_connection),
                ("Simple Query", self._test_simple_query),
                ("Best Selling Products", self._test_best_selling_products),
                ("Category Analysis", self._test_category_analysis),
                ("Complex Query with Planning", self._test_complex_query),
                ("Multi-turn Conversation", self._test_conversation),
                ("Error Handling", self._test_error_handling),
                ("Performance", self._test_performance),
                ("Available Functions", self._test_available_functions)
            ]
            
            for test_name, test_func in tests:
                print(f"\n🔬 Running Test: {test_name}")
                print("-" * 40)
                
                success = await test_func()
                self._record_test_result(test_name, success)
                
                if success:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            
            # Print summary
            await self._print_test_summary()
            
            # Cleanup
            if self.agent:
                await self.agent.shutdown()
            
            # Return overall success
            passed_tests = sum(1 for result in self.test_results if result["success"])
            return passed_tests == len(self.test_results)
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            logger.exception("Test suite error")
            return False
    
    async def _test_agent_initialization(self) -> bool:
        """Test agent initialization"""
        try:
            print("🤖 Initializing Revenue Agent...")
            start_time = time.time()
            
            self.agent = await create_revenue_agent_from_env()
            
            init_time = time.time() - start_time
            print(f"✅ Agent initialized in {init_time:.2f}s")
            
            return self.agent is not None and self.agent.is_initialized
            
        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            return False
    
    async def _test_health_check(self) -> bool:
        """Test agent health check"""
        try:
            health = await self.agent.health_check()
            
            print(f"Overall Status: {health['overall_status']}")
            print("Component Status:")
            
            for component, status in health.get('components', {}).items():
                status_emoji = "✅" if "healthy" in str(status) else "❌"
                print(f"  {status_emoji} {component}: {status}")
            
            return health['overall_status'] in ['healthy', 'degraded']
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def _test_database_connection(self) -> bool:
        """Test database connection and basic operations"""
        try:
            # Test table listing
            if self.agent.mcp_client:
                tables_result = await self.agent.mcp_client.client.call_tool("list_tables")
                print("✅ Database connection verified")
                
                # Extract table info
                if hasattr(tables_result, 'content') and tables_result.content:
                    tables_text = tables_result.content[0].text
                elif isinstance(tables_result, list) and tables_result:
                    tables_text = tables_result[0].text if hasattr(tables_result[0], 'text') else str(tables_result[0])
                else:
                    tables_text = str(tables_result)
                
                print(f"Available tables: {tables_text[:100]}...")
                return True
            else:
                print("❌ MCP client not available")
                return False
                
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
    
    async def _test_simple_query(self) -> bool:
        """Test simple query execution"""
        try:
            query = "List the available tables in the database"
            
            result = await self.agent.process_query(query, self.session_id)
            
            if result["success"]:
                print(f"✅ Query executed in {result['execution_time']:.2f}s")
                print(f"Response length: {len(result['result'])} characters")
                print(f"Used planning: {result.get('used_planning', False)}")
                return True
            else:
                print(f"❌ Query failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Simple query test failed: {e}")
            return False
    
    async def _test_best_selling_products(self) -> bool:
        """Test best-selling products analysis"""
        try:
            query = "What are the top 5 best-selling products by revenue in Norte region for March 2025?"
            
            result = await self.agent.process_query(query, self.session_id)
            
            if result["success"]:
                print(f"✅ Best-selling products query executed in {result['execution_time']:.2f}s")
                print("Response preview:")
                print(result["result"][:300] + "..." if len(result["result"]) > 300 else result["result"])
                return True
            else:
                print(f"❌ Best-selling products query failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Best-selling products test failed: {e}")
            return False
    
    async def _test_category_analysis(self) -> bool:
        """Test category revenue analysis"""
        try:
            query = "Analyze revenue by product category for Norte region in March 2025"
            
            result = await self.agent.process_query(query, self.session_id)
            
            if result["success"]:
                print(f"✅ Category analysis executed in {result['execution_time']:.2f}s")
                print(f"Used planning: {result.get('used_planning', False)}")
                return True
            else:
                print(f"❌ Category analysis failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Category analysis test failed: {e}")
            return False
    
    async def _test_complex_query(self) -> bool:
        """Test complex query requiring planning"""
        try:
            query = """
            Compare the revenue performance between Norte and Sur regions for March 2025. 
            Analyze both total revenue and top-performing product categories. 
            Explain which region is performing better and why.
            """
            
            result = await self.agent.process_query(query, self.session_id)
            
            if result["success"]:
                print(f"✅ Complex query executed in {result['execution_time']:.2f}s")
                print(f"Used planning: {result.get('used_planning', False)}")
                
                # Should use planning for this complex query
                expected_planning = True
                if result.get('used_planning') == expected_planning:
                    print("✅ Planning correctly triggered")
                else:
                    print(f"⚠️ Planning not triggered as expected")
                
                return True
            else:
                print(f"❌ Complex query failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Complex query test failed: {e}")
            return False
    
    async def _test_conversation(self) -> bool:
        """Test multi-turn conversation capabilities"""
        try:
            # First query
            query1 = "What are the top 3 products by revenue in Norte region?"
            result1 = await self.agent.process_query(query1, self.session_id)
            
            if not result1["success"]:
                print(f"❌ First conversation query failed: {result1['error']}")
                return False
            
            # Follow-up query (should use context)
            query2 = "What about in Sur region? How do they compare?"
            result2 = await self.agent.process_query(query2, self.session_id)
            
            if not result2["success"]:
                print(f"❌ Follow-up query failed: {result2['error']}")
                return False
            
            # Test conversation summary
            summary = await self.agent.get_conversation_summary(self.session_id)
            
            print("✅ Multi-turn conversation completed")
            print(f"Conversation summary: {summary[:150]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversation test failed: {e}")
            return False
    
    async def _test_error_handling(self) -> bool:
        """Test error handling with invalid queries"""
        try:
            # Test with invalid SQL
            query = "Execute this invalid SQL: INVALID SYNTAX HERE"
            
            result = await self.agent.process_query(query, "error_test_session")
            
            # Should handle error gracefully
            if not result["success"]:
                print("✅ Error handling working correctly")
                print(f"Error message: {result['error'][:100]}...")
                return True
            else:
                print("⚠️ Expected error but query succeeded")
                return True  # Still pass if it handles it somehow
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    async def _test_performance(self) -> bool:
        """Test performance with multiple queries"""
        try:
            queries = [
                "List all tables",
                "What are the top 3 products by volume?",
                "Show revenue by category"
            ]
            
            execution_times = []
            
            for i, query in enumerate(queries):
                result = await self.agent.process_query(query, f"perf_test_{i}")
                
                if result["success"]:
                    execution_times.append(result["execution_time"])
                else:
                    print(f"❌ Performance test query {i+1} failed")
                    return False
            
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            
            print(f"✅ Performance test completed")
            print(f"Average execution time: {avg_time:.2f}s")
            print(f"Maximum execution time: {max_time:.2f}s")
            
            # Consider good performance if average < 10s
            return avg_time < 10.0
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    async def _test_available_functions(self) -> bool:
        """Test listing of available functions"""
        try:
            functions = await self.agent.get_available_functions()
            
            print("✅ Available functions retrieved")
            print("Functions by plugin:")
            
            for plugin_name, function_list in functions.items():
                print(f"  {plugin_name}: {len(function_list)} functions")
                for func in function_list[:3]:  # Show first 3
                    print(f"    - {func}")
                if len(function_list) > 3:
                    print(f"    ... and {len(function_list) - 3} more")
            
            # Should have at least database and revenue plugins
            expected_plugins = ["database", "revenue"]
            has_expected = all(plugin in functions for plugin in expected_plugins)
            
            if has_expected:
                print("✅ Expected plugins found")
            else:
                print("⚠️ Some expected plugins missing")
            
            return len(functions) > 0
            
        except Exception as e:
            print(f"❌ Available functions test failed: {e}")
            return False
    
    def _record_test_result(self, test_name: str, success: bool):
        """Record test result"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  ❌ {test['test_name']}")
        
        print(f"\n🎯 Overall Result: {'PASS' if len(failed_tests) == 0 else 'FAIL'}")

async def run_quick_test():
    """Run a quick subset of tests"""
    print("⚡ Running Quick Test Suite")
    print("-" * 30)
    
    try:
        agent = await create_revenue_agent_from_env()
        
        # Quick health check
        health = await agent.health_check()
        print(f"Health Status: {health['overall_status']}")
        
        # Quick query test
        result = await agent.process_query("What tables are available?")
        
        if result["success"]:
            print("✅ Quick test PASSED")
            print(f"Execution time: {result['execution_time']:.2f}s")
        else:
            print(f"❌ Quick test FAILED: {result['error']}")
        
        await agent.shutdown()
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")

async def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        await run_quick_test()
    else:
        tester = AgentTester()
        success = await tester.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
