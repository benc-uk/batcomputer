# Azure ML Orchestration Scripts
These scripts are at the heart of the Batcomputer project; driving the training & model generation, and tie closely to the operationalization process of building the model API

These are Python scripts that use the [Azure ML Python SDK](https://docs.microsoft.com/python/api/overview/azure/ml/intro) to run & drive several processes. They are described as 'orchestration' scripts in order to differentiate them from the Python scripts that perform the actual machine learning & training. 

Scripts have been developed in such a way they are re-usable and generic as possible, hence the high degree of parameterization. With a switch of a few variables a totally different model can be trained on different data

The scripts can be run locally, but they are intended to be run by Azure DevOps in a pipeline

## Pre-reqs
- You must have an Azure ML Workspace  
You can use the [provided script](../azure) to create one or use the Azure Portal
- Python 3.6

## Running / Testing Locally
- Follow the [Python Environment steps in the setup guide](../docs/setup#python-environment)
- Copy/rename the `.env.sample` file to `.env` and edit to match your setup, the only parts you MUST change are the first three settings. See below
- Simply run with `python <script-name>` some scripts take command line parameters, all scripts rely on environmental variables

# Environmental Variables
The scripts make heavy use of system environmental variables, this allows them to used in Azure DevOps pipelines where pipeline variables are automatically 