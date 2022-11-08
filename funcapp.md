# Function App Deploy
In order to deploy a function app, we first need to setup the Azure resources.  You can do this with IaS using Azure specific Bicep templates, but in this example we are going to start with learning how to create them using the Azure CLI.

This is the order in which to create or manage the resources:
1. Resource group and storage account for the application (not the function app)
2. Log analytics workspace (mandatory for a function app)
3. Application insights instance (mandatory for a function app)
4. An empty Function app
5. Custom function app settings (transfer any local.settings.json settings to Azure)
6. Azure Core Tools Deployment

Note: Application Insights is mandatory when deploying/creating a function app in Azure.  If you don't specify one yourself, then a default one will be automatically created.  It is best to configure your own so you can choose the settings.  


## 1. Application Resources
If you already have a storage account then you don't need to do this step.
   
First create the application resource group.  
```
export apprg=UkLandregApp  
az group create --name $apprg --location uksouth  
```
Storage account names must be globally unique, so check it is available.  
```
az storage account check-name -n uklandregappdata  
```
If all ok, then create it.  
```
export appstore=uklandregappdata  

az storage account create \
  --name $appstore \
  --resource-group $apprg \
  --location uksouth \
  --kind StorageV2 \
  --sku Standard_LRS
```

You can query for a list of locations that are valid for your Azure account.
```
az account list-locations --query "[].{Region:name}" --out table
```


## 2. Log Analytics Workspace
Each application insights instance will require a log analytics workspace, which must be specified on app insight creation in step 3.  

Setup variables for CLI commands.
```
export wkspacerg=UkLandregMonitor   
export spacename=uklandregWorkspace  
```
First create a resource group.
```
az group create --name $wkspacerg --location uksouth  
```
Then create the log analytics workspace. Set the daily ingest quota to 0.3 of a Gb (close to 300 Mb - the smallest allowed) and retain logs for 30 days (the free default).  
```
az monitor log-analytics workspace create \
  --workspace-name $spacename \
  --resource-group $wkspacerg \
  --ingestion-access Enabled \
  --location uksouth \
  --quota 0.3 \
  --retention-time 30
```

You must pay for data ingestion and data retention in the workspace so check the docs:  
https://azure.microsoft.com/en-gb/pricing/details/monitor/  


## 3. Application Insights Instance
To enable logging and monitoring of our function app when it eventually runs, we need to create an application insights component.  
Setup variables for CLI commands.  
```
export insightsname=uklandreg-insights  
```
Then create the app insight instance  
```
az monitor app-insights component create \
  --app $insightsname \
  --location uksouth \
  --resource-group $wkspacerg \
  --application-type function \
  --workspace $wkspacename \
  --kind function-app
```

https://docs.microsoft.com/en-us/cli/azure/ext/application-insights/monitor/app-insights?view=azure-cli-latest  

Once created you will need the instrumentation key which is displayed on the overview page of the resource.  

### Function Resources
Choose some names for the resources and add them as local variables to save typing in names repeatedly.  
```
export faresgrp=UkLandregFuncs  
export fastoreacc=uklandregfuncsdata  
```

check the storage account name, as they must be gloally unique in Azure.
```
az storage account check-name -n $fastoreacc
```

if all ok create a resource group to contain the infrastructure that will share a common lifetime, include the associated storage account.
```
az group create --name $faresgrp --location uksouth
```

The storage account being created here is only for the function app deployment and will not contain the application data which could span multiple function apps if they are created.
```
az storage account create \
  --name $fastoreacc \
  --resource-group $faresgrp \
  --location uksouth \
  --kind StorageV2 \
  --sku Standard_LRS
```

### Function App
We need to create the infrastructure that is our application.  This step assumes you already have an app service plan, such as a consumptionplan.  Remember to align the function version with the runtime you are using for development.

Setup variables to get the application insight instrumentation key.
```
export insightapp=landreg-insights
export insightrg=UkLandregMonitor
```

Then setup the variables to create the function app.  Note that the funcname will need to change for each app you deploy.
```
export funcname=landreg-marmalade
export instrumentationkey=$(az monitor app-insights component show --app $insightapp --resource-group $insightrg --query 'instrumentationKey' -o tsv)
```

If creating a python runtime, check the supported versions and make sure you set this, otherwise the function will default to 'dotnet' which will give you big problems when attempting the deployment later.
```
az functionapp list-runtimes  
az functionapp list-runtimes --os linux --query "[].{stack:join(' ', [runtime, version]), LinuxFxVersion:linux_fx_version, SupportedFunctionsVersions:to_string(supported_functions_versions[])}" --output table  
```

Next create the empty functions app.
See https://docs.microsoft.com/en-us/cli/azure/functionapp?view=azure-cli-latest#az_functionapp_create for latest syntax.

```
az functionapp create \
  --name $funcname \
  --resource-group $faresgrp \
  --storage-account $fastoreacc \
  --app-insights $funcname \
  --app-insights-key $instrumentationkey \
  --consumption-plan-location uksouth \
  --functions-version 4 \
  --os-type linux \
  --runtime python \
  --runtime-version 3.8
```
In case you were wondering, if you do not specify your own application insights resources, they will be created automatically by Azure when you create a function app.
Also, if you are using a linux OS then you must specify the --os-type flag, otherwise the 'functionapp create' command will believe you are on windows.

Creating the app will automatically start it.  You can stop this by finding the function app ID.


### Functionapp Information
Check we have created everything we need by listing out the contents of our function app resource group.
```
az resource list -g $faresgrp -o table
```
and see what parameters have been set.
```
az functionapp config appsettings list -n $funcname -g $faresgrp -o table
az functionapp config show -n $funcname -g $faresgrp
```

### App Settings
The storage account of the function app is NOT the same as the one used for land registry data. The *AzureWebJobStorage* will have been set to the $fastoreacc when creating the "az functionapp create" command above.  

To make sure we are inserting land registry data into the correct storage account it is easier to use a specifically named app setting.  

Our function app uses the "LandregDataStorage" key in the local.settings.json file.  
This must be specifically created and populated within the Azure function app settings before deployment.  

https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#application-settings-in-azure

Add the storage account to our function app settings.  
```
export appstorage=$(az storage account show-connection-string -n marmaladedata -g marmalade-rg -o tsv)
az functionapp config appsettings set \
  --name $funcname \
  --resource-group $faresgrp \
  --settings "LandregDataStorage=$appstorage"
```

List the settings to make sure everything exists as you expect.
```
az functionapp config appsettings list  -n $funcname -g $faresgrp -o table
```

### Deployment
At long last!  
Make sure you are in the root directory as the function app to be published.  

Generate a requirements file so Azure can install the correct Python packages when you publish.
```
py38 -m pip freeze > requirements.txt
```

If you did not set the python (runtime) version when creating the empty function app, then ensure you set it now before the deployment.
https://learn.microsoft.com/en-us/azure/azure-functions/set-runtime-version?tabs=portal#manual-version-updates-on-linux

First check what the existing linux fx (python) version.
```
az functionapp config show --name $funcname --resource-group $faresgrp --query 'linuxFxVersion'
```

If it is not what you want, then make sure to set it now.
```
az functionapp config set \
  --name $funcname \
  --resource-group $faresgrp \
  --linux-fx-version "PYTHON|3.8"
```

Then use the Azure functions core tools command (not a CLI command).
```
func azure functionapp publish $funcname
``` 

https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash#project-file-deployment

You can also use this command to publish the local any settings (local.settings.json) in which case you would not need to use the CLI command "az functionapp config appsettings set".

