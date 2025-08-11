targetScope@minLength(1)
@description('Name of the resource group')
param resourceGroupName string = 'rg-${environmentName}'

// Existing SQL Configuration (Using Existing Resources)cription'

// Parameters
@minLength(1)
@description('Primary location for all resources')
param location string = 'eastus2'

@minLength(1)  
@description('Name of the environment (e.g., dev, test, prod)')
param environmentName string

@minLength(1)
@description('Name of the resource group')
param resourceGroupName string = 'rg-${environmentName}'

// Generate a unique suffix for resource naming
param resourceToken string = toLower(uniqueString(subscription().id, rg.id, environmentName))

// Database Configuration Parameters (Using Existing Resources)
@description('Existing Azure SQL Server name (without .database.windows.net suffix)')
param sqlServerName string = 'sql-yompagai-dev'

@description('Existing Azure SQL Database name')
param sqlDatabaseName string = 'sqldb-yompagai-dev'

@description('Resource group containing the existing SQL Server')
param existingSqlResourceGroup string = 'rg-yompagai-dev'

@description('Create new SQL resources (false to use existing)')
param createNewSqlResources bool = false

// FastMCP Server Configuration
@description('FastMCP server HTTP host (0.0.0.0 for container apps)')
param mcpHttpHost string = '0.0.0.0'

@description('FastMCP server HTTP port')
param mcpHttpPort string = '8000'

@description('FastMCP API path')
param mcpApiPath string = '/mcp'

@description('FastMCP health check path')
param mcpHealthPath string = '/health'

@description('FastMCP metrics path')
param mcpMetricsPath string = '/metrics'

@description('MCP connection timeout in seconds')
param mcpConnectionTimeout string = '30'

@description('MCP request timeout in seconds')
param mcpRequestTimeout string = '120'

@description('MCP heartbeat interval in seconds')
param mcpHeartbeatInterval string = '60'

@description('Enable MCP error recovery')
param mcpEnableErrorRecovery string = 'true'

// Create the resource group
resource rg 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: resourceGroupName
  location: location
  tags: {
    'azd-env-name': environmentName
    'project': 'azsql-fastmcp'
    'purpose': 'FastMCP Azure SQL Server'
  }
}

// Deploy main infrastructure
module mainResources 'main.bicep' = {
  scope: rg
  name: 'main-resources'
  params: {
    location: location
    environmentName: environmentName
    resourceToken: toLower(uniqueString(subscription().id, rg.id, environmentName))
    sqlServerName: sqlServerName
    sqlDatabaseName: sqlDatabaseName
    existingSqlResourceGroup: existingSqlResourceGroup
    createNewSqlResources: createNewSqlResources
    mcpHttpHost: mcpHttpHost
    mcpHttpPort: mcpHttpPort
    mcpApiPath: mcpApiPath
    mcpHealthPath: mcpHealthPath
    mcpMetricsPath: mcpMetricsPath
    mcpConnectionTimeout: mcpConnectionTimeout
    mcpRequestTimeout: mcpRequestTimeout
    mcpHeartbeatInterval: mcpHeartbeatInterval
    mcpEnableErrorRecovery: mcpEnableErrorRecovery
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name

output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = mainResources.outputs.AZURE_CONTAINER_APPS_ENVIRONMENT_ID
output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = mainResources.outputs.AZURE_CONTAINER_APPS_ENVIRONMENT_NAME
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = mainResources.outputs.AZURE_CONTAINER_REGISTRY_ENDPOINT
output AZURE_CONTAINER_REGISTRY_NAME string = mainResources.outputs.AZURE_CONTAINER_REGISTRY_NAME

output AZURE_KEY_VAULT_NAME string = mainResources.outputs.AZURE_KEY_VAULT_NAME
output AZURE_KEY_VAULT_ENDPOINT string = mainResources.outputs.AZURE_KEY_VAULT_ENDPOINT

output AZURE_SQL_SERVER string = mainResources.outputs.AZURE_SQL_SERVER
output AZURE_SQL_DATABASE string = mainResources.outputs.AZURE_SQL_DATABASE
output AZURE_SQL_CONNECTION_STRING string = mainResources.outputs.AZURE_SQL_CONNECTION_STRING

output SERVICE_WEB_ENDPOINT_URL string = mainResources.outputs.SERVICE_WEB_ENDPOINT_URL
output SERVICE_WEB_NAME string = mainResources.outputs.SERVICE_WEB_NAME

output AZURE_LOG_ANALYTICS_WORKSPACE_NAME string = mainResources.outputs.AZURE_LOG_ANALYTICS_WORKSPACE_NAME
output AZURE_APPLICATION_INSIGHTS_NAME string = mainResources.outputs.AZURE_APPLICATION_INSIGHTS_NAME
