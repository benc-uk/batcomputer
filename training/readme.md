# Scikit Learn Training Scripts

These are the training scripts that train and fit the model using Scikit Learn and Pandas

**⚡ Important!**  
These have been written by someone learning ML and trying it for the first time. It was not developed by a data scientist or someone with a background in AI. It does not represent any sort of best practice or exemplary way of training a model with Scikit/Python or analyzing the data. However it is functional, and the resulting models serves the purposes of this project adequately 

Scripts can be running locally without AML, but you will need to install the packages in `model-api/requirements.txt`

Both scripts write their results into the `./outputs/` directory in the form of three pickle (.pkl) files. When running under AML, the contents of the `./outputs/` directory is automatically uploaded to AML and stored alongside the run. For more information on the model, pickle files and this project's approach to metadata [please refer to the main docs](../#models-metadata-and-api-design)

## scikit-batcomputer.py
This trains the Batcomputer crime model
- Uses the training data from `data/batcomputer/crime.zip`. 
- Data is automatically unzipped and loaded into Pandas
- A RandomTree classifier is used, which is probably not the best choice
- If running locally, change the glob on line 45 to load a smaller subset of data otherwise on a quad core machine such as a SurfaceBook it can take around 20 minutes to run
- The model returns results indicating the **probability** of "getting caught" for given crime, this is deemed as going to prison, being fined, cautioned etc. This encoding of crime outcomes is done with a lambda function `mapOutcomesToProba` which returns 1 for "getting caught" and a zero otherwise

## scikit-titanic.py
This trains the Titanic "would someone survive" model
- Uses the training data from `data/titanic/titanic.csv`. 
- A RandomTree classifier is used, which seems to work OK
