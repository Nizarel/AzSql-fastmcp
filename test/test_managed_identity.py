#!/usr/bin/env python3
"""
Test script for Managed Identity Authentication
"""

import os
import sys
import asyncio
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.connection.database_config import DatabaseConfig
from src.connection.sql_connection_factory import SqlConnectionFactory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_managed_identity_connection():
    """Test managed identity connection to Azure SQL"""
    
    print("🔐 Testing Managed Identity Authentication")
    print("=" * 50)
    
    try:
        # Create configuration for managed identity
        config = DatabaseConfig(
            authentication_type='managed_identity',
            managed_identity_client_id='id-AcraSalesAnalytics2'
        )
        
        print(f"📋 Configuration Summary:")
        config_summary = config.get_config_summary()
        for key, value in config_summary.items():
            print(f"   {key}: {value}")
        
        print(f"\n🔗 Connection String (masked): {config.get_masked_connection_string()}")
        
        # Test configuration validation
        if config.validate():
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed")
            return False
        
        # Create connection factory
        factory = SqlConnectionFactory(config)
        
        # Test connection
        print(f"\n🔌 Testing database connection...")
        connection = await factory.create_connection()
        
        if connection:
            print("✅ Database connection successful!")
            
            # Test database info
            db_info = await factory.test_connection(connection)
            print(f"\n📊 Database Information:")
            for key, value in db_info.items():
                print(f"   {key}: {value}")
            
            # Close connection
            await factory.close_connection(connection)
            print("✅ Connection closed successfully")
            
            return True
        else:
            print("❌ Failed to establish database connection")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        logger.exception("Detailed error information:")
        return False

async def test_sql_authentication():
    """Test traditional SQL authentication (if configured)"""
    
    print("\n🔑 Testing SQL Authentication (Fallback)")
    print("=" * 50)
    
    # Check if SQL credentials are available
    if not (os.getenv('AZURE_SQL_USERNAME') and os.getenv('AZURE_SQL_PASSWORD')):
        print("⚠️ SQL credentials not configured, skipping SQL auth test")
        return None
    
    try:
        config = DatabaseConfig(authentication_type='sql')
        
        print(f"📋 Configuration Summary:")
        config_summary = config.get_config_summary()
        for key, value in config_summary.items():
            print(f"   {key}: {value}")
        
        if config.validate():
            print("✅ SQL configuration validation passed")
            
            factory = SqlConnectionFactory(config)
            connection = await factory.create_connection()
            
            if connection:
                print("✅ SQL authentication successful!")
                await factory.close_connection(connection)
                return True
            else:
                print("❌ SQL authentication failed")
                return False
        else:
            print("❌ SQL configuration validation failed")
            return False
            
    except Exception as e:
        print(f"❌ SQL auth test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    
    print("🚀 Azure SQL MCP Server - Authentication Test Suite")
    print("=" * 60)
    
    # Test managed identity
    managed_identity_result = await test_managed_identity_connection()
    
    # Test SQL authentication if available
    sql_auth_result = await test_sql_authentication()
    
    # Summary
    print(f"\n📈 Test Results Summary")
    print("=" * 30)
    print(f"Managed Identity: {'✅ PASS' if managed_identity_result else '❌ FAIL'}")
    if sql_auth_result is not None:
        print(f"SQL Authentication: {'✅ PASS' if sql_auth_result else '❌ FAIL'}")
    else:
        print(f"SQL Authentication: ⚠️ SKIPPED")
    
    if managed_identity_result:
        print(f"\n🎉 Managed Identity authentication is working correctly!")
        print(f"🔒 Your MCP server is ready for secure, credential-free operation.")
    else:
        print(f"\n⚠️ Managed Identity authentication needs attention.")
        print(f"📝 Please check the configuration and Azure setup.")

if __name__ == "__main__":
    asyncio.run(main())
