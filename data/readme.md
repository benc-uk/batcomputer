# Source Data

The data used for training the Batcomputer model was obtained from https://data.police.uk/data/  
The 'street' CSV data was used, and imported into a table using the 'dataload-batcomputer' Notebook

The data used for training the Batcomputer model was obtained from https://data.police.uk/data/ and uses the "street" CSVs. The model is intended to predict the outcome of a given crime in a given region & month, the outcome being "caught" (convicted, fined, cautioned) or not

The specific CSVs used for training which is data for all forces for all of 2017, can be found here:
https://bcmisc.blob.core.windows.net/shared/crime.zip

It should be placed in the `data/batcomputer` folder