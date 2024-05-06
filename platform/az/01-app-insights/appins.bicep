@description('the parameters needed to deploy all Azure resources for App Insights')
param azLocation string
param azTags object
param logRetention int
param workspaceName string
param insightsName string
param dailyQuota int
param workspaceSku string


resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: azLocation
  tags: azTags
  properties: {
    sku: {
      name: workspaceSku
    }
    retentionInDays: logRetention
    features: {
      enableLogAccessUsingOnlyResourcePermissions: false
    }
    workspaceCapping: {
      dailyQuotaGb: dailyQuota
    }    
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: insightsName
  location: azLocation
  tags: azTags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    ImmediatePurgeDataOn30Days: true
    IngestionMode: 'string'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    Request_Source: 'rest'
    RetentionInDays: logRetention
    WorkspaceResourceId: workspace.id
  }
}
