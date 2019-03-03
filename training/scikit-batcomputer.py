import argparse, os, glob, pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from azureml.core import Run
from collections import OrderedDict

# =============================================================
# Input args
# =============================================================

# let user feed in parameters, the location of the data files (from datastore)
parser = argparse.ArgumentParser()
parser.add_argument('--data-path', type=str, dest='data_path', help='data folder mounting point')
parser.add_argument('--estimators', type=int, dest='estimators', help='number of estimators')
args, unknown = parser.parse_known_args()

data_folder = args.data_path or "../data/batcomputer/"
n_estimators = args.estimators or 100

# Get the AML run
run = Run.get_context()

# =============================================================
# Data loading and inital prep & clean up
# =============================================================

import zipfile
print("### Unzipping CSV data...")
zip_ref = zipfile.ZipFile(data_folder + "/crime.zip", 'r')
zip_ref.extractall(data_folder)
zip_ref.close()

# Load data from CSVs
print("### Loading CSV data...")
allFiles = glob.glob(data_folder + "/2017-*/*.csv")
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
data = pd.concat(list_, axis = 0, ignore_index = True)

# Drop rubbish columns we don't need
data = data.drop(['Falls within', 'Latitude', 'Longitude', 'Context', 'Location', 'LSOA code', 'LSOA name', 'Crime ID'], axis=1)
data = data.dropna()

print("### Working with training set of", data.shape[0], "rows")
run.log("training_rows", data.shape[0], description='Number of rows of training data')

# =============================================================
# Data encoding 
# =============================================================

print("### Data encoding...")

outcome_encoder = LabelEncoder()
data['Outcome_e']= outcome_encoder.fit(data['Last outcome category']).transform(data['Last outcome category'])
#print({outcome: oi for oi, outcome in enumerate(outcome_encoder.classes_)})

# This is a manual mapping but critical to training
def mapOutcomesToProba(x):
  return 1 if x in [23, 21, 20, 19, 18, 17, 12, 13, 11, 10] else 0
data["y"] = data["Outcome_e"].map(mapOutcomesToProba)

reported_by_encoder = LabelEncoder()
data['ReportedBy_e'] = reported_by_encoder.fit(data['Reported by']).transform(data['Reported by'])
crime_encoder = LabelEncoder()
data['Crime_e'] = crime_encoder.fit(data['Crime type']).transform(data['Crime type'])

def mapMonth(m):
  return int(m[-2:])
data["Month_e"] = data["Month"].map(mapMonth)

#print(data.head(100))

# =============================================================
# Training and fitting the model
# =============================================================

print("### Training and fitting the model...")

# Get our training data in NumPy format
all_data = np.array(data[["y", "ReportedBy_e", "Crime_e", "Month_e"]])

# Shuffle data, and split into train and test 90% vs 10%
np.random.shuffle(all_data)
split_point = int(all_data.shape[0] / 1.1)
train = all_data[0:split_point]
test = all_data[split_point:]

print("#### Done shuffling, now fitting...")
classifier = RandomForestClassifier(n_estimators = n_estimators)
X = train[0:, 1:]
y = train[0:, 0]
model = classifier.fit(X, y)

print("#### Testing predictions on", test.shape[0], "samples...")
Xtest = test[0:, 1:]
ytest = test[0:, 0]
preds = model.predict(Xtest)
accuracy = accuracy_score(ytest, preds)
print("#### Accuracy was:", accuracy)

# =============================================================
# Testing & checking
# =============================================================

#print({force: fi for fi, force in enumerate(reported_by_encoder.classes_)})
#print({crime: ci for ci, crime in enumerate(crime_encoder.classes_)})

#crime = 3
month = 7
for ci, crime in enumerate(crime_encoder.classes_):
  for fi, force in enumerate(reported_by_encoder.classes_):
    ans = model.predict_proba([[fi, ci, month]])[0]
    run.log_row(name='Crime Index', force=fi, caught=ans[1], crime=crime)
    #print(crime, force, ans)

# =============================================================
# Send results to AML
# =============================================================

run.log('accuracy', np.float(accuracy))
run.log('estimators', np.float(n_estimators))

# Done! Now upload results as pickles
# Files saved in the outputs folder are automatically uploaded into AML 
os.makedirs('outputs', exist_ok=True)

with open("outputs/model.pkl" , 'wb') as file:  
    pickle.dump(model, file)
    file.close()

lookup = OrderedDict()
# Lookup needs to contain our encoded labels and their values as a OrderedDict of dicts
lookup["force"] = {force: fi for fi, force in enumerate(reported_by_encoder.classes_)}
lookup["crime"] = {crime: ci for ci, crime in enumerate(crime_encoder.classes_)}
lookup["month"] = 0
with open("outputs/lookup.pkl" , 'wb') as file:  
    pickle.dump(lookup, file)
    file.close()
    
# Create output lookup
flags = ["notCaughtProb", "caughtProb"]
with open("outputs/flags.pkl" , 'wb') as file:  
    pickle.dump(flags, file)
    file.close()
