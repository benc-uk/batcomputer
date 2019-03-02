import argparse, os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from azureml.core import Run
from collections import OrderedDict
import pickle

# let user feed in parameters, the location of the data files (from datastore)
parser = argparse.ArgumentParser()
parser.add_argument('--data-path', type=str, dest='data_path', help='data folder mounting point')
parser.add_argument('--estimators', type=int, dest='estimators', help='number of estimators')
args = parser.parse_args()

data_folder = args.data_path
n_estimators = args.estimators

# Load data from CSV
data = pd.read_csv(f"{data_folder}/titanic.csv")

# Drop rubbish columns we don't need
try:
    data = data.drop(['Name', 'Ticket', 'Cabin'], axis=1)
    data = data.dropna()
except:
    pass

# Encode columns manually 
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

# Get our training data in NumPy format
train_data = data.values

# Use RandomForestClassifier
clf = RandomForestClassifier(n_estimators = n_estimators)
model = clf.fit(train_data[0:,2:], train_data[0:,0])

# Find prediction accuracy for:
# 16,1,2,"Hewlett, Mrs. (Mary D Kingcome) ",female,55,0,0,248706,16,,S
answer = model.predict_proba([[2, 55, 0, 0, 16, 0, 2]])
# get hold of the current run and log data
run = Run.get_context()
run.log('accuracy', np.float(answer[0][1]))
run.log('estimators', np.float(n_estimators))

# Done! Now upload results as pickles

# note file saved in the outputs folder is automatically uploaded into experiment record
os.makedirs('outputs', exist_ok=True)

# SAVE THE MODEL!
with open("outputs/model.pkl" , 'wb') as file:  
    pickle.dump(model, file)
    file.close()

# Metadata: lookup & flags
lookup = OrderedDict()
lookup["Pclass"] = 0
lookup["Age"] = 0
lookup["SibSp"] = 0
lookup["Parch"] = 0
lookup["Fare"] = 0
lookup["Gender"] = {"male": 1, "female": 0}
lookup["Port"] = {"Cherbourg": 1, "Southampton": 2, "Queenstown": 3}
flags = ["died_proba", "survived_proba"]

with open("outputs/lookup.pkl" , 'wb') as file:  
    pickle.dump(lookup, file)
    file.close()
    
with open("outputs/flags.pkl" , 'wb') as file:  
    pickle.dump(flags, file)
    file.close()
