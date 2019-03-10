# Source Data

## Titanic
The data for the Titanic training is very small so is included in the repo

## Batcomputer
The data used for training the Batcomputer model was obtained from https://data.police.uk/data/ and uses the "street" CSVs. The model is intended to predict the outcome of a given crime in a given region & month, the outcome being "caught" (convicted, fined, cautioned) or not


This data is too large to commit into Git, so the data has been zipped and put on Blob storage here: 

#### [https://bcmisc.blob.core.windows.net/shared/crime.zip](https://bcmisc.blob.core.windows.net/shared/crime.zip)

This is the data downloaded from the the above URL, for all forces, for all of 2017.  
There is no need to unzip the data, this is done by the training script

To quickly download to the correct location run:
```
wget --show-progress https://bcmisc.blob.core.windows.net/shared/crime.zip -O ./data/batcomputer/crime.zip
```

If manually downloading, `crime.zip` should be placed in the `data/batcomputer` folder