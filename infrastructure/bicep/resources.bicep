// Azure Security Platform V2 - Resources Module

param environment string
param location string

var baseName = 'secplatform${environment}'
var uniqueSuffix = uniqueString(resourceGroup().id)

// CosmosDB Account
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  name: '${baseName}-cosmos-${uniqueSuffix}'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
  tags: {
    environment: environment
    application: 'azure-security-platform'
  }
}

// CosmosDB Database
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: cosmosAccount
  name: 'security_platform'
  properties: {
    resource: {
      id: 'security_platform'
    }
  }
}

// CosmosDB Containers
var containers = [
  { name: 'tenants', partitionKey: '/id', ttl: -1 }
  { name: 'security_scores', partitionKey: '/tenantId', ttl: 7776000 }
  { name: 'findings', partitionKey: '/tenantId', ttl: 31536000 }
  { name: 'alerts', partitionKey: '/tenantId', ttl: 7776000 }
  { name: 'backup_status', partitionKey: '/tenantId', ttl: 7776000 }
  { name: 'audit_logs', partitionKey: '/tenantId', ttl: 7776000 }
  { name: 'dashboard_snapshots', partitionKey: '/tenantId', ttl: 31536000 }
]

resource cosmosContainers 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = [for container in containers: {
  parent: cosmosDb
  name: container.name
  properties: {
    resource: {
      id: container.name
      partitionKey: {
        paths: [container.partitionKey]
        kind: 'Hash'
      }
      defaultTtl: container.ttl
    }
  }
}]

// Redis Cache
resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: '${baseName}-redis-${uniqueSuffix}'
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    redisConfiguration: {
      'maxmemory-policy': 'volatile-lru'
    }
  }
  tags: {
    environment: environment
    application: 'azure-security-platform'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${baseName}-kv-${uniqueSuffix}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
  }
  tags: {
    environment: environment
    application: 'azure-security-platform'
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${baseName}-plan-${uniqueSuffix}'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
  tags: {
    environment: environment
    application: 'azure-security-platform'
  }
}

// App Service (Backend)
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: '${baseName}-api-${uniqueSuffix}'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'COSMOS_ENDPOINT'
          value: cosmosAccount.properties.documentEndpoint
        }
        {
          name: 'REDIS_URL'
          value: 'rediss://${redisCache.properties.hostName}:6380'
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
      ]
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
  tags: {
    environment: environment
    application: 'azure-security-platform'
  }
}

// Static Web App (Frontend)
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: '${baseName}-web-${uniqueSuffix}'
  location: 'eastus2' // Static Web Apps have limited regions
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: 'out'
    }
  }
  tags: {
    environment: environment
    application: 'azure-security-platform'
  }
}

// Outputs
output cosmosDbEndpoint string = cosmosAccount.properties.documentEndpoint
output redisHostName string = redisCache.properties.hostName
output keyVaultUri string = keyVault.properties.vaultUri
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
output staticWebAppUrl string = staticWebApp.properties.defaultHostname
