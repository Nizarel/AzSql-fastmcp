#!/usr/bin/env python3
"""
Prompt Manager Module

Handles registration and management of MCP prompts for common database operations.
"""

import logging
from fastmcp import FastMCP
from connection import SqlConnectionFactory

logger = logging.getLogger("azure_sql_prompt_manager")


class PromptManager:
    """Manages MCP prompt registration for interactive database operations"""
    
    def __init__(self, mcp: FastMCP, connection_factory: SqlConnectionFactory):
        """Initialize prompt manager"""
        self.mcp = mcp
        self.connection_factory = connection_factory
        self._registered_prompts = []
        
    def register_all_prompts(self):
        """Register all MCP prompts for common database operations"""
        
        @self.mcp.prompt("sql_query_builder")
        async def sql_query_builder(table_name: str = None) -> str:
            """Interactive SQL query builder prompt
            
            Args:
                table_name: Optional table name to build queries for
            """
            if not table_name:
                return """
                # SQL Query Builder
                
                Please specify a table name to build a query for that specific table.
                Use the `list_tables` tool to see all available tables first.
                
                **Example usage:**
                - Prompt: sql_query_builder with table_name="users"
                - This will show columns and generate example queries for the users table
                """
            
            # Get table schema for better query building
            try:
                conn = await self.connection_factory.create_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COLUMN_NAME, 
                        DATA_TYPE,
                        IS_NULLABLE,
                        CHARACTER_MAXIMUM_LENGTH,
                        COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                """, (table_name,))
                
                columns = cursor.fetchall()
                cursor.close()
                await self.connection_factory.close_connection(conn)
                
                if not columns:
                    return f"❌ Table '{table_name}' not found. Use `list_tables` tool to see available tables."
                
                # Build column information
                column_details = []
                column_names = []
                for col in columns:
                    col_name = col[0]
                    col_type = col[1]
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    max_len = f"({col[3]})" if col[3] else ""
                    default = f" DEFAULT {col[4]}" if col[4] else ""
                    
                    column_details.append(f"  - **{col_name}** {col_type}{max_len} {nullable}{default}")
                    column_names.append(col_name)
                
                column_list = "\n".join(column_details)
                column_names_str = ", ".join(column_names)
                
                return f"""
# SQL Query Builder for Table: `{table_name}`

## Available Columns:
{column_list}

## Example Queries:

### 1. SELECT Operations
```sql
-- Select all data (limit recommended)
SELECT * FROM {table_name}

-- Select specific columns
SELECT {column_names_str} FROM {table_name} WHERE [condition]

-- Select with filtering and ordering
SELECT * FROM {table_name} 
WHERE [column] = 'value' 
ORDER BY [column] ASC/DESC

-- Count records
SELECT COUNT(*) FROM {table_name}

-- Group by example (if applicable)
SELECT [column], COUNT(*) 
FROM {table_name} 
GROUP BY [column]
```

### 2. INSERT Operations
```sql
-- Insert single record
INSERT INTO {table_name} ({column_names_str}) 
VALUES (value1, value2, ...)

-- Insert multiple records
INSERT INTO {table_name} ({column_names_str}) 
VALUES 
    (value1a, value2a, ...),
    (value1b, value2b, ...)
```

### 3. UPDATE Operations
```sql
-- Update specific records
UPDATE {table_name} 
SET column1 = 'new_value', column2 = 'new_value2'
WHERE [condition]

-- Update with join (if needed)
UPDATE {table_name} 
SET column1 = 'new_value'
WHERE [primary_key] IN (SELECT [key] FROM [other_table] WHERE [condition])
```

### 4. DELETE Operations
```sql
-- Delete specific records
DELETE FROM {table_name} WHERE [condition]

-- Delete with subquery
DELETE FROM {table_name} 
WHERE [column] IN (SELECT [column] FROM [other_table] WHERE [condition])
```

## Tools to Use:
- **read_data**: Execute SELECT queries (use `query` parameter)
- **insert_data**: Execute INSERT statements (use `sql` parameter)  
- **update_data**: Execute UPDATE/DELETE statements (use `sql` parameter)
- **describe_table**: Get detailed table structure and constraints

## Safety Tips:
- Always use WHERE clauses for UPDATE/DELETE operations
- Test SELECT queries before running INSERT/UPDATE/DELETE
- Use transactions for multiple related operations
- Consider using LIMIT for large result sets
                """
            except Exception as e:
                logger.error(f"Error building query helper: {e}")
                return f"❌ Error building query helper for table '{table_name}': {str(e)}"
        
        @self.mcp.prompt("analyze_performance")
        async def analyze_performance(query: str = None) -> str:
            """SQL query performance analysis and optimization prompt
            
            Args:
                query: Optional SQL query to analyze
            """
            if not query:
                return """
