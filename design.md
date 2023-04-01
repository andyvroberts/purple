# Requirements
## Functional
Take an input CSV file of land registry paid prices and group the data by:
- REQ 1: Postcode
- REQ 2: Property within Postcode
- REQ 3: Date and Price of each Property

It should be possible to query the re-shaped data by postcode to see the history of all prices for all properties within that postcode.  Note, in the UK, a postcode usually equates to a single street (although not always in sparsley or very densely populated areas).

## Non-Functional
The implementation should be able to execute fully within an Azure environment.  Within this, the following are desired:
- NFR1: Low cost PaaS components should be used (serverless / no-ops)
- NFR2: Complexity should be reduced to a reasonable minimum, although achieving this should not override NFR1.
- NFR3: Data Egress costs should be minimised (ingress is usually free) as the asusmption is that reads will far exceed writes.
- NFR4: The 'latest' land registry CSV file contains approx. 100,000 records, although this process should cater for an annual file (approx. 1 million rows).

# Design
## Phase 1  
| Requirement | Azure Choice | Notes |
|:-------------|:--------------|:-------|
| REQ1/2/3 | Blob File | create a hierarchical document structure to group all properties within a postcode |
| NFR1 | Blob File | low-cost storage |
| NFR1 | Function | low-cost serverless compute (free montly executions) |
| NFR2 | Queue Storage | use as an intermediate store (functions are too limited for large memory grouping/sorting operations) |
| NFR3 | Blob File | groups many property prices and the hierarchical document structure de-duplicates data |
| NFR4 | Function | could possibly scale by multiple executions but cannot multi-thread or parallel process within a single function due to small resource size |
  
Create a single python function app, with a timer trigger, to stream read the land registry CSV file, and write each property record to queue storage specifically associated to single postcode.  

Azure Queue Storage has these capacity constraints:
- Maximum size is 500Tb for all queue's within a storage account
- Message max size is 64Kb
- Maximum TTL (time to live) is 7 days
- Unlimited number of queues

Function App processing steps:
- Stream source data file
- Decode record and determine its postcode
- Create the queue if it does not exist
- Store decoded record to queue
  
### Update 1
Git branch "full-file"  
Creating queues by postcode results in over 100,000 queue creation requests.  Because of this, two test executions timed-out locally after 30 minutes (Azure consumption plan time-out is 5 minutes).  Therefore, change the queue granularity to be the outcode (the first half of a postcode).  
Some outcodes are only 2 characters long.  This makes them impossible to create as a Queue (minimum name length = 3 characters), so append the prefix "landreg-" to each queue name.   

### Update 2
Git branch "full-file"  
The resulting outcode process creates approximately 2,300 queues.  
Execution times across three tests for just queue creation averaged 7 minutes.
However, execution times including message insert always exceed the funciton app time-out after 30 minutes. 

The next option is to split our workload into much smaller units that can each run within under 5 minutes.  Firstly, try to load a single outcode of price records into a queue.  Choose the outcode with the largest number of records in the file, and run locally.  If ok, publish to Azure and run as a test.  
In the monthly update file, outcode **B5** has 257 records.
In the yearly 2019 file, outcode **CR0** has 2,133 records.
Optimise the queue client creation and and message send operations.

### Update 3
Git branch "per-outcode"  
Timing for single Outcode storage queue inserts
| Job | Queue Inserts | Approx Time |
|:-----|:---------|:-------------|
| Monthly Update (local) | 257 | 11 secs. |
| 2019 Yearly (local) | 2,133 | 1 min, 31 secs.|
| 2020 Yearly (local) | 2,338 | 1 min, 27 secs. |
| 2020 Yearly (Azure) | 2,338 | 53 secs. |
| 2020 Yearly (Azure) | 2,338 | 55 secs. |
  
To complete the design, there are now some additional steps required.   
- Determine when the Outcode records for the monthly update file have changed.  Triger this process on a timer.     
    - Read the file and create a distinct list of Outcodes, totaling the price value of all price records as they are processed
    - Read configuration for the previous price total of each Outcode  
    - If the total is different, send a message to the "Execution" storage queue with the outcode as the payload  
    - If the total is different, replace the new total value into the configuration record  
    - Create a Function App that is triggered by a message in the "Execution" storage queue and process the insert for the outcode given
    - Execute the Outcode specific Queue insert process
  
