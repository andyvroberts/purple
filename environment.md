# Setup Linux Dev Environment
WSL Debian with Python 3.11, dotnet 8.0, Azure CLI & Azure Functions core tools v4.

## WSL 
From an elevated powershell prompt do one or the other:  
```
wsl --install
wsl --update
```
To set WSL2 and check the version: 
```
wsl --set-default-version 2
wsl --version
```

### Debian 12 WSL
Download Debian from the Microsoft Store and start it up for the first time.  

Setup tools and environment. 
```
sudo apt update
sudo apt upgrade
sudo apt-get install wget
sudo apt-get install git
sudo apt install openssh-client
```
Create a deb-src source repository.
```
cd /etc/apt
sudo vi sources.list
```
Add this line for Deb12:
```
deb-src http://deb.debian.org/debian bookworm main
```
Next, install all Python build dependancies.
```
sudo apt-get build-dep python3
sudo apt-get install pkg-config
sudo apt-get install libssl-dev
sudo apt-get install build-essential
sudo apt-get install libffi-dev
```

Then install **Python** by first downlading the 3.11 tar from the pyhon.org [website](https://www.python.org/downloads/release/python-3118/) into a downloads (or any other) folder.

```
tar -xvf Python-3.11.8.tgz
cd Python-3.11.8
```
Run configure, make and install.
```
./configure --enable-optimizations
sudo make
sudo make install
**or**
sudo make altinstall
```
make install will place python in /usr/local/lib which will overwrite the default Python version.  
make altinstall will palce python in your custom location


## Dotnet
https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian  

For Debian, first add the MS package signing key.
```
wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
```
Then run the install
```
sudo apt-get update  
sudo apt-get install -y dotnet-sdk-8.0
```


## Azure CLI
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

## Azure Functions Core Tools v4
Install by using [these instructions](https://github.com/Azure/azure-functions-core-tools) above.  Once installed, check you have the latest v4.   

For Debian on WSL or Chromeos:
```
export DEBIAN_VERSION=12

sudo apt-get update 
sudo apt-get install gpg 
sudo apt-get install wget

sudo wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft-prod.gpg
sudo chown root:root microsoft-prod.gpg
sudo mv microsoft-prod.gpg /usr/share/keyrings/microsoft-prod.gpg

wget -q https://packages.microsoft.com/config/debian/$DEBIAN_VERSION/prod.list

sudo mv prod.list /etc/apt/sources.list.d/microsoft-prod.list

sudo chown root:root /usr/share/keyrings/microsoft-prod.gpg

sudo chown root:root /etc/apt/sources.list.d/microsoft-prod.list

sudo apt-get update 
sudo apt-get install azure-functions-core-tools-4  -y

sudo apt-get update 
sudo apt-get install libicu-dev  -y
```


### C# Setup
To develop C# Functions locally using the Functions Core Tools, see this doc page:  https://learn.microsoft.com/en-gb/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-csharp  

Create the project scaffold.  [At this time](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core#lifecycle), dotnet-isolated is .net 8.0    
```
func init MyProjFolder --worker-runtime dotnet-isolated
```

For creating a Queue Trigger function, read this doc page:  https://learn.microsoft.com/en-gb/azure/azure-functions/functions-bindings-storage-queue-trigger?tabs=python-v2%2Cisolated-process%2Cnodejs-v4%2Cextensionv5&pivots=programming-language-csharp  

To see all the possible templates for functions across all languages (runtimes) use the list command
```
func templates list
```

To create a storage queue trigger, navigate into our project folder and then add the function.
```
cd PurpleIngest
func new --template "QueueTrigger" --name PostcodePrices
```

The queue trigger template will add the nuget packages for you, however you will need to add other packages yourself.  For example this installs the latest and correct table storage namespace in your project:  
```

dotnet add package Microsoft.Azure.Functions.Worker.Extensions.Tables --version 1.3.0
```

