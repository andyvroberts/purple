# Azure Storage Queue
## CLI Commands
1. List Queues
2. Delete a Queue

### 1. List
List all storage queues in the storage account.
```
export storeacc=uklandregappdata
export prefix=landreg

az storage queue list --prefix $prefix --account-name $storeacc
```
To capture just the names in a file
```
az storage queue list --prefix $prefix --account-name $storeacc --query "[].name" -o tsv > qlist.txt
```

### 2. Delete
Delete a single named queue.
```
export name=landreg-b5

az storage queue delete -n $name --fail-not-exist --account-name $storeacc
```
Combine a list and delete using linux bash xargs command.
```
az storage queue list --prefix $prefix --account-name $storeacc --query "[].name" -o tsv | xargs -L1 -P10 -I{} az storage queue delete --fail-not-exist --account-name $storeacc -n {}
```