### Update 4
Git branch "outcode-config"  
Configuration should be saved across executions.  This should use Azure Table Storage.
  
Azure *Table storage* has these limitations:
|Feature | Limitation |
|:--------------|:----------------|
|Unique Key per Entity|2 values: Partition Key + Row Key|
|Max Columns (properties) per Row|252|
|Max Row Size (data) |1Mb|
|Max Key Size (each) |1kb|

Table storage records can also be inserted in batches of 100 records.  Use this feature to reduce the number of API calls when inserting config.
  
### Update 5
Table storage proved to be so easy to use, I decided to also make it the price record storage medium, replacing the previous design choice of blobs.  The additinal benefits of this are the ability to query rows by partition + row keys and to perform upsert (insert if new, else update) operations on rows.

Price records:
- There should only be 1 record per property
- Prices should be stored in a column as a list (array) of tuples (date:price:rectype)
- The partition key should be the Postcode
- The row key should be the address

This has also changed our NFR list:  
| Requirement | Azure Choice | Notes |
|:-------------|:--------------|:-------|
| REQ1/2/3 | Table Storage | create a key-value pair data entity to group all properties within a postcode, within an outcode |
| NFR1 | Table Storage | low-cost storage |
| NFR1 | Function | low-cost serverless compute (free montly executions) |
| NFR2 | Queue Storage | use as an intermediate store (functions are too limited for large memory grouping/sorting operations) |
| NFR3 | Table Storage | groups many property prices into a single address data entity and so helps to de-duplicates data (rows) |
| NFR4 | Function | can scale out to parallel executions using queue storage as an orchestration mechanism, ensuring data is appropriately partitioned |
    
Note: for the 2019 price file, the outcode CR0 has approximatly 1,100 distinct postcodes from the 2,133 records.  
   
### Update 6  
Git branch "price-table" & "price-table2"  
We encountered another timing issue when inserting many rows into Azure table storage.  A single threaded python process can insert approximately 1000 rows within a 5-minute window, although the this leaves a narrow margin of safety.   

There are only 2 ways to increase table storage insert performance.  Either parallel process or insert in batches of 100.  We will choose to insert price records in batches but this means we must alter our partition key, as all records belonging ot a single batch insert must be for the same partition key.

Price records:
- Partition key is outcode (already our grouping in queue's by outcode)
- Row key is now the postcode followed by the address
- Address and postcode should also now be stored as an additional non-key column
    
### Update 7
Git branch "main"  
As queue triggers expect the payload to be base64 encoded, so make sure that any message you put on a queue which acts as an orchestration trigger is encoded properly.  

Also, using Azure log analytics workspace has a fixed cost associated, and the table storage tables that are inserted during log capture cannot be truncated easily.  For these reasons we are going to remove the logging workspace and let Azure created a default application insights instance within the function app resource group.  

Running the end-to-end process locally results in a large parallel effort to execute 2,300 functions to load records by outcodes into the individual queue's and then 2,300 functions to convert and load those into table storage.  
In order to slow this down and monitor the executing functions, we have set the visiblity timeout of messages being created on the load-outcode queue to + 30 seconds on each consecutive outcode record set.  This has the effect of spacing out the executions.   

### Update 8
Remove the increasing visibilty timeout on the load-outcode queue.  Set the config to load the first avaialable yearly price file in the PriceDataURL setting.  This begins with 1995.

Set the schedule of the outcode_scanner to run once a week on a Monday at 9am.

publish the function app to Azure.

### Update 9
After considering how to reduce queue usage and reduce execution time, the following design changes were made.  

**(A)** The outcode scanner switched to using a blob file to contain the list of outcodes and their summed prices.
This results in a large reduction in execution time, as the blob is read on startup and written out again at the end of the process.  Avoiding 2,300 reads and (potential) updates saved approximately 3 minutes.  

**(B)** The middle collection of queues holding outcode-specific sets of price records was removed.  The process which populated those queues not directly inserts the set of outcode prices into table storage.  
This results in reduction to just a single queue used as the trigger for a distributed load process.  

As before, the schedule of the outcode_scanner is set to run once a week.

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