# Query Performance Analyzer

Please provide a SQL query to analyze for performance optimization.

**Example usage:**
- Prompt: analyze_performance with query="SELECT * FROM users WHERE email = 'user@example.com'"
                """
            
            return f"""
# Query Performance Analysis

## Query to Analyze:
```sql
{query}
```

## Azure SQL Database Performance Optimization Guide

### 1. **Index Analysis**
- **Primary recommendation**: Ensure indexes exist on columns used in:
  - WHERE clauses
  - JOIN conditions  
  - ORDER BY clauses
  - GROUP BY clauses

- **Check existing indexes**:
```sql
SELECT 
    i.name AS index_name,
    c.name AS column_name,
    i.type_desc
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID('[table_name]')
```

### 2. **Query Plan Analysis**
Get the execution plan to identify bottlenecks:
```sql
SET SHOWPLAN_ALL ON
GO
{query}
GO
SET SHOWPLAN_ALL OFF
```

Or use:
```sql
-- Get actual execution plan with statistics
SET STATISTICS IO ON
SET STATISTICS TIME ON
{query}
SET STATISTICS IO OFF
SET STATISTICS TIME OFF
```

### 3. **Optimization Strategies**

#### **SELECT Query Optimization:**
- ✅ Specify only needed columns instead of `SELECT *`
- ✅ Use appropriate WHERE conditions to filter early
- ✅ Consider adding covering indexes for frequently used queries
- ✅ Use EXISTS instead of IN with subqueries for better performance

#### **JOIN Optimization:**
- ✅ Ensure indexes on both sides of JOIN conditions
- ✅ Use appropriate JOIN types (INNER vs LEFT/RIGHT)
- ✅ Consider query rewriting for complex multi-table joins

#### **WHERE Clause Optimization:**
- ✅ Put most selective conditions first
- ✅ Avoid functions on indexed columns in WHERE clauses
- ✅ Use SARGable (Search ARGument-able) predicates

### 4. **Azure SQL Specific Features**

#### **Automatic Tuning:**
```sql
-- Enable automatic plan correction
ALTER DATABASE [your_database] SET AUTOMATIC_TUNING (PLAN_CORRECTION = ON)

-- Enable automatic index management
ALTER DATABASE [your_database] SET AUTOMATIC_TUNING (CREATE_INDEX = ON, DROP_INDEX = ON)
```

#### **Query Store Analysis:**
```sql
-- Top resource consuming queries
SELECT TOP 10
    qsq.query_id,
    qsq.query_sql_text,
    qsp.avg_cpu_time,
    qsp.avg_logical_io_reads,
    qsp.avg_duration
FROM sys.query_store_query_text qsqt
JOIN sys.query_store_query qsq ON qsqt.query_text_id = qsq.query_text_id
JOIN sys.query_store_plan qsp ON qsq.query_id = qsp.query_id
ORDER BY qsp.avg_cpu_time DESC
```

#### **Columnstore Indexes** (for analytics):
- Consider for large tables with analytical queries
- Best for aggregations and data warehouse scenarios

### 5. **Monitoring Recommendations**
- Enable Query Store for performance history
- Monitor DTU/vCore utilization
- Set up alerts for high resource usage
- Use Azure SQL Analytics for comprehensive monitoring

### 6. **Testing Your Query**
Use these tools to test performance:
- **read_data**: Execute your optimized query
- **database_info**: Check current database status
- **health_check**: Monitor server performance

### 7. **Common Performance Anti-Patterns to Avoid**
- ❌ Using `SELECT *` when only few columns needed
- ❌ Missing WHERE clauses on large tables
- ❌ Using functions in WHERE clauses on indexed columns
- ❌ Implicit data type conversions
- ❌ Cursor-based operations when set-based would work
            """
        
        @self.mcp.prompt("data_migration_guide")
        async def data_migration_guide() -> str:
            """Comprehensive guide for data migration to Azure SQL Database"""
            return """
# Azure SQL Database Migration Guide

## Pre-Migration Assessment

### 1. **Compatibility Check**
Use Azure Data Migration Assistant (DMA) to assess:
- Schema compatibility issues
- Feature parity gaps  
- Performance recommendations
- Blocking issues that need resolution

### 2. **Sizing and Performance Tier Selection**
- **DTU Model**: Good for predictable workloads
- **vCore Model**: Better control and hybrid benefits
- **Serverless**: Cost-effective for variable workloads

## Migration Strategies

