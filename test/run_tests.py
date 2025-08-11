#!/usr/bin/env python3
"""
Test Runner for Azure SQL MCP Server

Run this from the project root to execute all tests:
    python run_tests.py
"""

import asyncio
import sys
import subprocess
from pathlib import Path

def run_test_file(test_file: Path):
    """Run a single test file"""
    print(f"🧪 Running {test_file.name}...")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file.name} passed!\n")
            return True
        else:
            print(f"❌ {test_file.name} failed with exit code {result.returncode}\n")
            return False
            
    except Exception as e:
        print(f"❌ Error running {test_file.name}: {e}\n")
        return False

def main():
    """Run all tests"""
    print("🚀 Azure SQL MCP Server Test Suite")
    print("=" * 50)
    
    # Find test directory
    test_dir = Path(__file__).parent
    if not test_dir.exists():
        print("❌ Test directory not found!")
        return False
    
    # Find test files
    test_files = [
        test_dir / "test_managed_identity.py",
        test_dir / "test_fastmcp_client.py",
        test_dir / "test_mcp_stdio.py",
        test_dir / "test_sse_client.py"
    ]
    
    # Run tests
    results = []
    for test_file in test_files:
        if test_file.exists():
            success = run_test_file(test_file)
            results.append((test_file.name, success))
        else:
            print(f"⚠️ Test file not found: {test_file}")
            results.append((test_file.name, False))
    
    # Summary
    print("🏆 Test Summary")
    print("=" * 20)
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
