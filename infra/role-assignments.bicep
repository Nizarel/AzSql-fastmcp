// Role assignments for managed identity
targetScope = 'resourceGroup'

@description('Principal ID of the managed identity')
param managedIdentityPrincipalId string

@description('Container Registry name')
param containerRegistryName string

@description('Key Vault name')
param keyVaultName string

@description('Existing SQL Server resource ID (if using existing SQL resources)')
param existingSqlServerResourceId string = ''

// Container Registry - ACR Pull role
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, managedIdentityPrincipalId, 'AcrPull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Key Vault - Key Vault Secrets User role
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource keyVaultSecretsUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, managedIdentityPrincipalId, 'Key Vault Secrets User')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// SQL Server - SQL DB Contributor role (if using existing SQL resources)
resource existingSqlServer 'Microsoft.Sql/servers@2023-05-01-preview' existing = if (!empty(existingSqlServerResourceId)) {
  name: split(existingSqlServerResourceId, '/')[8] // Extract server name from resource ID
  scope: resourceGroup(split(existingSqlServerResourceId, '/')[4]) // Extract resource group from resource ID
}

resource sqlDbContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(existingSqlServerResourceId)) {
  scope: existingSqlServer
  name: guid(existingSqlServerResourceId, managedIdentityPrincipalId, 'SQL DB Contributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '9b7fa17d-e63e-47b0-bb0a-15c516ac86ec') // SQL DB Contributor
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}
