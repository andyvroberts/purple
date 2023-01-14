# Ingest Historical Land Registry Property Prices
Ingest the UK land registry update file of sold residential property prices.  Store them in table storage.  Create the application using Python.

## Application Design
[Read this file for the requirements, design choices and changes throughout the implementaton process](design.md)  

## Useful Information
### 1. Dotnet
Setup the dotnet and Azure SKD's before you do anything else.  
[Read this file for Azure setup and configuration](azure.md)  

### 2. Python
[Read this file for Python setup and configuration](python.md)  

### 3. Deploy an Aure Function App
[Read this file for CLI commands to create resources and the Functions Core Tools Deploy command](funcapp.md) 


## Execution Observations
### Function Timeouts
Sometimes a function app will timeout for an unknown reason. In these cases:
- load the same file again but..
- edit the configuration table and update the 'Total' column to zero for the outcodes impacted
- this will force re-execution at the next timer triggered process

### Queue Costs
Loading a 900k row dataset results in queue costs of approximately £0.75 per load.  Although this is by no means high, compared to table storage costs (£0.04) it is an order of magnitude larger.  We need to investigate queue storage options to see why this is the case.  

### Load 1995 Prices
Resulted in 2,299 outcode messages being placed onto the queue for the prices load trigger function.   The overall duration of the load process was 2 hours and 10 minutes.  
Prices Load Function ended up with:  
- 550 Success
- 5,651 Failures (each failed message was dequeued for retry operations, up to 5 times)  

The high number of failures resulted from a) function time-out when they ran for longer than 5 minutes or b) HTTP errors retrieving the CSV file.  
There are now 1,702 messages in the dead-letter queue.  

Using the default parallel execution options, a function app cannot cope with being asked to trigger over 2k jobs and manage the workload appropriately.  
According to the docs, Python functions on Linux can only scale out to a maximum of 100 concurrent instances.  
https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#scale

Replace the trigger queue visibiity from zero, to be in staggered 30-second intervals to avoid overlaoding the function executions.

Run the application insights query to determine success and failures.  
```
requests
| where timestamp > ago(7d)
| where success == False
| where appName == 'PurpleFunc002'
```

Next Prices Load Function resulted in:
- 2,291 Success
- 317 Failures (> 5 minute execution duration)

Automatic retries (up to 5 per queue message) during the load process mean that only 9 outcodes ended up in the poison queue.  These were manually added to the main queue where they ran to completion.

### Design Suitability
This design is just an interesting excercise using queue's and table storage.  For production purposes (or if you have plenty of Azure credits) the correct approach would be to use a data-lake and data warehouse appliance such as Databricks or Synapse analytics.  

So, even though there is not excessive code in this project, there is still far more than you would need to write if you followed the expected process of:
- downloading the entire source dataset
- grouping, sorting and filtering in-memory
- producing the output records in a single pass

The end.  


