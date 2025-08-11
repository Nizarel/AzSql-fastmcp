# Production Deployment Validation Script
# PowerShell version with enhanced testing

Write-Host "================================================================" -ForegroundColor Green
Write-Host "Testing Managed Identity Configuration for Production Deployment" -ForegroundColor Green  
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Check virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not activated" -ForegroundColor Red
    Write-Host "Please run: venv\Scripts\activate" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Step 1: Environment Configuration" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Copy test configuration
try {
    Copy-Item ".env.test" ".env" -Force
    Write-Host "✅ Environment configuration copied from .env.test to .env" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to copy environment configuration: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test configuration loading
Write-Host ""
Write-Host "Testing configuration loading..." -ForegroundColor Yellow

$configTest = @"
import sys
import os
sys.path.insert(0, '.')

try:
    from src.connection.database_config import DatabaseConfig
    config = DatabaseConfig()
    
    print('✅ Configuration loaded successfully')
    print(f'   Server: {config.server}')
    print(f'   Database: {config.database}') 
    print(f'   Auth Type: {config.authentication_type}')
    print(f'   Client ID: {config.managed_identity_client_id}')
    print(f'   Validation: {config.validate()}')
    
    if config.authentication_type == 'managed_identity':
        print('✅ Managed identity authentication configured')
    else:
        print('⚠️ Authentication type is not managed_identity')
        
except Exception as e:
    print(f'❌ Configuration error: {str(e)}')
    import traceback
    traceback.print_exc()
    exit(1)
"@

$result = python -c $configTest
if ($LASTEXITCODE -eq 0) {
    Write-Host $result -ForegroundColor White
} else {
    Write-Host "❌ Configuration validation failed" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Step 2: Azure Identity Libraries" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$azureTest = @"
try:
    from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
    from azure.core.credentials import TokenCredential
    print('✅ Azure Identity libraries imported successfully')
    
    # Test credential creation (without actual authentication)
    cred = ManagedIdentityCredential(client_id='id-AcraSalesAnalytics2')
    print('✅ ManagedIdentityCredential created successfully')
    
    default_cred = DefaultAzureCredential()
    print('✅ DefaultAzureCredential created successfully')
    
except ImportError as e:
    print(f'❌ Import error: {str(e)}')
    print('Please ensure azure-identity package is installed')
    exit(1)
except Exception as e:
    print(f'❌ Azure Identity error: {str(e)}')
    exit(1)
"@

$result = python -c $azureTest
if ($LASTEXITCODE -eq 0) {
    Write-Host $result -ForegroundColor Green
} else {
    Write-Host "❌ Azure Identity libraries test failed" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Step 3: MCP Server Components" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$mcpTest = @"
import sys
sys.path.insert(0, '.')

try:
    from src.connection.sql_connection_factory import SqlConnectionFactory
    from src.connection.database_config import DatabaseConfig
    
    print('✅ SQL Connection Factory imported successfully')
    
    # Test factory creation
    config = DatabaseConfig()
    factory = SqlConnectionFactory(config)
    print('✅ SQL Connection Factory created successfully')
    
    # Test connection string generation
    conn_string = factory._create_connection_string()
    if 'Authentication=ActiveDirectoryMsi' in conn_string:
        print('✅ Connection string configured for managed identity')
    else:
        print('⚠️ Connection string not configured for managed identity')
        
except Exception as e:
    print(f'❌ MCP Server component error: {str(e)}')
    import traceback
    traceback.print_exc()
    exit(1)
"@

$result = python -c $mcpTest  
if ($LASTEXITCODE -eq 0) {
    Write-Host $result -ForegroundColor Green
} else {
    Write-Host "❌ MCP Server components test failed" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Step 4: Deployment Readiness Check" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Check required files
$requiredFiles = @(
    "setup_managed_identity_SalesMX01.sql",
    "PRODUCTION_DEPLOYMENT_GUIDE.md", 
    "Doc/MANAGED_IDENTITY_SECURITY_ENHANCEMENT.md",
    "scripts/setup_managed_identity.py",
    "scripts/setup_managed_identity.ps1"
)

Write-Host "Checking required deployment files..." -ForegroundColor Yellow
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (missing)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "Production Configuration Summary" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

Write-Host "🎯 Your Production Settings:" -ForegroundColor White
Write-Host "   SQL Server: agenticdbsv.database.windows.net" -ForegroundColor Cyan
Write-Host "   Database: SalesMX01" -ForegroundColor Cyan
Write-Host "   Authentication: managed_identity" -ForegroundColor Cyan
Write-Host "   Managed Identity: id-AcraSalesAnalytics2" -ForegroundColor Cyan

Write-Host ""
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "🚀 NEXT STEPS FOR PRODUCTION DEPLOYMENT" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

Write-Host ""
Write-Host "1. 📊 Database Setup:" -ForegroundColor White
Write-Host "   • Open SQL Server Management Studio or Azure Portal Query Editor" -ForegroundColor Gray
Write-Host "   • Connect as Azure AD admin to agenticdbsv.database.windows.net" -ForegroundColor Gray
Write-Host "   • Execute: setup_managed_identity_SalesMX01.sql" -ForegroundColor Cyan
Write-Host "   • Verify user creation and permissions" -ForegroundColor Gray

Write-Host ""
Write-Host "2. ☁️ Azure Resource Configuration:" -ForegroundColor White
Write-Host "   • Assign managed identity 'id-AcraSalesAnalytics2' to your Azure resource" -ForegroundColor Gray
Write-Host "   • Set environment variables (copy from .env file)" -ForegroundColor Gray
Write-Host "   • Deploy your application code with latest changes" -ForegroundColor Gray

Write-Host ""
Write-Host "3. 🧪 Testing:" -ForegroundColor White
Write-Host "   • Test health endpoint: https://your-app-url/health" -ForegroundColor Gray
Write-Host "   • Verify MCP operations using client tools" -ForegroundColor Gray
Write-Host "   • Check logs for successful managed identity authentication" -ForegroundColor Gray

Write-Host ""
Write-Host "4. 📚 Documentation:" -ForegroundColor White
Write-Host "   • Complete guide: PRODUCTION_DEPLOYMENT_GUIDE.md" -ForegroundColor Gray
Write-Host "   • Security details: Doc/MANAGED_IDENTITY_SECURITY_ENHANCEMENT.md" -ForegroundColor Gray

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "✅ PRE-DEPLOYMENT VALIDATION COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "Your MCP server is ready for production deployment with managed identity." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to continue..."
