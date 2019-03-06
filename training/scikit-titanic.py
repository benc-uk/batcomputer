import argparse, os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from azureml.core import Run
from collections import OrderedDict
import pickle

# let user feed in parameters, the location of the data files (from datastore)
parser = argparse.ArgumentParser()
parser.add_argument('--data-path', type=str, dest='data_path', help='data folder mounting point')
parser.add_argument('--estimators', type=int, dest='estimators', help='number of estimators')
args, unknown = parser.parse_known_args()

data_folder = args.data_path or "../data/titanic/"
n_estimators = args.estimators or 800

# Get the AML run
run = Run.get_context()

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

print("### Training and fitting the model...")

# Get our training data in NumPy format
all_data = data.values

# Shuffle data, and split into train and test 90% vs 10%
np.random.shuffle(all_data)
split_point = int(all_data.shape[0] / 1.1)
train = all_data[0:split_point]
test = all_data[split_point:]

# Use RandomForestClassifier
X = train[0:, 2:]
y = train[0:, 0]
clf = RandomForestClassifier(n_estimators = n_estimators)
model = clf.fit(X, y)

print("### Testing predictions on", test.shape[0], "samples...")
Xtest = test[0:, 2:]
ytest = test[0:, 0]
preds = model.predict(Xtest)
accuracy = accuracy_score(ytest, preds)
print("### Accuracy was:", accuracy)

run.log('accuracy', np.float(accuracy))
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