### 1. **Azure Database Migration Service (DMS)** 🥇
**Best for**: Large databases requiring minimal downtime

**Advantages:**
- Near-zero downtime with online migration
- Supports SQL Server, MySQL, PostgreSQL sources
- Automated migration workflow
- Built-in monitoring and error handling

**Process:**
1. Create DMS instance in Azure Portal
2. Configure source and target connections
3. Select databases and tables to migrate
4. Run assessment and resolve issues
5. Start migration (offline or online)
6. Monitor progress and cutover

### 2. **BACPAC Export/Import** 📦
**Best for**: Smaller databases (<200GB), development environments

**Process:**
```sql
-- Export BACPAC
SqlPackage.exe /Action:Export /SourceServerName:[server] 
/SourceDatabaseName:[database] /TargetFile:[file.bacpac]

-- Import BACPAC
SqlPackage.exe /Action:Import /SourceFile:[file.bacpac] 
/TargetServerName:[azure-server] /TargetDatabaseName:[database]
```

### 3. **Transactional Replication** 🔄
**Best for**: Near-zero downtime, SQL Server sources only

**Setup:**
1. Configure distributor and publisher
2. Create publication on source database
3. Add Azure SQL DB as subscriber
4. Monitor replication lag
5. Cutover when ready

### 4. **Bulk Copy Program (BCP)** ⚡
**Best for**: Data-only migration, ETL scenarios

```bash
# Export data
bcp "SELECT * FROM [table]" queryout data.txt -S [server] -d [database] -T -c

# Import data  
bcp [azure_table] in data.txt -S [azure-server] -d [azure-database] -U [username] -P [password] -c
```

## Post-Migration Checklist

### 1. **Data Validation** ✅
```sql
-- Compare row counts
SELECT COUNT(*) FROM [source_table]
SELECT COUNT(*) FROM [target_table]

-- Sample data comparison
SELECT TOP 100 * FROM [source_table] ORDER BY [primary_key]
SELECT TOP 100 * FROM [target_table] ORDER BY [primary_key]

-- Checksum validation for critical tables
SELECT CHECKSUM_AGG(CHECKSUM(*)) FROM [table_name]
```

### 2. **Performance Optimization** 🚀
```sql
-- Update statistics for all tables
EXEC sp_updatestats

-- Rebuild indexes if needed
ALTER INDEX ALL ON [table_name] REBUILD

-- Update compatibility level
ALTER DATABASE [database_name] SET COMPATIBILITY_LEVEL = 150
```

### 3. **Security Configuration** 🔒
- Configure firewall rules
- Set up Azure AD authentication
- Enable Advanced Data Security
- Configure data classification and masking
- Set up auditing and threat detection

### 4. **Backup and Recovery** 💾
```sql
-- Verify automated backups are configured
SELECT * FROM sys.database_recovery_status

-- Test point-in-time restore
-- (Use Azure Portal or PowerShell)
```

### 5. **Application Configuration** ⚙️
Update connection strings:
```
Server=tcp:[server].database.windows.net,1433;
Database=[database];
User ID=[username];
Password=[password];
Encrypt=True;
TrustServerCertificate=False;
Connection Timeout=30;
```

## Azure SQL Specific Features to Enable

### 1. **Automatic Tuning** 🤖
```sql
ALTER DATABASE [database] SET AUTOMATIC_TUNING = ON
ALTER DATABASE [database] SET AUTOMATIC_TUNING (CREATE_INDEX = ON, DROP_INDEX = ON, PLAN_CORRECTION = ON)
```

### 2. **Query Store** 📊
```sql
ALTER DATABASE [database] SET QUERY_STORE = ON
ALTER DATABASE [database] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, DATA_FLUSH_INTERVAL_SECONDS = 900)
```

### 3. **Geo-Replication** 🌍
Set up active geo-replication for disaster recovery

### 4. **Elastic Pools** 🏊
Consider for multiple databases with variable usage patterns

## Monitoring and Maintenance

### **Set Up Alerts** 📢
- High DTU/CPU utilization
- Storage usage thresholds  
- Failed connections
- Long-running queries

### **Regular Maintenance** 🔧
- Monitor Query Store for performance regressions
- Review automatic tuning recommendations
- Update statistics regularly
- Monitor and optimize resource usage

## Migration Tools Available Here
Use these tools to inspect your migrated database:
- **list_tables**: Verify all tables migrated
- **describe_table**: Check table structure and constraints  
- **read_data**: Sample data for validation
- **database_info**: Check database status and metrics
- **Resources**: Access schema and status information

## Common Migration Issues and Solutions

