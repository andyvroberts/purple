## Python Setup

### Setup pip and venv.
```python
sudo apt-get install python3-venv
sudo apt install python3-pip
```

### Setup a Virtual Environment.  
From within the *src* code directory, add the **.venv** folder and activate a new virtual environment called 'purple'.  This gives us a clean python starting point.   
```python
cd src
mkdir .venv
python3 -m venv .venv/purple
source .venv/purple/bin/activate
```
Add the required Azure SDK libs.
```
py -m pip install azure-data-tables
py -m pip install azure-storage-queue
```
Add the open telemetry libs for application insights monitoring.  
```
py -m pip install azure-monitor-opentelemetry
```

### Linux Environment Variables
To connect to an Azure storage account, we will create clients (table and queue) using whichever Azure Python SDK ".from_connection_string" function is needed.  In order for this to work, a Linux environment variable must be set:  
```
export LandregDataStorage="connection string"
```

In WSL/ChromeOS, closing the session removes the variable.