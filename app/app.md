# Javascript Env
Install the webserver and js exection environment.  

```
sudo apt-get install nodejs
sudo apt-get install npm
OR
doas apk install nodejs
doas apk install npm
```
Install the Serve command.  
```
sudo npm install --global serve
OR
doas npm install --global serve
```
Now you can run a JS project in folder.  
```
cd folder_name/
npx serve
```