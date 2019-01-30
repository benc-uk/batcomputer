# DataBricks Setup
This brief readme covers some of the steps & JSON configs in order to setup DataBricks for Batcomputer. A fully automated/scripted deployment is not provided at this stage (indeed if it is even possible)

## Pre-Requisites
You will need the DataBricks CLI (which in turn requires Python. https://docs.databricks.com/user-guide/dev-tools/databricks-cli.html  

In order to connect the CLI to your DataBricks instance, a PAT first needs to be created https://docs.databricks.com/api/latest/authentication.html#authentication


## Create cluster
This is a very simple one node cluster
```
databricks clusters create --json-file databricks/cluster.json
CLUSTER_ID=`databricks clusters list --output JSON | jq -r '.clusters[] | select (.cluster_name == "main-cluster").cluster_id'`
echo "Your cluster id: $CLUSTER_ID"
```

## Install Libraries
```
databricks libraries install --cluster-id $CLUSTER_ID --pypi-package azure-storage-blob
databricks libraries install --cluster-id $CLUSTER_ID --pypi-package scikit-learn==0.20.2
```

## Create jobs
 **IMPORTANT!** Before running, edit the JSON files and put the cluster id in the `existing_cluster_id` field
```
databricks clusters create --json-file databricks/job-train-batcomputer-model.json
databricks clusters create --json-file databricks/job-train-titanic-model.json
```

# Import Notebooks
Decide where you want to put the Notebooks and import them
```
databricks workspace import notebooks/scikit-batcomputer.py /Users/changeme/scikit-batcomputer -l python -o
databricks workspace import notebooks/scikit-titanic.py /Users/changeme/scikit-titanic -l python -o
```