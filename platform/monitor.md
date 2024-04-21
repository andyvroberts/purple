# Azure Monitoring
For function apps, the currently (2024) recommended method is by application insights.  There is an introductory web page here: https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview.  

In addition, function apps are the only service which can be auto-instrumented across all languages.  See the table on this page: https://learn.microsoft.com/en-us/azure/azure-monitor/app/codeless-overview#supported-environments-languages-and-resource-providers.  However, this seems to mean that the resources you would otherwise organise yourself get auto-created with names and in locations you probably wouldn't choose.  We will create everything to our own specification.  

Azure log monitoring uses tables to store the logging and telemetry data.  Layouts of these tables can be found in the documentation [here](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/tables-resourcetype).  

## Log Analytics Workspace
This is still required in order to provide the underlying storage for logging and other telemetry, although it is now called an Operational Insights Workspace.  

To create a workspace, the Bicep tempate can be found here:  
https://learn.microsoft.com/en-us/azure/templates/microsoft.operationalinsights/workspaces?tabs=bicep&pivots=deployment-language-bicep  
  
## Application Insights
Or as it now seems to be called [Azure Monitor Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python#enable-azure-monitor-application-insights).  In a way, it is good MS are using a standard telemetry, trace, logs & metrics toolkit.  So, we're going to use this in all of our function apps.  You'll notice in the [environment.md](/environment.md) at the root of this project, included are the language specific imports required to use this framework.  

In the function app settings (or local.settings.json)  you may need to add the APPLICATIONINSIGHTS_CONNECTION_STRING=<your app insights connection string> as an additional entry.  For local testing, you can optionally export it as a local environment variable.  

Examples of using this in Python can be found here:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples.  

To create an application insights component, the Bicep template can be found here:  
https://learn.microsoft.com/en-us/azure/templates/microsoft.insights/components?pivots=deployment-language-bicep  



