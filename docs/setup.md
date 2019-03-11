# Batcomputer - End to End Setup

If you wish to setup this project in your own Azure subscription, this provides (most? all?) of the steps to do so.  

**⚡ Important!**  
You MUST fork this repo to your own GitHub account before proceeding, and then clone it if you want to work with it locally. For the DevOps Pipelines this is a requirement as webhooks and other git configuration is required

## Prereqs
- Python 3.6 
  - Earlier versions of Python can **NOT** be used
  - Python for Windows or the Python that comes with WSL can be used
- Azure Subscription
- Azure DevOps Account, you can [create a new free account here](https://azure.microsoft.com/en-gb/services/devops/)


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

- A [Deployment Script](../azure/aml-script) is provided as a convenience
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

#### [Source Data Prep](../data)


# Locally Test Azure ML Orchestration Scripts
Detailed documentation for this section is found in the docs for the 'Azure ML Orchestration Scripts'

#### [Azure ML Orchestration Scripts - Docs](../aml)

We assume the Batcomputer model is the training target, for the Titanic model modify the `.env` file and change the `--data-dir` path

In summary, the steps are:
- Create `.env` file and populate/update variables as described in the above guide
- Remember to have the Python virtual environment enabled/activated
- Work from the `aml/` directory
- Run `python upload-data.py --data-dir ../data/batcomputer`  
  - This make take several minutes as 250Mb is uploaded
- Run `python run-training.py`
  - **NOTE.** This will take about 10-15 minutes the first time you run it, as it creates a new cluster and builds Docker images for use with it, as well as the actual training.
- Run `python fetch-model.py`
 

# Locally Test Model API
Detailed documentation for this section is found in the docs for the 'model API'

#### [Model API - Docs](../model-api)

In summary, the steps are:
- Remember to have the Python virtual environment enabled/activated
- Ensure that training and `python fetch-model.py` from the above section has run
- Work from the `model-api/` directory
- Run `python src/server`
- Open a browser and access: `http://localhost:8000/api/info`
- Open the [Batcomputer client](../batclient) and test using the model from a Real Working Batcomputer!
- For further testing use [Postman](https://www.getpostman.com/) and the provided [Postman Collection](../tests)


# Setup Azure DevOps

!TODO!