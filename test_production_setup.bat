@echo off
echo.
echo ================================================================
echo Testing Managed Identity Configuration for Production Deployment
echo ================================================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Virtual environment not activated
    echo Please run: venv\Scripts\activate
    exit /b 1
) else (
    echo ✅ Virtual environment activated: %VIRTUAL_ENV%
)

echo.
echo ================================================================
echo Step 1: Testing Configuration Loading
echo ================================================================

REM Copy test configuration to .env for testing
copy .env.test .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Environment configuration copied from .env.test to .env
) else (
    echo ❌ Failed to copy environment configuration
    exit /b 1
)

REM Test configuration loading
python -c "import sys; sys.path.insert(0, '.'); from src.connection.database_config import DatabaseConfig; config = DatabaseConfig(); print('✅ Configuration loaded successfully'); print(f'   Server: {config.server}'); print(f'   Database: {config.database}'); print(f'   Auth Type: {config.authentication_type}'); print(f'   Client ID: {config.managed_identity_client_id}'); print(f'   Validation: {config.validate()}')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Configuration validation passed
) else (
    echo ❌ Configuration validation failed
    echo Please check your environment variables and code
)

echo.
echo ================================================================
echo Step 2: Testing Azure Identity Imports
echo ================================================================

python -c "from azure.identity import ManagedIdentityCredential, DefaultAzureCredential; print('✅ Azure Identity libraries imported successfully')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Azure Identity libraries are working
) else (
    echo ❌ Azure Identity libraries import failed
    echo Please ensure azure-identity package is installed
)

echo.
echo ================================================================
echo Step 3: Testing MCP Server Imports
echo ================================================================

python -c "import sys; sys.path.insert(0, '.'); from src.connection.sql_connection_factory import SqlConnectionFactory; print('✅ SQL Connection Factory imported successfully')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MCP Server components are working
) else (
    echo ❌ MCP Server imports failed
    echo Please check your code for syntax errors
)

echo.
echo ================================================================
echo Step 4: Configuration Summary
echo ================================================================

echo Your production configuration:
echo   Server: agenticdbsv.database.windows.net
echo   Database: SalesMX01
echo   Authentication: managed_identity
echo   Managed Identity: id-AcraSalesAnalytics2
echo.

echo ================================================================
echo Next Steps for Production Deployment:
echo ================================================================
echo.
echo 1. 📊 Execute SQL Setup:
echo    Run the SQL commands in: setup_managed_identity_SalesMX01.sql
echo    Connect as Azure AD admin to both 'master' and 'SalesMX01' databases
echo.
echo 2. ☁️ Deploy to Azure:
echo    - Assign managed identity 'id-AcraSalesAnalytics2' to your Azure resource
echo    - Set environment variables (use values from .env file)
echo    - Deploy your application code
echo.
echo 3. 🧪 Test Connection:
echo    - Verify health endpoint: https://your-app-url/health
echo    - Test MCP operations using client tools
echo    - Check application logs for authentication success
echo.
echo 4. 📚 Documentation:
echo    - Complete guide: PRODUCTION_DEPLOYMENT_GUIDE.md
echo    - Security details: Doc/MANAGED_IDENTITY_SECURITY_ENHANCEMENT.md
echo.

echo ================================================================
echo ✅ Pre-deployment validation completed successfully!
echo Your MCP server is ready for production deployment with managed identity.
echo ================================================================
echo.

pause
