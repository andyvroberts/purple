# Setup Linux Dev Environment
WSL Debian with Python 3.11, dotnet, Azure CLI & Azure Functions core tools.

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

### Debian 12
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
sudo apt-get install sudo libssl-dev
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
Install by using the instructions [already linked](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=linux%2Cbash%2Cazure-cli&pivots=python-mode-decorators#install-the-azure-functions-core-tools) above.  Once installed, check you have the latest v4.  
Currently, after following the instructions this fails on Debian 12.  

As a workaround until the official Debian 12 package is released I was able to run the Debian 11 azure-functions-core-tools package on Debian 12.
to do so - manually replace:  
```
https://packages.microsoft.com/debian/12/prod bookworm main
```
with:
```
https://packages.microsoft.com/debian/11/prod bullseye main
```
in:
```
/etc/apt/sources.list.d/dotnetdev.list
```
and then 
```
run sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
func --version
```