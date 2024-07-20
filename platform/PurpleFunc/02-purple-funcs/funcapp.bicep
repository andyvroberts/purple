targetScope = 'resourceGroup'
@description('the parameters needed to deploy all Azure resources for a function app')
param azLocation string
param azTags object
param projShortName string 
param projVersion string 
param storageName string

var hostPlanName = '${projShortName}Farm${projVersion}'
var insightsName = '${projShortName}Insights${projVersion}'
var functionName = '${projShortName}Funcs${projVersion}'

// Get a reference to the seperate configuration storage account (table storage)
resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' existing = {
  scope: resourceGroup()
  name: storageName
}

// Get a reference to the previously created app insights in the same RG.
resource insights 'Microsoft.Insights/components@2020-02-02' existing = {
  scope: resourceGroup()
  name: insightsName
}

// default to windows.
@description('Create the App Service Plan for the Server Farm. sku Y1 is the free tier.')
resource hostingPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: hostPlanName
  location: azLocation
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {}
  tags: azTags
}

// Deploy as windows running LTS dotnet isolated (8.0)
@description('Create the Function App with references to all other resources')
resource functionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: functionName
  location: azLocation
  kind: 'functionapp'
  identity: {
    type:'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: insights.properties.ConnectionString
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'dotnet-isolated'
        }
        {
          name: 'LandregDataStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
      ]
      ftpsState: 'FtpsOnly'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
  tags: azTags
}
