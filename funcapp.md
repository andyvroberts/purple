# Function App Deploy
In order to deploy a function app, we first need to setup the Azure resources.  For full automation, you could do this with IaS using Azure specific Bicep templates, but in this example we are going to start with learning how to create them using the Azure CLI.  

This is the order in which to create or manage the resources:
1. Resource group and storage account for the application (not the function app)
2. Log analytics workspace (required for application insights)
3. Application insights instance (mandatory for a function app)
4. An empty Azure Function App Component
5. Custom function app settings (transfer any custom local.settings.json settings to Azure)
6. Azure Core Tools Deployment

Note: Application Insights is mandatory when deploying/creating a function app in Azure.  If you don't specify one yourself, then a default one will be automatically created.  It is best to configure your own so you can choose the settings.  


## 1. Application Resources
If you already have a business data storage account then you don't need to do this step.
   
First create the application resource group.  
```
export apprg=UkLandregApp  
az group create --name $apprg --location uksouth  
```
Storage account names must be globally unique, so check it is available.  
```
az storage account check-name -n uklandregappdata  
```
If all ok, then create the storage account to be used for storing business data.  
```
export appstore=uklandregappdata  

az storage account create \
  --name $appstore \
  --resource-group $apprg \
  --location uksouth \
  --kind StorageV2 \
  --sku Standard_LRS
```

Get this storage account connection string and set it as the 'LandregDataStorage' value in the Python local.settings.json file.  
```
az storage account show-connection-string -n $appstore -g $apprg -o tsv
```

Note: You can query for a list of locations that are valid for your Azure account.
```
az account list-locations --query "[].{Region:name}" --out table
```


## 2. Log Analytics Workspace
Each application insights instance will require a log analytics workspace, which must be specified on app insight creation in step 3.  

Setup variables for CLI commands.
```
export wkspacerg=UkLandregMonitor   
export spacename=uklandreg-logs  
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
To enable logging and monitoring of our function app when it eventually runs in Azure, we need to create an application insights component.  
Setup variables and issue the app-insights create command. 
```
export insightsname=uklandreg-insights  

az monitor app-insights component create \
  --app $insightsname \
  --location uksouth \
  --resource-group $wkspacerg \
  --application-type function \
  --workspace $spacename \
  --kind function-app
```

https://docs.microsoft.com/en-us/cli/azure/ext/application-insights/monitor/app-insights?view=azure-cli-latest  

Once created you will need the instrumentation key which is displayed on the overview page of the resource.  


## 4. Empty Function App
Before deploying, we need to setup the Azure Function app component and its settings.  
```
export faresgrp=UkLandregFuncs  
export fastoreacc=uklandregfuncsdata  
```

The function app will have its own resource group and storage accont.  
```
az group create --name $faresgrp --location uksouth

az storage account check-name -n $fastoreacc

az storage account create \
  --name $fastoreacc \
  --resource-group $faresgrp \
  --location uksouth \
  --kind StorageV2 \
  --sku Standard_LRS
```

Get this storage account connection string and make sure it is the one set as the 'AzureWebJobsStorage' value in the Python local.settings.json file.  
```
az storage account show-connection-string -n $fastoreacc -g $faresgrp -o tsv
```

Setup variables for the Azure function app name and retrieve the application insight instrumentation key (this key is used by Azure to connect the function app to the application insight instance for monitoring).  
```
export funcname=landreg-purple
export instrumentationkey=$(az monitor app-insights component show --app $insightsname --resource-group $wkspacerg --query 'instrumentationKey' -o tsv)
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
  --app-insights-key $instrumentationkey \
  --consumption-plan-location uksouth \
  --functions-version 4 \
  --os-type linux \
  --runtime python \
  --runtime-version 3.9
```


## 5. App Settings
The storage account of the function app is NOT the same as the one used for land registry data. The *AzureWebJobStorage* will have been set to the $fastoreacc when creating the "az functionapp create" command above.  

To make sure we are inserting land registry data into the correct storage account it is easier to use a specifically named app setting.  

Our function app uses the "LandregDataStorage" key for business data, in the local.settings.json file.  
This must be specifically created and added to the Azure function app settings before deployment.  

https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#application-settings-in-azure

Add the business data storage account to our function app settings.  
```
export businessdatastorage=$(az storage account show-connection-string -n $appstore -g $apprg -o tsv)
export dataurl=http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv

az functionapp config appsettings set \
  --name $funcname \
  --resource-group $faresgrp \
  --settings "LandregDataStorage=$businessdatastorage" "PriceDataURL=$dataurl"
```

At anytime you can list the settings to make sure everything exists as you expect.
```
az functionapp config appsettings list  -n $funcname -g $faresgrp -o table
```

Check we have created everything we need by listing out the contents of our function app resource group and showing the config.  
```
az resource list -g $faresgrp -o table
az functionapp config show -n $funcname -g $faresgrp
```

## 6. Deployment
At long last!  
Make sure you are in the root directory as the function app to be published.  

Generate a requirements file so Azure can install the correct Python packages when you publish.
```
py -m pip freeze > requirements.txt
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
  --linux-fx-version "Python|3.9"
```

Then use the Azure functions core tools command (not a CLI command).
```
func azure functionapp publish $funcname
``` 
Note: If you are re-deploying the function app after modifying it, you will need to ensure that the **Function App** is active in Azure, otherwise you will receive trigger synch errors.  
  
https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash#project-file-deployment

You can also use this command to publish the local any settings (local.settings.json) in which case you would not need to use the CLI command "az functionapp config appsettings set".


# Funcapp Deploy rebuild after deletion
Sometimes, you just need to delete the function app from azure and re-create it to clear a lot of bad stats and noise.  This assumes that you are leaving the resource groups, storage accounts and app insights components in place and you have not removed them. 

## Setup the env variables.
```
export apprg=UkLandregApp
export appstore=uklandregappdata

export faresgrp=Purple002  
export fastoreacc=purpledata002 
export funcname=PurpleFunc002

export businessdatastorage=$(az storage account show-connection-string -n $appstore -g $apprg -o tsv)
export dataurl=ttp://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-1995.csv
```

## Function App
```
az group create --name $faresgrp --location uksouth
```
Storage.
```
az storage account create \
  --name $fastoreacc \
  --resource-group $faresgrp \
  --location uksouth \
  --kind StorageV2 \
  --sku Standard_LRS
```
Func app component.
```
az functionapp create \
  --name $funcname \
  --resource-group $faresgrp \
  --storage-account $fastoreacc \
  --consumption-plan-location uksouth \
  --functions-version 4 \
  --os-type linux \
  --runtime python \
  --runtime-version 3.9
```
App Settings.
```
az functionapp config appsettings set \
  --name $funcname \
  --resource-group $faresgrp \
  --settings "LandregDataStorage=$businessdatastorage" "PriceDataURL=$dataurl"
```

## Deploy
Deploy, if re-deploy also make sure you have defined the $funcname.
```
export funcname=PurpleFunc002

func azure functionapp publish $funcname
```

# Github Action to Deploy
Follow the instructions here:  
https://github.com/Azure/functions-action#using-publish-profile-as-deployment-credential-recommended  

Add the publish profile contents from the Azure Function to github:  
```
Settings > Secrets & Variables > Actions > New reposiroty secret
```
In the YML file, make sure to run the deploy workflow ONLY when something in the actual function code has changed.   
Accomplish by only including the specific code folders for the **on: push:** github action.  
```
on:
  push:
    branches:
    - ["main"]
    paths:
    - 'purple/outcode_scanner/**'
    - 'purple/prices_loader/**'
    - 'purple/utils/**'
```

