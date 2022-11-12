# Azure Table Storage
Read the docs.  
https://learn.microsoft.com/en-us/python/api/overview/azure/data-tables-readme?view=azure-python  

Start by installing the SDK into the virtual environment.
```
py -m pip install azure-data-tables.
```

You will need a table client before you can interact with the storage service.  There are several methods by which you can instantiate a valid client, we will use the storage account connection string as we already have it in our configuration (local.settings.json & Function App settings in Azure).  
```
from azure.data.tables import TableServiceClient

storage_conn_str = os.getenv('LandregDataStorage')
tab_service = TableServiceClient.from_connection_string(storage_conn_str)
```

See the github Python samples.  
https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/tables/azure-data-tables/samples
  
