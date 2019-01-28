# Databricks notebook source
# MAGIC %md ## Pandas - Extracting data

# COMMAND ----------

import pandas as pd
import numpy as np

# Load data from CSV
data = pd.read_csv('/dbfs/FileStore/tables/titanic.csv')

# COMMAND ----------

# MAGIC %md   ## Pandas - Cleaning data

# COMMAND ----------

# Drop rubbish columns we don't need
try:
    data = data.drop(['Name', 'Ticket', 'Cabin'], axis=1)
except:
    pass

# Drop any rows that have nulls/na/blanks
data = data.dropna()

# Create numerical columns 
try:
    data['Gender'] = data['Sex'].map({'female': 0, 'male':1}).astype(int)
    data['Port'] = data['Embarked'].map({'C':1, 'S':2, 'Q':3}).astype(int)
    data = data.drop(['Sex', 'Embarked'], axis=1)
except:
    pass

# Move survived column first as it's our outcome
cols = data.columns.tolist()
cols = [cols[1]] + cols[0:1] + cols[2:]
data = data[cols]

# Column info
data.info()

# Get our training data in NumPy format
train_data = data.values

# COMMAND ----------

# MAGIC %md ## Scikit-learn - Training the model

# COMMAND ----------

from sklearn.ensemble import RandomForestClassifier

# Use RandomForestClassifier
model = RandomForestClassifier(n_estimators = 100)
model = model.fit(train_data[0:,2:], train_data[0:,0])

# COMMAND ----------

# MAGIC %md ## Test

# COMMAND ----------

answer = model.predict_proba([[3, 42, 0, 0, 2, 1, 1]])

print(answer[0])

# COMMAND ----------

# MAGIC %md ## Pickle model and store in Azure storage

# COMMAND ----------

#
# Widgets are how we get values passed from a DataBricks job
#
try:
  #dbutils.widgets.text("model_version", "1.0.0")
  #dbutils.widgets.text("storage_account", "modelreg")
  #dbutils.widgets.text("model_name", "batcomputer")

  # Model version, name & storage-account is passed into job, and storage key is kept in Azure Key Vault
  STORAGE_KEY       = dbutils.secrets.get("ai-deploy-secrets", "storage-key")
  STORAGE_ACCOUNT   = dbutils.widgets.get("storage_account")
  MODEL_VERSION     = dbutils.widgets.get("model_version")
  STORAGE_CONTAINER = dbutils.widgets.get("model_name")
except:
    pass
    
#
# STORAGE_ACCOUNT value should only be set when this Notebook is invoked via a job
# So we only pickle and store in Azure blobs when running as a job
#
if 'STORAGE_ACCOUNT' in vars():
  print("Saving pickles to:", STORAGE_ACCOUNT, " / ", STORAGE_CONTAINER)
  
  # Create pickles and data lookup 
  from collections import OrderedDict
  import pickle

  lookup = OrderedDict()

  # ORDER IS IMPORTANT! This is why we use OrderedDict and create entries one by one
  lookup["Pclass"] = 0
  lookup["Age"] = 0
  lookup["SibSp"] = 0
  lookup["Parch"] = 0
  lookup["Fare"] = 0
  lookup["Gender"] = {"male": 1, "female": 0}
  lookup["Port"] = {"Cherbourg": 1, "Southampton": 2, "Queenstown": 3}

  # Create output lookup
  flags = ["died_proba", "survived_proba"]

  # Pickle the whole damn lot
  with open("model.pkl" , 'wb') as file:  
    pickle.dump(model, file)
    file.close()

  with open("lookup.pkl" , 'wb') as file:  
    pickle.dump(lookup, file)
    file.close()

  with open("flags.pkl" , 'wb') as file:  
    pickle.dump(flags, file)    
    file.close()

  from azure.storage.blob import BlockBlobService

  # Create the BlockBlockService that is used to call the Blob service for the storage account
  block_blob_service = BlockBlobService(account_name=STORAGE_ACCOUNT, account_key=STORAGE_KEY) 

  # Create a container
  block_blob_service.create_container(STORAGE_CONTAINER) 

  # Upload the created file, use local_file_name for the blob name
  block_blob_service.create_blob_from_path(STORAGE_CONTAINER, MODEL_VERSION + "/model.pkl", "model.pkl")
  block_blob_service.create_blob_from_path(STORAGE_CONTAINER, MODEL_VERSION + "/lookup.pkl", "lookup.pkl")
  block_blob_service.create_blob_from_path(STORAGE_CONTAINER, MODEL_VERSION + "/flags.pkl", "flags.pkl")
  
  # Job complete
  dbutils.notebook.exit("Version: " + MODEL_VERSION + " pickled model and lookups stored in " + STORAGE_ACCOUNT + "/" + STORAGE_CONTAINER+"/"+MODEL_VERSION)
