#!/bin/bash

# CHANGE THESE
resGroup="temp.batcomputer4"
region="westeurope"

# CHANGE THESE - Resource names and prefixes
databricksName="batcomputer"
modelRegPrefix="modelreg"
acrPrefix="modelimages"
keyVaultPrefix="keyvault"
suffix="$RANDOM"

# Don't change these
keyVaultName="$keyVaultPrefix$suffix"
acrName="$acrPrefix$suffix"
modelRegName="$modelRegPrefix$suffix"

echo "### Creating resource group $resGroup ..."
az group create -n $resGroup -l $region -o table

echo "### Creating DataBricks workspace ..."
az group deployment create -g $resGroup --template-file ../azure/databricks/azuredeploy.json --parameters workspaceName=$databricksName -o table

echo "### Creating Key Vault ..."
az keyvault create -n $keyVaultName --sku standard -g $resGroup -l $region -o table

echo "### Creating Storage account ..."
az storage account create -n $modelRegName -g $resGroup -l $region --sku Standard_LRS -o table
storeKey=`az storage account keys list -n $modelRegName -g $resGroup --query "[0].value" -o tsv`

echo "### Creating Container Registry ..."
az acr create -n $acrName -g $resGroup -l $region --sku Standard -o table --admin-enabled true
acrPassword=`az acr credential show -n $acrName -g $resGroup --query "passwords[0].value" -o tsv`

echo
echo "### Deployment complete!"
echo "### - Model registry storage key is: $storeKey"
echo "### - Model registry storage name is: $modelRegName"
echo "### - Key Vault name is: $keyVaultName"
echo "### - Container registry name is: $acrName"
echo "### - Container registry password is: $acrPassword"
echo
