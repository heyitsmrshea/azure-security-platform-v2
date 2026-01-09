// Azure Security Platform V2 - Infrastructure
// Deploy with: az deployment sub create --location eastus --template-file main.bicep

targetScope = 'subscription'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Primary location for resources')
param location string = 'eastus'

@description('Resource group name')
param resourceGroupName string = 'rg-security-platform-${environment}'

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: resourceGroupName
  location: location
  tags: {
    environment: environment
    application: 'azure-security-platform'
    managedBy: 'bicep'
  }
}

// Deploy resources to resource group
module resources 'resources.bicep' = {
  name: 'deploy-resources'
  scope: rg
  params: {
    environment: environment
    location: location
  }
}

output resourceGroupId string = rg.id
output cosmosDbEndpoint string = resources.outputs.cosmosDbEndpoint
output redisHostName string = resources.outputs.redisHostName
output keyVaultUri string = resources.outputs.keyVaultUri
output appServiceUrl string = resources.outputs.appServiceUrl
