#!/bin/bash
export $(cat .env | xargs)

echo "Downloading model & pickles version $VERSION from: $AZURE_STORAGE_ACCOUNT/$BLOB_CONTAINER"
rm *.pkl
az storage blob download -c $BLOB_CONTAINER -n $VERSION/model.pkl -f model.pkl -o tsv
az storage blob download -c $BLOB_CONTAINER -n $VERSION/lookup.pkl -f lookup.pkl -o tsv
az storage blob download -c $BLOB_CONTAINER -n $VERSION/flags.pkl -f flags.pkl -o tsv
