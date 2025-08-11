// Main infrastructure deployment for Azure SQL FastMCP Server
// Uses existing SQL Server and Database
targetScope = 'resourceGroup'

// Parameters
@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Name of the environment (e.g., dev, test, prod)')
param environmentName string

// Existing SQL Configuration
@description('Existing Azure SQL Server name (without .database.windows.net suffix)')
param sqlServerName string

@description('Existing Azure SQL Database name')
param sqlDatabaseName string

@description('Resource group containing the existing SQL Server')
param existingSqlResourceGroup string

@description('Create new SQL resources (false to use existing)')
param createNewSqlResources bool = false

// FastMCP Server Configuration
@description('FastMCP HTTP host')
param mcpHttpHost string

@description('FastMCP HTTP port')
param mcpHttpPort string

@description('FastMCP API path')
param mcpApiPath string

@description('FastMCP health path')
param mcpHealthPath string

@description('FastMCP metrics path') 
param mcpMetricsPath string

@description('MCP connection timeout')
param mcpConnectionTimeout string

@description('MCP request timeout')
param mcpRequestTimeout string

@description('MCP heartbeat interval')
param mcpHeartbeatInterval string

@description('MCP enable error recovery')
param mcpEnableErrorRecovery string

// Variables
var resourceToken = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))
var resourceName = {
  containerAppsEnvironment: 'cae-${environmentName}-${resourceToken}'
  containerApp: 'ca-${environmentName}-${resourceToken}'
  containerRegistry: 'cr${toLower(environmentName)}${resourceToken}'
  keyVault: 'kv${take(resourceToken, 20)}' // Key Vault names must be <= 24 chars
  logAnalyticsWorkspace: 'law-${environmentName}-${resourceToken}'
  applicationInsights: 'ai-${environmentName}-${resourceToken}'
  managedIdentity: 'id-yompagai-dev'
}

var tags = {
  'azd-env-name': environmentName
  'project': 'azsql-fastmcp'
  'purpose': 'FastMCP Azure SQL Server'
}

// User-assigned managed identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: resourceName.managedIdentity
  location: location
  tags: tags
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: resourceName.logAnalyticsWorkspace
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 90
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: resourceName.applicationInsights
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: resourceName.containerRegistry
  location: location
  tags: tags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: false
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
      exportPolicy: {
        status: 'enabled'
      }
      azureADAuthenticationAsArmPolicy: {
        status: 'enabled'
      }
      softDeletePolicy: {
        retentionDays: 7
        status: 'disabled'
      }
    }
    encryption: {
      status: 'disabled'
    }
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: 'Disabled'
  }
}

// Grant managed identity ACR pull permissions
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, managedIdentity.id, 'AcrPull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: resourceName.keyVault
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    accessPolicies: [
      {
        tenantId: tenant().tenantId
        objectId: managedIdentity.properties.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: false
    vaultUri: 'https://${resourceName.keyVault}.vault.azure.net/'
    provisioningState: 'Succeeded'
    publicNetworkAccess: 'Enabled'
  }
}

// Reference to existing SQL Server (no creation)
resource existingSqlServer 'Microsoft.Sql/servers@2023-08-01-preview' existing = {
  name: sqlServerName
  scope: resourceGroup(existingSqlResourceGroup)
}

// Reference to existing SQL Database (no creation)
resource existingSqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' existing = {
  name: sqlDatabaseName
  parent: existingSqlServer
}

// Store SQL connection string in Key Vault (using existing SQL resources)
resource sqlConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'sql-connection-string'
  properties: {
    value: 'Server=tcp:${sqlServerName}.database.windows.net,1433;Database=${sqlDatabaseName};Authentication=Active Directory Managed Identity;Encrypt=true;TrustServerCertificate=false;Connection Timeout=${mcpConnectionTimeout};'
    contentType: 'text/plain'
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: resourceName.containerAppsEnvironment
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
    kedaConfiguration: {}
    daprConfiguration: {}
    customDomainConfiguration: {}
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    peerAuthentication: {
      mtls: {
        enabled: false
      }
    }
  }
}

// Container App
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: resourceName.containerApp
  location: location
  tags: union(tags, {
    'azd-service-name': 'azsql-fastmcp'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: managedIdentity.id
        }
      ]
      secrets: [
        {
          name: 'sql-connection-string'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/sql-connection-string'
          identity: managedIdentity.id
        }
        {
          name: 'appinsights-connection-string'
          value: applicationInsights.properties.ConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'azsql-fastmcp'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'AZURE_SQL_SERVER'
              value: '${sqlServerName}.database.windows.net'
            }
            {
              name: 'AZURE_SQL_DATABASE'  
              value: sqlDatabaseName
            }
            {
              name: 'AZURE_SQL_AUTH_TYPE'
              value: 'managed_identity'
            }
            {
              name: 'AZURE_MANAGED_IDENTITY_CLIENT_ID'
              value: managedIdentity.properties.clientId
            }
            {
              name: 'MCP_HTTP_HOST'
              value: mcpHttpHost
            }
            {
              name: 'MCP_HTTP_PORT'
              value: mcpHttpPort
            }
            {
              name: 'MCP_API_PATH'
              value: mcpApiPath
            }
            {
              name: 'MCP_HEALTH_PATH'
              value: mcpHealthPath
            }
            {
              name: 'MCP_METRICS_PATH'
              value: mcpMetricsPath
            }
            {
              name: 'MCP_CONNECTION_TIMEOUT'
              value: mcpConnectionTimeout
            }
            {
              name: 'MCP_REQUEST_TIMEOUT'
              value: mcpRequestTimeout
            }
            {
              name: 'MCP_HEARTBEAT_INTERVAL'
              value: mcpHeartbeatInterval
            }
            {
              name: 'MCP_ENABLE_ERROR_RECOVERY'
              value: mcpEnableErrorRecovery
            }
            {
              name: 'MCP_ENABLE_COMPRESSION'
              value: 'true'
            }
            {
              name: 'MCP_ENABLE_CORS'
              value: 'true'
            }
            {
              name: 'MCP_MAX_CONCURRENT_REQUESTS'
              value: '100'
            }
            {
              name: 'LOG_LEVEL'
              value: 'INFO'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              secretRef: 'appinsights-connection-string'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: mcpHealthPath
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 30
              periodSeconds: 30
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: mcpHealthPath
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output RESOURCE_GROUP_ID string = resourceGroup().id

output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.id
output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = containerAppsEnvironment.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = 'https://${containerRegistry.properties.loginServer}'
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.name

output AZURE_KEY_VAULT_NAME string = keyVault.name
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.properties.vaultUri

output AZURE_SQL_SERVER string = '${sqlServerName}.database.windows.net'
output AZURE_SQL_DATABASE string = sqlDatabaseName
output AZURE_SQL_CONNECTION_STRING string = 'Server=tcp:${sqlServerName}.database.windows.net,1433;Database=${sqlDatabaseName};Authentication=Active Directory Managed Identity;Encrypt=true;TrustServerCertificate=false;Connection Timeout=${mcpConnectionTimeout};'

output SERVICE_WEB_ENDPOINT_URL string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output SERVICE_WEB_NAME string = containerApp.name

output AZURE_LOG_ANALYTICS_WORKSPACE_NAME string = logAnalyticsWorkspace.name
output AZURE_APPLICATION_INSIGHTS_NAME string = applicationInsights.name

output MANAGED_IDENTITY_CLIENT_ID string = managedIdentity.properties.clientId
output MANAGED_IDENTITY_PRINCIPAL_ID string = managedIdentity.properties.principalId
