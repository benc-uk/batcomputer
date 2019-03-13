# Batcomputer - End to End Setup

If you wish to setup this project in your own Azure subscription, this guide provides of the steps to do so.  

**⚡ Important!**  
You MUST fork the [main repo](https://github.com/benc-uk/batcomputer) to your own GitHub account before proceeding, and then clone it if you want to work with it locally. For the DevOps Pipelines this is a requirement as webhooks and other git configuration is required

Alternatively you can [import this repo](https://docs.microsoft.com/en-gb/azure/devops/repos/git/import-git-repository?view=azure-devops) into an private Azure Repo, you need an Azure DevOps project first. See the steps below

## Prereqs
- Python 3.6 
  - Earlier versions of Python can **NOT** be used
  - Python for Windows or the Python that comes with WSL can be used
- Azure Subscription
- Azure DevOps Account, you can [create a new free account here](https://azure.microsoft.com/en-gb/services/devops/)

**💬 Note.** You can jump straight to the [Azure DevOps part](#setup-azure-devops) if you don't want to try to testing/running locally. This skips any requirement for Python 


# Python Environment
It's strongly advised to use a Python [virtual environment](https://docs.python.org/3.6/tutorial/venv.html), but it is not mandatory. If you are comfortable with using Python or have an existing virtual environment setup that you use, then that can used instead.

To create a virtual environment and install Python packages/modules  

From root of batcomputer project directory
- `python -m venv pyenv` (**Note** If using WSL, run `python3 -m venv pyenv`)
- `source pyenv/bin/activate` (Linux/WSL)  
  OR
- `.\pyenv\Scripts\activate` (Windows)
- `pip install -r aml/requirements.txt`
- `pip install -r model-api/requirements.txt`


# Azure Setup
The only resource required in Azure is an 'Azure Machine Learning workspace', to create one of these, there are several options:

- A [📃 Deployment Script](../azure/aml-script) is provided as a convenience
- [The Azure Portal](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started#create-a-workspace)
- Azure CLI

When you create a new workspace, it automatically creates several other Azure resources, namely: Azure Container Registry, Azure storage account, Azure Application Insights and Azure Key Vault

When deployment is complete, make a note of the following things they will be needed later:

- **Azure ML workspace name**
- **Resource group** containing the workspace
- **Subscription ID**
- **Container Registry name**. Find this in the same resource group your deployed the workspace to, it will have an auto generated number prefix
- **Container Registry password**. If you deployed using the provided script this will have been shown to you. If you didn't, then find it via the portal, it's under the 'Access keys' blade


# Prepare Data
Assuming you are training the Batcomputer model you will need to download the source/training data. For the Titanic model, data is included in the Git repo

#### [📃 Source Data Prep](../data)


# Locally Test Azure ML Orchestration Scripts
Detailed documentation for this section is found in the docs for the 'Azure ML Orchestration Scripts'

#### [📃 Azure ML Orchestration Scripts - Docs](../aml)



In summary, the steps are:
- Create `.env` file and populate/update variables as described in the above guide
- Remember to have the Python virtual environment enabled/activated
- Work from the `aml/` directory
- Run `python upload-data.py --data-dir ../data/batcomputer`  
  - This may take several minutes as 250Mb is uploaded
- Run `python run-training.py`
  - **NOTE.** This will take about 10-15 minutes the first time you run it, as it creates a new cluster and builds Docker images for use with it, as well as the actual training. See notes below on ["What happens in AML?"](#what-happens-in-azure-ml)
- Run `python fetch-model.py`

These steps are for having the Batcomputer model as the training target, for the Titanic model modify the values in the `.env` file and change the `--data-dir` path

# Locally Test Model API
Detailed documentation for this section is found in the docs for the 'model API'

#### [📃 Model API - Docs](../model-api)

In summary, the steps are:
- Remember to have the Python virtual environment enabled/activated
- Ensure that training and `python fetch-model.py` from the above section has run
- Work from the `model-api/` directory
- Run `python src/server`
- Test and try out the model, see [📃 Using The Model](#using-the-model) below

---

# Setup Azure DevOps
This part requires you to sign up to Azure DevOps (which is free) and create an organization and a project

- [Sign up for Azure DevOps](https://docs.microsoft.com/en-gb/azure/devops/user-guide/sign-up-invite-teammates?view=azure-devops)
- [Create a Project](https://docs.microsoft.com/en-gb/azure/devops/organizations/projects/create-project)

### Enable Preview Features
The pipeline creation steps follow the new YAML pipeline creation flow, this is a preview feature (as of March 2019) so will need to be enabled:
- Click your account icon in top right
- Click 'Preview features'
- Enabled the 'New YAML pipeline creation experience' setting

### Connect to Azure
Create a service connection so that Azure DevOps can work with the Azure subscription:
- Click 'Project settings' in lower left
- Click on 'Pipelines / Service connections'
- Create new service connection:
  - Type: 'Azure Resource Manager'
  - Name the connection anything, e.g. `azure-connection`
  - Select the Azure subscription you are using
  - Leave 'Allow all pipelines to use this connection' ticked
  - You will be prompted to login/authenticate

**💬 Note.** This creates a service principal in Azure, make sure you are using an subscription & tenant where you have rights to create service principals

### Create Variable Group
Create a variable group which will be used a shared by all pipelines

- [Create a variable group](https://docs.microsoft.com/en-gb/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=yaml)
- Name the group `shared-variables`
- Enable "Allow access to all pipelines"
- Populate with the following variables, these are described in the [📃 AML scripts doc](../aml/#environmental-variables)

```
AZML_WORKSPACE
AZML_SUBID
AZML_RESGRP
AZML_COMPUTE_MIN_NODES
AZML_COMPUTE_MAX_NODES
AZML_COMPUTE_VMSIZE
AZML_COMPUTE_NAME
ACR_NAME
ACR_PASSWORD
AZURE_SVC_CONNECTION
```

**💬 Note 1.** Most of the values can be copied from your `aml/.env` file

**💬 Note 2.** `ACR_NAME` & `ACR_PASSWORD` will be from your original deployment of the AML workspace. The `ACR_NAME` **must not** include the `.azurecr.io` suffix

# DevOps Build Pipelines
Three pipelines need to be created, the process is the same for all three:

- Go into: Pipelines ➔ Build, Click 'New Pipeline'
- "Where is your code?", pick GitHub
  - First time you will need to authorize access to GitHub, so sign into GitHub
- Browse/locate your own fork of the batcomputer repo
- Select 'Existing Azure Pipelines YAML file'
  - Pick `/pipelines/batcomputer-data-load.yml`
- The YAML should be displayed, do not modify it
- Click 'Run'
- Rename the pipeline `Batcomputer Load Data` (You can rename the pipeline while it is running)

Repeat the process for:
- `/pipelines/batcomputer-training.yml`, renaming the pipeline `Batcomputer Run Training`. This might take some time to run, see notes below on ["What happens in AML?"](#what-happens-in-azure-ml)
- `/pipelines/batcomputer-build-api.yml`, renaming the pipeline `Batcomputer Build API`

**💬 Note.** There is no reason to run the "Load Data" pipeline more than once. It's included as a repeatable pipeline for completeness 

After the pipelines are created & run once, they should automatically trigger based on code pushes to the repo

# DevOps Release Pipelines
As of March 2019 YAML release pipelines are not available in Azure DevOps making it borderline impossible to share a re-usable pipeline for release/deployment

***This section is on hold until this feature becomes available, until then using the supplied Helm chart and ARM template you can create your own pipeline without too much effort***

- [📃 ARM Template - Docs](../azure/aci-arm-template)
- [📃 Helm Chart - Docs](../kubernetes/helm)

## Manually Deploying the API
In order to manually deploy the API from the built Docker image, you can create an Azure Container Instance quite easily

These steps use the Azure CLI and Bash, for this you can use the [Azure Cloud Shell](https://shell.azure.com), select 'Bash' when prompted. The Azure Portal is another choice for doing this

Then [Install the Azure ML CLI extension](https://docs.microsoft.com/en-us/azure/machine-learning/service/reference-azure-machine-learning-cli#install-the-extension)

Change these three variables to match your setup of Azure ML and the model version you want to deploy. Copy and paste this snippet into a text file, modify then copy & paste into the Cloud Shell bash session, use the up arrow to correct any mistakes
```
resGrp=MY_AML_RESGRP
workspace=MY_AML_NAME
modelVer=1
```

Then copy and paste this whole snippet into the bash session
```
ACR_ID=$(az ml workspace show -n $workspace -g $resGrp --query "containerRegistry" -o tsv)
ACR_NAME=$(az resource show --id $ACR_ID --query "name" -o tsv)
ACR_PASSWORD=$(az acr credential show -n $ACR_NAME -g $resGrp --query "passwords[0].value" -o tsv)

az container create \
  --name batcomputer-api \
  --resource-group $resGrp \
  --image $ACR_NAME.azurecr.io/batcomputer-model-api:$modelVer \
  --registry-username $ACR_NAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label batcomputer-api-$RANDOM \
  --port 8000 \
  --query "join('', ['http://', ipAddress.fqdn, ':8000/api'])" -o tsv 
```

When the deployment is complete (should take about a minute), the URL to the deployed API will be output, which you can copy and use later

Open the URL in the browser, if you see a 'Not Found' error page that means deployment was successful. 

Test and try out the model, see [📃 Using The Model](#using-the-model) below

# What Happens in Azure ML?
When running the training process you might want to observe what happens in AML, either during or after the run

Use the [Azure Portal](https://portal.azure.com) and navigate to your AML Workspace:
- Under **Compute** you should see a single target called "aml-cluster" and the number of nodes. It might be resizing and scaling up (e.g. from 0 -> 1) or running with 1 or more nodes (most likely 1)
  - The first time the cluster is used, a Docker image is created with all of the Python packages, this is done automatically but it does take time so expect a 10 minute delay in addition to the training on first run
  - The cluster will resize down to 0 nodes after an hour, which means no costs are being incurred, it will automatically scale back up when needed, but this scalling also adds some additional delay
- Under **Experiments** you should see the name of the experiment, e.g. "batcomputer"
  - Under the experiment you can see a summary & history of all the runs
  - Clicking into a run you can access logs and other details
  - For completed runs, various metrics are displayed including model accuracy, number of rows of training data, as well as some graphs
  - Outputs of the run in the form of the three .pkl files will be available
- Under **Models** you should see the model names e.g. "batcomputer-model" and all of the versions that have been created


# Using The Model
There are a few ways to test and use the Batcomputer model

The api-host might be `localhost` if testing locally or a FQDN if you deployed the API using Azure Container Instances

- Open a browser and access: `http://{{api-host}}:8000/api/info` various information and model metadata should be shown
- Open the [📃 Batcomputer Client](../batclient) and test using the model with a recreation of the 1960s Batcomputer. You need to provide the URL to your API when you first open the client page
- For further testing use [Postman](https://www.getpostman.com/) and the provided [📃 Postman Collection](../tests)
- Make a basic cURL request to get a prediction
  ```
  curl http://{{api-host}}:8000/api/predict -d '{"force":"Surrey Police", "crime": "Drugs", "month": 7}'
  ```