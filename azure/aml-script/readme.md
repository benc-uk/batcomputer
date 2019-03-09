# Deploy Azure ML
This is a simple bash script to setup a new Azure ML Workspace

# Prereqs
- Azure CLI
- [WSL bash/zsh](https://docs.microsoft.com/en-us/windows/wsl/install-win10) prompt
  - If you don't use WSL then [Azure Cloud Shell](https://shell.azure.com) can be used

# Usage
- Edit deploy.sh and change
  - `workspaceName="CHANGEME"`
  - `resGroup="CHANGEME"`
  - `region="westeurope"`
- Run `./deploy.sh`

The script should output your container registry password and other values, you will need these for setting up the Azure ML scripts and Azure DevOps pipelines