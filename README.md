![Build Status](https://github.com/avroberts-azure/purple/actions/workflows/test-deploy.yml/badge.svg)

# Ingest Historical Land Registry Property Prices
Ingest the UK land registry update file of sold residential property prices.  Store them in table storage.  Create the application using Python.

## Application Design
[Read this file for the requirements, design choices and changes throughout the implementaton process](docs/design.md)  

## Useful Information
### 1. Dotnet
Setup the dotnet and Azure SKD's before you do anything else.  
[Read this file for Azure setup and configuration](docs/azure.md)  

### 2. Python
[Read this file for Python setup and configuration](docs/python.md)  

### 3. Deploy an Aure Function App
[Read this file for CLI commands to create resources and the Functions Core Tools Deploy command](docs/funcapp.md) 

<br>

## Montly Costs Tracker

| Month | Data | Function App | Total |
|:-------------|:--------------|:-------|:------------|
| 2023-04 |  | | |
| 2023-03 | (2.3gb/6m rows) £0.34 | £0.93  | £1.27 |