### **Compatibility Issues** 🔧
- Review deprecated features
- Update syntax for Azure SQL differences
- Test application compatibility thoroughly

### **Performance Issues** ⚡
- Update statistics after migration
- Recreate missing indexes
- Adjust compatibility level
- Enable automatic tuning

### **Connection Issues** 🔌
- Configure firewall rules
- Update connection strings
- Test connectivity from application servers
- Consider connection pooling optimization
            """
        
        @self.mcp.prompt("database_troubleshooting")
        async def database_troubleshooting() -> str:
            """Database troubleshooting and diagnostic guide"""
            return """
# Azure SQL Database Troubleshooting Guide

## Common Issues and Solutions

### 1. **Connection Issues** 🔌

#### **Firewall Problems**
```sql
-- Check current firewall rules (run from Azure Portal/Cloud Shell)
az sql server firewall-rule list --server [server-name] --resource-group [rg-name]

-- Add firewall rule for your IP
az sql server firewall-rule create --server [server-name] --resource-group [rg-name] --name AllowMyIP --start-ip-address [your-ip] --end-ip-address [your-ip]
```

#### **Authentication Issues**
- Verify username/password combination
- Check if Azure AD authentication is configured correctly
- Ensure user has proper database permissions

#### **Connection String Issues**
```
# Correct format for Azure SQL Database
Server=tcp:[server].database.windows.net,1433;Database=[database];User ID=[username];Password=[password];Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;
```

### 2. **Performance Issues** ⚡

#### **High CPU Usage**
```sql
-- Find CPU-intensive queries
SELECT TOP 10
    qs.sql_handle,
    qs.execution_count,
    qs.total_worker_time as total_cpu_time,
    qs.total_worker_time/qs.execution_count as avg_cpu_time,
    SUBSTRING(qt.text, (qs.statement_start_offset/2)+1, 
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(qt.text)
            ELSE qs.statement_end_offset
        END - qs.statement_start_offset)/2)+1) as statement_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY qs.total_worker_time DESC
```

#### **Blocking and Deadlocks**
```sql
-- Check for active blocks
SELECT 
    blocking_session_id,
    session_id,
    wait_duration_ms,
    wait_type,
    wait_resource
FROM sys.dm_exec_requests 
WHERE blocking_session_id <> 0

-- Enable deadlock monitoring
-- (Use Extended Events or Query Store)
```

#### **Memory Pressure**
```sql
-- Check memory usage
SELECT 
    CEILING(total_physical_memory_kb/1024.0) AS total_memory_mb,
    CEILING(available_physical_memory_kb/1024.0) AS available_memory_mb,
    CEILING((total_physical_memory_kb - available_physical_memory_kb)/1024.0) AS used_memory_mb,
    (total_physical_memory_kb - available_physical_memory_kb) * 100.0 / total_physical_memory_kb AS memory_usage_percentage
FROM sys.dm_os_sys_memory
```

### 3. **Storage Issues** 💾

#### **Database Size Monitoring**
```sql
-- Check database size and usage
SELECT 
    DB_NAME() AS database_name,
    CAST(SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS bigint) * 8192.) / 1024 / 1024 AS decimal(15,2)) AS space_used_mb,
    CAST(SUM(size) * 8192. / 1024 / 1024 AS decimal(15,2)) AS space_allocated_mb,
    CAST((SUM(size) - SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS int))) * 8192. / 1024 / 1024 AS decimal(15,2)) AS space_unused_mb
FROM sys.database_files
WHERE type IN (0,1)
```

#### **Log File Growth**
```sql
-- Check transaction log usage
SELECT 
    DB_NAME() AS database_name,
    CAST(total_log_size_in_bytes/1024.0/1024.0 AS decimal(15,2)) AS log_size_mb,
    CAST(used_log_space_in_bytes/1024.0/1024.0 AS decimal(15,2)) AS used_log_mb,
    used_log_space_in_percent
FROM sys.dm_db_log_space_usage
```

### 4. **Query Performance Issues** 🐌

#### **Slow Query Analysis**
```sql
-- Find slowest queries
SELECT TOP 10
    qs.total_elapsed_time/qs.execution_count as avg_elapsed_time,
    qs.execution_count,
    SUBSTRING(qt.text, (qs.statement_start_offset/2)+1, 
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(qt.text)
            ELSE qs.statement_end_offset
        END - qs.statement_start_offset)/2)+1) as statement_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY qs.total_elapsed_time/qs.execution_count DESC
```

