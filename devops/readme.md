# DevOps CI/CD
This section describes the CI process and pipelines and how they are setup and run from Azure DevOps 

Currently the CD part is "an exercise left to the reader" as there is no elegant way to share Azure Pipelines release definitions. 

However the [infrastructure as code templates are provided](../#infrastructure-as-code). The ARM template for deploying to ACI and the Kubernetes Helm chart for deploying to AKS are fairly trivial to setup in an Azure release Pipeline 

# Prerequisites  
You will need a complete system with all aspects of the project environment

- Azure DevOps account and project
- GitHub repo
- Azure Container Registry
- Azure Key Vault
- Azure Storage Account
- DataBricks fully setup and configured with a cluster and jobs, see [the DataBricks setup docs](../databricks)

**⚡ Important!**  
Clone or fork this repo to your own GitHub account before proceeding

---

# Azure DevOps Setup
Very high level setup tasks for putting the pipelines into Azure DevOps. These steps assuming everything else is in place

- [Setup Azure Pipelines or Azure DevOps account](https://azure.microsoft.com/en-gb/services/devops/pipelines/)
- Populate Key Vault with secrets [described below for shared-secrets](variable-groups) 
- Create a variable group named **"shared-secrets"** and link it to the Key Vault, add the three secrets. Enable **Allow access to all pipelines**
- Create a variable group named **"shared-variables"**, enable **Allow access to all pipelines** and create five variables [described below](variable-groups) 
- Add each of the build pipelines described in the next section:
  - New build pipeline
  - Select **Use the visual designer** 
  - Pick GitHub (Link Azure DevOps to your GitHub if not already)
  - Select your forked Batcomputer repo
  - Pick YAML as the template under 'Configuration as code'
  - Use the 'YAML file path' to select the relevant YAML file

---

# Azure Pipelines

## Variable Groups
The pipelines make use of a feature of Azure Pipelines called variable groups, these allow you to define and share a common set of variables across multiple pipelines

Two named variable groups are used used:
- `shared-variables` - Variables that are not secret. The variables in this group are:
  - `acr-name` - The name of the Azure Container Registry instance/account
  - `databricks-host` - The URL used to access DataBricks, e.g. `https://westeurope.azuredatabricks.net`
  - `storage-account` - Storage account name for the model registry
  - `version` - The version of model to be trained/built, e.g. `1.0.0`

- `shared-secrets` - Secret variables, keys passwords etc. Based with Azure Key Vault. The secret variables in this group are:
  - `acr-password` - The admin password for the Azure Container Registry
  - `databricks-token` - PAT for accessing DataBricks with admin rights
  - `storage-key` - Storage account key for the model registry

## Continuous Integration - Model Training 
Two pipelines are provided to train the models via CI
- pipelines/train-titanic-model.yaml
- pipelines/train-batcomputer-model.yaml

These pipelines carry out several tasks
1. Connect to DataBricks using the DataBricks CLI
2. Import Python file into DataBricks workspace as a Notebook
3. Trigger the job pointing at the Notebook to run it, and pass parameters to the Notebook

The pipeline YAML files define variables specific to that model & Notebook, the actual task steps are held in a template called `pipelines/templates/run-databricks-job.yaml` 

### Trigger
These pipelines are set to trigger on specific files, `notebooks/scikit-batcomputer.py` and `notebooks/scikit-titanic.py` so they only perform CI when those Notebooks are saved/synced from DataBricks and pushed to the git repo

## Continuous Integration - Build API Model App Container Image
Two pipelines are provided to train the models via CI
- pipelines/build-titanic-image.yaml
- pipelines/build-batcomputer-image.yaml

These pipelines carry out several tasks
1. Fetch and download the trained model from the model registry (Blob storage)
2. Run the Docker build for the `model-api/Dockerfile`
3. Tag the image for ACR and with the model version 
4. Push the image up to ACR

The pipeline YAML files define variables specific to that image, the actual task steps are held in a template called `pipelines/templates/build-image.yaml` 

### Trigger
These pipelines are set not to trigger on anything, and currently they are run manually
