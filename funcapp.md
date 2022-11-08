# Function App Deploy



## Deployment pre-requisites
Application Insights is mandatory when deploying/creating a function app in Azure.  If you don't specify one then a default one will be automatically created.  It is best to configure your own so you can choose the settings.

### Log Analytics Workspace
Each application insights instance will require a log analytics workspace, which must be specified on app insight creation.  

Setup variables for CLI commands.
```
export resgrp=UkLandregMonitor   
export workspacename=uklandreg-logs  
```
First create a resource group.
```
az group create --name $resgrp --location uksouth  
```
Then create the log analytics workspace. Set the daily ingest quota to 0.3 of a Gb (close to 300 Mb) and retain logs for 30 days (the free default).  
```
az monitor log-analytics workspace create \
  --workspace-name $workspacename \
  --resource-group $resgrp \
  --ingestion-access Enabled \
  --location uksouth \
  --quota 0.3 \
  --retention-time 30
```

You must pay for data ingestion and data retention in the workspace so check the docs:  
https://azure.microsoft.com/en-gb/pricing/details/monitor/ 