# Databricks notebook source
# MAGIC %md ## Load the DataBricks table as Spark DataFrame

# COMMAND ----------

df = spark.table("policedata")

df = df.drop('FallsWithin')
df = df.drop('Lat')
df = df.drop('Long')
df = df.drop('Context')
df = df.drop('Location')
df = df.drop('LSOACode')
df = df.drop('LSOAName')
df = df.drop('CrimeID')

df = df.na.drop()

# Filter subset (remove when doing full training)
df.registerTempTable("temp")
df = sqlContext.sql("select * from temp where Month = '2017-01'")

print("Working with", "{:,}".format(df.count()), "rows of amazing crime data!")

# COMMAND ----------

# MAGIC %md ## Input parameters when invoked by AML

# COMMAND ----------

# let user feed in parameters, the location of the data files (from datastore)
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--estimators', type=int, dest='estimators', help='number of estimators')
args, unknown = parser.parse_known_args()

n_estimators = args.estimators

if not n_estimators: n_estimators = 40
  
print("********* TRAINING PARAMS: n_estimators=", n_estimators)

# COMMAND ----------

# MAGIC %md ## Encoding and feature extraction

# COMMAND ----------

from pyspark.ml.feature import StringIndexer
from pyspark.sql.types import IntegerType

# Encode the Outcome for our mapping  
indexer = StringIndexer(inputCol="Outcome", outputCol="Outcome_e")
indexerModel = indexer.fit(df)
OutcomeMap = {}
for idx, lab in enumerate(indexerModel.labels):
  OutcomeMap[lab] = idx   
df = indexerModel.transform(df)

# !IMPORTANT! This maps outcomes to our caught/not-caught for the crime: 1 = caught, 0 = not caught
#print(OutcomeMap)
# Note outcome 5 is "given a caution", which can make a big difference in the numbers
mapOutcomeUDF = udf(lambda x: 1 if x in [5, 6, 15, 18, 7, 12, 22, 21, 20, 17, 13] else 0, IntegerType())
df = df.withColumn("y", mapOutcomeUDF(df.Outcome_e))

# Encode the Crime and ReportedBy columns we'll be training on 
indexer = StringIndexer(inputCol="ReportedBy", outputCol="ReportedBy_e")
indexerModel = indexer.fit(df)
ReportedByMap = {}
for idx, lab in enumerate(indexerModel.labels):
  ReportedByMap[lab] = idx    
df = indexerModel.transform(df)

indexer = StringIndexer(inputCol="Crime", outputCol="Crime_e")
indexerModel = indexer.fit(df)
CrimeMap = {}
for idx, lab in enumerate(indexerModel.labels):
  CrimeMap[lab] = idx      
df = indexerModel.transform(df)  

# Finally add the month as an integer
mapMonthUDF = udf(lambda month: int(month[-2:]), IntegerType())
df = df.withColumn("Month_e", mapMonthUDF(df.Month))

# COMMAND ----------

# MAGIC %md ## Convert DF to Numpy array

# COMMAND ----------

import numpy as np
training_array = np.array(df.select("y", "ReportedBy_e", "Crime_e", "Month_e").collect())

# COMMAND ----------

# MAGIC %md ## Training the model with Scikit

# COMMAND ----------

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import BaggingClassifier

classifier = RandomForestClassifier(n_estimators = 100)
X = training_array[0:, 1:].astype(int)
y = training_array[0:, 0].astype(int)
model = classifier.fit(X, y)

# COMMAND ----------

# MAGIC %md ## Test the model

# COMMAND ----------

# print(CrimeMap)
# print()
# print(ReportedByMap)
# print()
# Test all forces, with crime 12 = possesion of a weapon
for f, fi in ReportedByMap.items():
  a = model.predict_proba([[fi, 12, 3]])[0]
  print(f, a)

# COMMAND ----------

# MAGIC %md ## Pickle model outputs back to AML

# COMMAND ----------

from collections import OrderedDict
from azureml.core import Run
import os, pickle

run = Run.get_context()
run.log('estimators', np.float(n_estimators))

# note files saved in the outputs folder is automatically uploaded into experiment record
os.makedirs('outputs', exist_ok=True)

with open("outputs/model.pkl" , 'wb') as file:  
    pickle.dump(model, file)
    file.close()

lookup = OrderedDict()
lookup["force"] = ReportedByMap
lookup["crime"] = CrimeMap
lookup["month"] = 0
with open("outputs/lookup.pkl" , 'wb') as file:  
    pickle.dump(lookup, file)
    file.close()
    
# Create output lookup
flags = ["notCaughtProb", "caughtProb"]
with open("outputs/flags.pkl" , 'wb') as file:  
    pickle.dump(flags, file)
    file.close()


# COMMAND ----------


