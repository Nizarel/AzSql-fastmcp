-- Azure SQL Database Setup for FastMCP Server with Managed Identity
-- Run this script in your existing database: sqldb-yompagai-dev
-- Make sure to run this as an Azure AD administrator

USE [sqldb-yompagai-dev];
GO

-- Create database user for the managed identity: id-yompagai-dev
PRINT 'Creating user for managed identity: id-yompagai-dev';

-- Create user from the specific managed identity
CREATE USER [id-yompagai-dev] FROM EXTERNAL PROVIDER;

-- Grant necessary permissions for MCP operations
PRINT 'Granting permissions for database operations...';

-- Grant read permissions (for queries and table listing)
ALTER ROLE db_datareader ADD MEMBER [id-yompagai-dev];

-- Grant write permissions (for INSERT, UPDATE, DELETE operations)
ALTER ROLE db_datawriter ADD MEMBER [id-yompagai-dev];

-- Grant DDL permissions (for table structure queries and describe operations)
ALTER ROLE db_ddladmin ADD MEMBER [id-yompagai-dev];

PRINT 'Permissions granted successfully!';

-- Create some sample tables for testing (optional)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FastMCPTest')
BEGIN
    PRINT 'Creating sample table for testing...';
    CREATE TABLE FastMCPTest (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(500),
        CreatedDate DATETIME2 DEFAULT GETUTCDATE(),
        IsActive BIT DEFAULT 1
    );
    
    INSERT INTO FastMCPTest (Name, Description) VALUES 
    ('Test Record 1', 'Sample data for FastMCP testing'),
    ('Test Record 2', 'Another sample record'),
    ('Test Record 3', 'Third sample record for validation');
    
    PRINT 'Sample table created with test data.';
END
ELSE
BEGIN
    PRINT 'Sample table already exists.';
END

PRINT 'Database setup complete!';
PRINT '';
PRINT 'SUCCESS: Managed identity "id-yompagai-dev" has been configured with:';
PRINT '- db_datareader: Can read all tables and views';
PRINT '- db_datawriter: Can insert, update, delete data';
PRINT '- db_ddladmin: Can query table structures and metadata';
PRINT '';
PRINT 'The FastMCP server should now be able to connect using managed identity authentication.';
GO
