# Dotnet & Azure Installs
To prepare our linux environment, we will install and/or configure the following:
1. Dotnet SDK (latest) and dotnet 3.1 LTS (for function apps)
2. Azure CLI
3. Azure Functions Core Tools


## 1. Dotnet
See the main doc pages to make sure instructions are current.  Add the microsoft package references to apt so the install will work.   
  
https://docs.microsoft.com/en-us/dotnet/core/install/linux

For Debian, first add the MS package signing key.
```
wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
```
Then run the install
```
sudo apt-get update 
sudo apt-get install -y dotnet-sdk-6.0
```

### Dotnet 3.1 (LTS)
At this time (October 2022), Azure function core tools still requires the dotnet core 3.1 SDK.  So we must also install this version.
```
sudo apt-get install -y dotnet-sdk-3.1
```

### Using Multiple Dotnet Versions
In case you need to use more than one dotnet version, you can create a global.json file at your project root folder.  Any dotnet commands will use the version you specified in global.json.  
https://docs.microsoft.com/en-us/dotnet/core/tools/global-json?tabs=netcore3x

To generate a global.json file for 3.1, placed in the root of the specific project.  
```
dotnet new globaljson --sdk-version 3.1
```

If you need to know what versions you have installed, list the sdk's.
```
dotnet --list-sdks
```
See all the dotnet new commands in the reference.  
https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-new


## 2. Azure CLI
As always, read the docs first.  
https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt

Download and the run the Debian single command script.
```
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```
Note: It is possible to install the CLi using PIP.  However, I have had issues with some CLI commands using this approach.  I recommend only using the Debian install script.  

Then test it exists and logon using your account.  
Note: If you have MFA on your Azure account, you should login with your tenant id. First create an env variable "export mytenant=<your_id>"  
```
az --version
az login --tenant $mytenant
az account show
```


## 3. Azure Function Core Tools
You require this in order to create function app scaffolds, run an azure function locally, and to publish a function app to your Azure subscription.

https://github.com/Azure/azure-functions-core-tools

Setup Azure Functions core tools if not installed:  
https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash

Keep track of the runtime versions and their compatibilities.  
https://docs.microsoft.com/en-us/azure/azure-functions/functions-versions

The MS docs currently say this is only valid for Debian 9 or 10, but it also works for version 11.  To prepare for installation:
```
# set to 9 or 10 in the docs.microsoft pages!
DEBIAN_VERSION=11
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.asc.gpg
sudo mv microsoft.asc.gpg /etc/apt/trusted.gpg.d/
wget -q https://packages.microsoft.com/config/debian/$DEBIAN_VERSION/prod.list
sudo mv prod.list /etc/apt/sources.list.d/microsoft-prod.list
sudo chown root:root /etc/apt/trusted.gpg.d/microsoft.asc.gpg
sudo chown root:root /etc/apt/sources.list.d/microsoft-prod.list
```

To install core tools and then test what version exists.
```
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
func --version
```
