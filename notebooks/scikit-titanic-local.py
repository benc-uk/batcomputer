import os
import pandas as pd
import numpy as np
import pickle
from dotenv import load_dotenv
from azure.storage.blob import BlockBlobService
from sklearn.ensemble import RandomForestClassifier
from collections import OrderedDict

load_dotenv()

# Model version is passed into job, and storage key is kept in a secret
MODEL_VERSION = os.getenv("VERSION", "1.0.0")

STORAGE_KEY = os.getenv('AZURE_STORAGE_KEY')
STORAGE_ACCOUNT = "bcmisc"
STORAGE_CONTAINER = "titanic-ml"

# Load data from CSV
data = pd.read_csv('./data/train.csv')

# Drop rubbish columns
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

# Use RandomForestClassifier
model = RandomForestClassifier(n_estimators = 100)
model = model.fit(train_data[0:,2:], train_data[0:,0])
answer = model.predict_proba([[3, 42, 0, 0, 2, 1, 1]])
print(answer[0])

# Create pickles and data lookup 


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



# Create the BlockBlockService that is used to call the Blob service for the storage account
block_blob_service = BlockBlobService(account_name=STORAGE_ACCOUNT, account_key=STORAGE_KEY) 

# Create a container
block_blob_service.create_container(STORAGE_CONTAINER) 

# Upload the created file, use local_file_name for the blob name
block_blob_service.create_blob_from_path(STORAGE_CONTAINER, MODEL_VERSION + "/model.pkl", "model.pkl")
block_blob_service.create_blob_from_path(STORAGE_CONTAINER, MODEL_VERSION + "/lookup.pkl", "lookup.pkl")
block_blob_service.create_blob_from_path(STORAGE_CONTAINER, MODEL_VERSION + "/flags.pkl", "flags.pkl")