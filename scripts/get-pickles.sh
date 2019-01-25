#!/bin/bash
export $(cat .env | xargs)

echo "Downloading model & pickles version $VERSION from: $AZURE_STORAGE_ACCOUNT/$BLOB_CONTAINER"
rm pickles/*.pkl
mkdir -p pickles
az storage blob download -c $BLOB_CONTAINER -n $VERSION/model.pkl -f pickles/model.pkl -o tsv
az storage blob download -c $BLOB_CONTAINER -n $VERSION/lookup.pkl -f pickles/lookup.pkl -o tsv
az storage blob download -c $BLOB_CONTAINER -n $VERSION/flags.pkl -f pickles/flags.pkl -o tsv
