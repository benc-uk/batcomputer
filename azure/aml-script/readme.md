# Deploy Azure ML
This is a simple bash script to setup a new Azure ML Workspace

If you don't fancy using this script, just [use the portal](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started#create-a-workspace), see if I care...

# Prereqs
- [Linux bash, e.g. WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-apt?view=azure-cli-latest)

If you don't use WSL and/or don't have the Azure CLI installed then [Azure Cloud Shell](https://shell.azure.com) can be used

⚠️ IMPORTANT [Install the 'CLI extension for Azure Machine Learning service'](https://docs.microsoft.com/en-us/azure/machine-learning/service/reference-azure-machine-learning-cli)


# Usage
- Edit deploy.sh and change
  - `workspaceName="CHANGEME"`
  - `resGroup="CHANGEME"`
  - `region="westeurope"`
- Run `./deploy.sh`

The script should output your container registry password and other values, you will need these for setting up the Azure ML scripts and Azure DevOps pipelines, e.g.

```
### Deployment complete!
### - Workspace name:                   demo
### - Workspace res group:              temp.batcomputer
### - Workspace sub id:                 2b144d4f-06b2-4174-8d77-0a8835fa6235
### - Container registry name:          demoacrakkuhcsx
### - Container registry password:      p4VLe4C/Iwcn=TdWF+TD+Ag0uk+KR14y
```

Make a note of these (copy and paste into a file)