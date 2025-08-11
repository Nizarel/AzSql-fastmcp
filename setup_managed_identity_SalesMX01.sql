-- ====================================================================
-- Azure SQL Database Setup for Managed Identity: rg-yompagai-dev
-- Server: agenticdbsv.database.windows.net
-- Database: SalesMX01
-- ====================================================================

-- ============================================
-- STEP 1: Connect to MASTER database first
-- ============================================
-- Execute this section while connected to the 'master' database

USE master;
GO

-- Create the managed identity user in master database
PRINT 'Creating managed identity user in master database...';
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'rg-yompagai-dev')
BEGIN
    CREATE USER [rg-yompagai-dev] FROM EXTERNAL PROVIDER;
    PRINT '✅ User [rg-yompagai-dev] created in master database';
END
ELSE
BEGIN
    PRINT '⚠️ User [rg-yompagai-dev] already exists in master database';
END
GO

-- ============================================
-- STEP 2: Connect to SalesMX01 database
-- ============================================
-- Execute this section while connected to the 'SalesMX01' database

USE [SalesMX01];
GO

-- Create the managed identity user in target database
PRINT 'Creating managed identity user in SalesMX01 database...';
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'rg-yompagai-dev')
BEGIN
    CREATE USER [rg-yompagai-dev] FROM EXTERNAL PROVIDER;
    PRINT '✅ User [rg-yompagai-dev] created in SalesMX01 database';
END
ELSE
BEGIN
    PRINT '⚠️ User [rg-yompagai-dev] already exists in SalesMX01 database';
END
GO

-- ============================================
-- STEP 3: Grant necessary permissions
-- ============================================

PRINT 'Granting database permissions...';

-- Grant data reader permissions
IF IS_ROLEMEMBER('db_datareader', 'rg-yompagai-dev') = 0
BEGIN
    ALTER ROLE db_datareader ADD MEMBER [rg-yompagai-dev];
    PRINT '✅ Granted db_datareader role to [rg-yompagai-dev]';
END
ELSE
BEGIN
    PRINT '⚠️ [rg-yompagai-dev] already has db_datareader role';
END

-- Grant data writer permissions
IF IS_ROLEMEMBER('db_datawriter', 'rg-yompagai-dev') = 0
BEGIN
    ALTER ROLE db_datawriter ADD MEMBER [rg-yompagai-dev];
    PRINT '✅ Granted db_datawriter role to [rg-yompagai-dev]';
END
ELSE
BEGIN
    PRINT '⚠️ [rg-yompagai-dev] already has db_datawriter role';
END

-- Grant DDL admin permissions (for schema operations)
IF IS_ROLEMEMBER('db_ddladmin', 'rg-yompagai-dev') = 0
BEGIN
    ALTER ROLE db_ddladmin ADD MEMBER [rg-yompagai-dev];
    PRINT '✅ Granted db_ddladmin role to [rg-yompagai-dev]';
END
ELSE
BEGIN
    PRINT '⚠️ [rg-yompagai-dev] already has db_ddladmin role';
END

-- Grant execute permissions for stored procedures
GRANT EXECUTE TO [rg-yompagai-dev];
PRINT '✅ Granted EXECUTE permissions to [rg-yompagai-dev]';
GO

-- ============================================
-- STEP 4: Verification and Status Check
-- ============================================

PRINT '============================================';
PRINT 'VERIFICATION: Checking user and permissions';
PRINT '============================================';

-- Check if user exists and show details
SELECT 
    name AS UserName,
    type_desc AS UserType,
    authentication_type_desc AS AuthenticationType,
    create_date AS CreateDate,
    modify_date AS ModifyDate
FROM sys.database_principals 
WHERE name = 'rg-yompagai-dev';

-- Check role memberships
PRINT '';
PRINT 'Role Memberships:';
SELECT 
    dp.name AS PrincipalName,
    dp.type_desc AS PrincipalType,
    r.name AS RoleName
FROM sys.database_role_members rm
    JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
    JOIN sys.database_principals dp ON rm.member_principal_id = dp.principal_id
WHERE dp.name = 'rg-yompagai-dev'
ORDER BY r.name;

-- Check specific permissions
PRINT '';
PRINT 'Specific Permissions:';
SELECT 
    dp.name AS UserName,
    dp.type_desc AS UserType,
    p.permission_name AS Permission,
    p.state_desc AS PermissionState,
    COALESCE(o.name, s.name, 'DATABASE') AS ObjectName,
    COALESCE(o.type_desc, 'SCHEMA', 'DATABASE') AS ObjectType
FROM sys.database_permissions p
    LEFT JOIN sys.objects o ON p.major_id = o.object_id
    LEFT JOIN sys.schemas s ON p.major_id = s.schema_id
    LEFT JOIN sys.database_principals dp ON p.grantee_principal_id = dp.principal_id
WHERE dp.name = 'rg-yompagai-dev'
ORDER BY p.permission_name;

-- Test basic access
PRINT '';
PRINT 'Testing basic database access...';
SELECT 
    'Database Access Test' AS TestType,
    DB_NAME() AS DatabaseName,
    SYSTEM_USER AS CurrentUser,
    GETDATE() AS CurrentTime;

PRINT '';
PRINT '🎉 Setup completed successfully!';
PRINT 'Managed identity [rg-yompagai-dev] is ready for use with SalesMX01 database';
PRINT '';
PRINT 'Next steps:';
PRINT '1. Deploy your application with managed identity assigned';
PRINT '2. Configure environment variables (AZURE_SQL_AUTH_TYPE=managed_identity)';
PRINT '3. Test the connection using your MCP server';
GO
