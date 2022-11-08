# Requirements
## Functional
Take an input CSV file of land registry paid prices and group the data by:
- REQ 1: Postcode
- REQ 2: Property within Postcode
- REQ 3: Date and Price of each Property

It should be possible to query the re-shaped data by postcode to see the history of all prices for all properties within that postcode.  Note, in the UK, a postcode usually equates to a single street (although not always in sparsley populated areas).

## Non-Functional
The implementation should be able to execute fully within an Azure environment.  Within this, the following are desired:
- NFR1: Low cost PaaS components should be used (serverless / no-ops)
- NFR2: Complexity should be reduced to a reasonable minimum, although achieving this should not override NFR1.
- NFR3: Data Egress costs should be minimised (ingress is usuall free) as the asusmption is that reads will far exceed writes.
- NFR4: The 'latest' land registry CSV file contains approx. 100,000 records, although this process should cater for an annual file (approx. 1 million rows).

# Design
## Approach 1
| Requirement | Azure Choice | Notes |
|:-------------|:--------------|:-------|
| REQ1/2/3 | Blob File | create a hierarchical document structure to group all properties within a postcode |
| NFR1 | Blob File | low-cost storage |
| NFR1 | Function | low-cost serverless compute (free montly executions) |
| NFR2 | Queue Storage | use as an intermediate store (functions are too limited for large memory grouping/sorting operations) |
| NFR3 | Blob File | groups many property prices and the hierarchical document structure de-duplicates data |
| NFR4 | Function | could possibly scale by multiple executions but cannot multi-thread or parallel process due to small resource size |
  
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
Creating queues by postcode results in over 100,000 queue creation requests.  Because of this, two test executions timed-out after 30 minutes.  Therefore, change the queue granularity to be the outcode (the first half of a postcode).  
Some outcodes are only 2 characters long.  This makes them impossible to create as a Queue (minimum name length = 3 characters), so append the prefix "landreg-" to each queue name.   

### Update 2
The resulting outcode process creates approximately 2,300 queues.  
Execution times across three tests for just queue creation averaged 7 minutes.
However, execution times including message insert always exceed the funciton app time-out after 30 minutes. 