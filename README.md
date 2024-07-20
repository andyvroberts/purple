# Purple-V2: Create a Query Endpoint for Accessing UK Property Prices by Postcode
Requirement:  
Create sets of UK Property Prices, grouped by Postcode, to be queried by a sample web application.  

[![Deploy Queue Trigger Azure Function App](https://github.com/andyvroberts/purple/actions/workflows/funcapp.qt.cs.deploy.yml/badge.svg)](https://github.com/andyvroberts/purple/actions/workflows/funcapp.qt.cs.deploy.yml)


## Project Structure  
The project has 4 components.  The ingest folder is for data acquisition and organising price records at the postcode grouping.  The PurpleFuncs folder is for the Azure functions that store prices and also allows clients to retrieve price data based on a postcode lookup.  The app folder contains a simple Web App which is the UX. Finally, the platform folder contains the Bicep IaC.  
```bash
├── app
│   └── src (javascript & css)
├── ingest
│   └── file-scanner-py
│       └── src (local price file scan using python)
├── platform
│   └── PurpleFunc (bicep and azure cli files)
│       └── 01-app-insights
│       └── 02-purple-funcs
└── PurpleFuncs (C# functionapp code)
```

### 1. App


### 2. Ingest
Locally run Python modules perform 2 functions:  
1. Create a list of postcodes available in the PPD file.
2. Per outcode, push each postcode set of prices to an Azure queue.

### 3. Platform


### 4. PurpleFuncs

<br>






