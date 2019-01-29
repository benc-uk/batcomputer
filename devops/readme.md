# DevOps CI/CD

## Prerequisites  
In essence you need a complete system with all aspects of the project environment

- Azure DevOps account and project
- GitHub repo
- Azure Container Registry
- Azure Key Vault
- Azure Storage Account
- DataBricks fully setup and configured with a cluster and jobs, see [the DataBricks setup docs](../databricks)

**⚡ Important!**  
Clone or fork this repo to your own GitHub account before proceeding

## Setup
Very high level basic setup tasks. Assuming the storage account for the model registry is already in place

- [Setup Azure Pipelines or Azure DevOps account](https://azure.microsoft.com/en-gb/services/devops/pipelines/)
- [Create Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/quick-create-portal)
- Populate Key Vault with secrets named:
  - `acr-password` - The admin password for the Azure Container Registry
  - `databricks-token` - PAT for accessing DataBricks with admin rights
  - `storage-key` - Storage account key for the model registry
- Create a variable group named **"shared-secrets"** and link it to the Key Vault, add the three secrets. Enable **Allow access to all pipelines**
- Create a variable group named **"shared-variables"**, wnable **Allow access to all pipelines** and create five variables:
  - `acr-name` - The name of the Azure Container Registry instance/account
  - `databricks-host` - The URL used to access DataBricks, e.g. `https://westeurope.azuredatabricks.net`
  - `storage-account` - Storage account name for the model registry
  - `version` - The version of model to be trained/built, e.g. `1.0.0`
- Add each of the build pipelines described in the next section:
  - New build pipeline
  - Select **Use the visual designer** 
  - Pick GitHub (Link Azure DevOps to your GitHub if not already)
  - Select your Batcomputer repo
  - Pick YAML as the template under 'Configuration as code'
  - Use the 'YAML file path' to select the relevant YAML file

## Azure Pipelines
```
pipelines/train-titanic-model.yaml
pipelines/train-batcomputer-model.yaml
pipelines/scikit-base-image.yaml
pipelines/build-titanic-image.yaml
pipelines/build-batcomputer-image.yaml
pipelines/templates/build-image.yaml
pipelines/templates/run-databricks-job.yaml
```