# Python Installs
My main system is a Linux Debian variant, with a Python3.9.2 version installed.  We will stick with this version for our application.  
To setup our Python environment, we need to:
1. Installs of Pip and Venv
2. Create the Python Function App
3. Create a virtual environment
4. Create a startup shell script
5. Azure Queue Storage SDK

  
## 1. Install PIP and VENV
In this case, I will use **venv** as the Virtual environment manager.  Make sure it is installed.  
```
sudo apt-get install python3-venv
```
Note: Venv only manages packages within projects, it cannot manage packages between python versions.  
  
If not present, add pip for the existing python3.9 major version.  You need to use apt within Debian.
```
sudo apt install python3-pip
```


## 2. Create a Function App
Read the docs  
https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level  

At this time (October 22), the Functions App Python programming model is **V1**.  
It is possible to use the V2 preview, but in this case we are not using V2.  

Pay attention to:
1. you must generate a python requirements.txt before publishing the function app to Azure
2. each function is a directory
3. you can use another (non-function) directory as a module for shared code
4. you should re-set the PYTHONPATH to the project root directory (in this example, 'purple')
5. the project root directory should contain the tests folder.
6. make sure you are on a supported Python version, as these are what Azure will use (in Oct 22, function v4.0 can use any minor version within the python major versions of 3.8 or 3.9)  

First initialise the python function called 'purple'.  
```
func init purple --python
```

Navigate into the new directory "purple", then create a function.  Use the templates list command if you need it.  
```
func templates lists -l python
func new --name get_landreg_updates --template "Timer trigger"
```
For cron expressions see this web page:  
https://github.com/atifaziz/NCrontab

To run a timer function app immediately, set the 'runOnStartup' configuration within the function.json file.  *Remember to remove this setting before deploying to your subscription.*   
```
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "mytimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 */30 * * * *",
      "runOnStartup": true
    }
  ]
}
```

You may also find is useful during testing to disable a particular function.  To do this set the 'disabled' flag to true.  
```
{
  "disabled": true,
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "mytimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 */2 * * * "
    }
  ]
}
```


## 3. Virtual Environment
From within the project root (as instructed by the programming model folder structure), create a new '.venv' directory so you can add the virtual environment and activite it.  
Make sure you are in the project root directory 'purple'.
```
mkdir .venv
py -m venv ~/projects/purple/purple/.venv/landreg
. ~/projects/purple/purple/.venv/landreg/bin/activate
```

From the activated venv, first install the Azure Function requirements from the scaffolded 'requirements.txt' file, then install the additional Python Azure SDKs we need.  
```
py -m pip install -r requirements.txt
py -m pip install azure-storage-queue
```


## 4. Startup Script
Always set the python path so modules can be imported between project base-level folders, and VS code linters, etc. can function correctly.
```
export PYTHONPATH=~/projects/purple/purple
```
  
If you have installed anything with a --user flag, you also need to put your user 'bin' folder references into the PATH environment variable.  To do this, add the following 2 lines to your .profile settings. 
```
PATH="$HOME/bin:$PATH"
PATH="$HOME/.local/bin:$PATH"
```
  
Optionally, create a command file to run to make your settings easier when starting development.  Place these instructions in an executable shell script.  
```
. ~/projects/purple/purple/.venv/landreg/bin/activate
cd ~/projects/purple/purple
export PYTHONPATH=~/projects/purple/purple
code ~/projects/purple
```
Ensure you chmod the file to make it run, then execute when required
```
. landreg.sh
```


## 5. Azure Queue Storage
Always look at the latest MS docs pages for Queue syntax and operations, to make sure you are using the most up-to-date and supported methods for authentication, queue creation and message writes/reads.

https://learn.microsoft.com/en-gb/azure/storage/queues/storage-python-how-to-use-queue-storage?tabs=python%2Cenvironment-variable-windows

https://github.com/azure/azure-storage-python

https://github.com/Azure-Samples/storage-queue-python-getting-started

https://github.com/azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue
  
These are the imports you may require, with their purpose:
- QueueClient: Allows interaction with a specific Queue
- BinaryBase64EncodePolicy: Convert a utf/string to binary (optional)
- BinaryBase64DecodePolicy: Convert binary to a utf/string (optional)

To create a queue, you will need to pass in the storage account connection string.  
Add a 'LandRegDataStorage' key in local.settings.json file with the right storage account connection string.  

In the Python Function, this can be referenced using either of these commands.  
```
os.getenv("LandregDataStorage")
os.environ["LandregDataStorage"]
```


# Install Python Major Versions
Your system Python version may not be the version you wish to use for building Azure Function Apps.  In this case, you can install a different (major) version as an alternative Python installation. 
Note: It is not recommended to try to install multiple minor versions within the same major version.  So if you have 3.8.10, this will appear as 3.8 and by further installing 3.8.15 will only overwrite the 3.8.10.  

## Pre-requisites
Ensure you have zlib in your system, as it is required to install pip.  You also will need to ensure open SSL is installed as pip uses this for TLS.
```
sudo apt-get install zlib1g-dev
sudo apt install libssl-dev
```

Now follow these steps to install a different python version, and be careful to use *make altinstall*. 
```
wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz  
tar xzf Python-3.8.0.tgz
cd Python-3.8.0
./configure
sudo make altinstall
```

Installing openssl should work ok, as the configure script does eventually find the "ssl.h" file. But if you want to remove all doubt you can specifically set it.
```
whereis openssl
export SSLLOC=/usr/include/openssl
```
Then before running the 'make' command, change the configure command to be explicit.
``` 
./configure --with-openssl=$SSLLOC
```

Note: If you have a fresh linux container you may also need to install gcc and make, etc.  
```
sudo apt-get install build-essentials
```

This alternative major python version (and any others) should now be visible in the /usr/local/bin.  

By using the altinstall make file, the process will not create symlinks and referencesj to the alternative version, so We should create an alias for this in our .bashrc file so we can use it by typing a simple 'py38' command.
```
alias py38='/usr/local/bin/python3.8'
```  
