-- ============================================================
-- Azure FastMCP Database Setup Script
-- ============================================================
-- IMPORTANT: Run this script as Azure AD administrator
-- Connect to: sql-yompagai-dev.database.windows.net
-- Database: sqldb-yompagai-dev
-- ============================================================

USE [sqldb-yompagai-dev];
GO

-- Create user for managed identity
PRINT 'Creating managed identity user: id-yompagai-dev';
CREATE USER [id-yompagai-dev] FROM EXTERNAL PROVIDER;
GO

-- Grant FastMCP permissions
PRINT 'Granting db_datareader permissions...';
ALTER ROLE db_datareader ADD MEMBER [id-yompagai-dev];
GO

PRINT 'Granting db_datawriter permissions...';
ALTER ROLE db_datawriter ADD MEMBER [id-yompagai-dev];
GO

PRINT 'Granting db_ddladmin permissions...';
ALTER ROLE db_ddladmin ADD MEMBER [id-yompagai-dev];
GO

PRINT 'Database setup completed successfully!';
PRINT 'Managed identity [id-yompagai-dev] now has:';
PRINT '  - READ access (db_datareader)';
PRINT '  - WRITE access (db_datawriter)';
PRINT '  - DDL access (db_ddladmin)';

-- Verify permissions
PRINT 'Verifying permissions...';
SELECT 
    dp.principal_id,
    dp.name AS principal_name,
    r.name AS role_name
FROM sys.database_principals dp
JOIN sys.database_role_members rm ON dp.principal_id = rm.member_principal_id
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
WHERE dp.name = 'id-yompagai-dev';
GO
