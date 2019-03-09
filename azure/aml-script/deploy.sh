#!/bin/bash

# CHANGE THESE!
workspaceName="fred2"
resGroup="temp.fred"
region="westeurope"

echo "### Creating resource group $resGroup ..."
az group create -n $resGroup -l $region -o table

echo "### Creating Azure ML workspace ..."
az ml workspace create --name $workspaceName -l $region -g $resGroup

# Stuff to get the ACR password
acrId=$(az ml workspace show -n $workspaceName -g $resGroup --query "containerRegistry" -o tsv)
subId=$(az account show --query "id" -o tsv)
acrName=$(az resource show --id $acrId --query "name" -o tsv)
acrPwd=$(az acr credential show -n $acrName -g $resGroup --query "passwords[0].value" -o tsv)

echo
echo "### Deployment complete!"
echo -e "### - Workspace name: \t\t\t$workspaceName"
echo -e "### - Workspace res group: \t\t$resGroup"
echo -e "### - Workspace sub id: \t\t$subId"
echo -e "### - Container registry name: \t\t$acrName"
echo -e "### - Container registry password: \t$acrPwd"
echo
