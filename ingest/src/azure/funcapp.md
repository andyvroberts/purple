# Python
Install the funcation app library.  
```
py -m pip install azure-functions  
```
**1**  
Using the Azure CLI to create the function app in your chosen directory.    
```
func init --python
```
This will create an empty python file with the default app initialization.  

**2**  
Follow the instructions for the V2 programming model here:    
https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators   

Avoid using the CLI scaffolding as it does not yet seem to create accurate and well structured content as described by the V2 model.  

**3**  
Create a Github Action to deploy the Azure Function App components.   
https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-github-actions?tabs=linux%2Cpython&pivots=method-manual  

You will have to create an empty Function App in an Azure Subscription prior to a deploy, as this method assumes the Function App already exists.  







