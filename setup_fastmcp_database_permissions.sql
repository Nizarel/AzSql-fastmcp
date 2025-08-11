-- =============================================
-- Azure SQL Database - Managed Identity Setup
-- FastMCP Server Database Permissions
-- =============================================
-- Run this script as an Azure AD administrator on database: sqldb-yompagai-dev
-- Server: sql-yompagai-dev.database.windows.net
-- Managed Identity: id-yompagai-dev

-- Connect to your target database
USE [sqldb-yompagai-dev];
GO

-- Step 1: Create user for the managed identity
PRINT 'Creating user for managed identity: id-yompagai-dev';
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'id-yompagai-dev')
BEGIN
    CREATE USER [id-yompagai-dev] FROM EXTERNAL PROVIDER;
    PRINT '✅ User [id-yompagai-dev] created successfully';
END
ELSE
BEGIN
    PRINT '⚠️  User [id-yompagai-dev] already exists';
END
GO

-- Step 2: Grant database reader permissions
PRINT 'Granting db_datareader role...';
ALTER ROLE db_datareader ADD MEMBER [id-yompagai-dev];
PRINT '✅ db_datareader role granted';
GO

-- Step 3: Grant database writer permissions  
PRINT 'Granting db_datawriter role...';
ALTER ROLE db_datawriter ADD MEMBER [id-yompagai-dev];
PRINT '✅ db_datawriter role granted';
GO

-- Step 4: Grant DDL admin permissions (for schema operations)
PRINT 'Granting db_ddladmin role...';
ALTER ROLE db_ddladmin ADD MEMBER [id-yompagai-dev];
PRINT '✅ db_ddladmin role granted';
GO

-- Step 5: Verify the user and permissions were created correctly
PRINT 'Verifying managed identity user creation...';
SELECT 
    name as username,
    type_desc as user_type,
    authentication_type_desc as auth_type,
    create_date,
    modify_date
FROM sys.database_principals 
WHERE name = 'id-yompagai-dev';

PRINT 'Verifying role memberships...';
SELECT 
    dp.name as principal_name,
    dp.type_desc as principal_type,
    r.name as role_name
FROM sys.database_principals dp
JOIN sys.database_role_members rm ON dp.principal_id = rm.member_principal_id
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
WHERE dp.name = 'id-yompagai-dev'
ORDER BY r.name;

PRINT '🎉 Managed Identity setup complete!';
PRINT 'Your FastMCP server should now be able to connect to this database.';

-- Optional: View current database schema for reference
PRINT 'Current database tables:';
SELECT 
    t.TABLE_SCHEMA as schema_name,
    t.TABLE_NAME as table_name,
    t.TABLE_TYPE as table_type
FROM INFORMATION_SCHEMA.TABLES t
WHERE t.TABLE_TYPE = 'BASE TABLE'
ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME;
