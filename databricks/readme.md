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
databricks libraries install --cluster-id $CLUSTER_ID --pypi-package azureml-sdk[databricks]"
databricks libraries install --cluster-id $CLUSTER_ID --pypi-package scikit-learn==0.20.2
```

## Create jobs
REMOVE THIS SECTION FOR V2 AML EDITION!
 **IMPORTANT!** Before running, edit the JSON files and put the cluster id in the `existing_cluster_id` field
```
databricks jobs create --json-file databricks/job-train-batcomputer-model.json
databricks jobs create --json-file databricks/job-train-titanic-model.json
```

# Import Notebooks
REMOVE THIS SECTION FOR V2 AML EDITION!
Decide where you want to put the Notebooks and import them
```
databricks workspace import notebooks/scikit-batcomputer.py /Shared/scikit-batcomputer -l python -o
databricks workspace import notebooks/scikit-titanic.py /Shared/scikit-titanic -l python -o
```

# Create KeyVault Secret Scope
REMOVE THIS SECTION FOR V2 AML EDITION!
You will need details of both your Key Vault and storage key for this step
If you deployed everything using the `deploy.sh` script then please use the output of that script

Create a secret scope, and link it to the Key Vault you deployed or wish to use. This has to be done in the DataBricks web UI. See this guide https://docs.azuredatabricks.net/user-guide/secrets/secret-scopes.html

For the values to enter on that page, run this command:
```
az keyvault show --name <<VAULT_NAME>> --query "{resourceId:id, dnsName:properties.vaultUri}"
```
**Important!** You must name the secret scope **keyvault-secrets**

Lastly create a secret in your Key Vault called **storage-key**, and place your model registry storage account key as the value
```
az keyvault secret set --vault-name <<VAULT_NAME>> --name "storage-key" --value "<<STORAGE_KEY>>"
```