#### **Missing Index Analysis**
```sql
-- Find missing index recommendations
SELECT 
    migs.avg_total_user_cost * (migs.avg_user_impact / 100.0) * (migs.user_seeks + migs.user_scans) AS improvement_measure,
    'CREATE INDEX [missing_index_' + CONVERT(varchar, mig.index_group_handle) + '_' + CONVERT(varchar, mid.index_handle) + ']'
    + ' ON ' + mid.statement + ' (' + ISNULL(mid.equality_columns,'') + CASE WHEN mid.equality_columns IS NOT NULL AND mid.inequality_columns IS NOT NULL THEN ',' ELSE '' END + ISNULL(mid.inequality_columns, '') + ')'
    + ISNULL(' INCLUDE (' + mid.included_columns + ')', '') AS create_index_statement,
    migs.*, mid.database_id, mid.[object_id]
FROM sys.dm_db_missing_index_groups mig
INNER JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details mid ON mig.index_handle = mid.index_handle
ORDER BY migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans) DESC
```

### 5. **Diagnostic Tools** 🔍

#### **Query Store Analysis**
```sql
-- Enable Query Store if not already enabled
ALTER DATABASE [database_name] SET QUERY_STORE = ON

-- Top resource consuming queries
SELECT TOP 10
    qsq.query_id,
    LEFT(qsqt.query_sql_text, 100) as query_text,
    qsp.avg_cpu_time,
    qsp.avg_logical_io_reads,
    qsp.avg_duration,
    qsp.execution_count
FROM sys.query_store_query_text qsqt
JOIN sys.query_store_query qsq ON qsqt.query_text_id = qsq.query_text_id
JOIN sys.query_store_plan qsp ON qsq.query_id = qsp.query_id
ORDER BY qsp.avg_cpu_time DESC
```

#### **Wait Statistics**
```sql
-- Identify wait types
SELECT TOP 10
    wait_type,
    wait_time_ms,
    percentage = CAST(100.0 * wait_time_ms / SUM(wait_time_ms) OVER() AS decimal(5,2)),
    avg_wait_time_ms = wait_time_ms / waiting_tasks_count
FROM sys.dm_os_wait_stats
WHERE wait_time_ms > 0
AND wait_type NOT IN ('CLR_SEMAPHORE','LAZYWRITER_SLEEP','RESOURCE_QUEUE','SLEEP_TASK','SLEEP_SYSTEMTASK','SQLTRACE_WAIT','WAITFOR')
ORDER BY wait_time_ms DESC
```

## Emergency Response Procedures

### **High Resource Usage** 🚨
1. Identify resource-intensive queries
2. Kill problematic sessions if necessary: `KILL [session_id]`
3. Scale up temporarily if needed
4. Implement query optimization

### **Connection Limit Reached** 🚪
```sql
-- Check current connections
SELECT 
    DB_NAME(database_id) as database_name,
    COUNT(*) as connection_count
FROM sys.dm_exec_sessions
WHERE database_id > 0
GROUP BY database_id
ORDER BY connection_count DESC
```

### **Deadlock Resolution** ⚰️
- Enable deadlock monitoring
- Analyze deadlock graphs
- Implement retry logic in applications
- Optimize transaction scope and order

## Monitoring Setup

### **Key Metrics to Monitor** 📊
- DTU/vCore percentage
- Storage usage percentage
- Connection count
- Average response time
- Error rate
- Blocked process count

### **Azure Monitor Integration**
Set up alerts for:
- CPU > 80% for 5 minutes
- Storage > 90%
- Failed connections > 10 per minute
- Long-running queries > 30 seconds

## Tools Available for Diagnostics
- **health_check**: Get current server health status
- **database_info**: Check database connection and metrics
- **read_data**: Execute diagnostic queries
- **database://status**: Access real-time status resource
- **list_tables**: Verify database objects
            """
        
        # Track registered prompts
        self._registered_prompts = [
            "sql_query_builder",
            "analyze_performance", 
            "data_migration_guide",
            "database_troubleshooting"
        ]
        
        logger.info(f"✅ Registered {len(self._registered_prompts)} prompts")
    
    def get_registered_prompts(self) -> list:
        """Get list of registered prompt names"""
        return self._registered_prompts.copy()
    
    def get_prompt_count(self) -> int:
        """Get number of registered prompts"""
        return len(self._registered_prompts)
    
    def get_prompt_summary(self) -> dict:
        """Get summary of available prompts"""
        return {
            "total_prompts": len(self._registered_prompts),
            "prompts": {
                "sql_query_builder": "Interactive SQL query builder with table-specific examples",
                "analyze_performance": "Query performance analysis and optimization guide",
                "data_migration_guide": "Comprehensive guide for migrating to Azure SQL Database",
                "database_troubleshooting": "Troubleshooting guide for common database issues"
            }
        }
