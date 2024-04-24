

// Get a reference to the seperate data lake storage account (data lake)
resource dataLake 'Microsoft.Storage/storageAccounts@2019-06-01' existing = {
  scope: resourceGroup(dataLakeRg)
  name: dataLakeName
}
