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
#classifier = BaggingClassifier()
X = training_array[0:, 1:].astype(int)
y = training_array[0:, 0].astype(int)
model = classifier.fit(X, y)

# COMMAND ----------

# MAGIC %md ## Test the model

# COMMAND ----------

print(CrimeMap)
print()
print(ReportedByMap)
print()
# Test all forces, with crime 12 = possesion of a weapon
for f, fi in ReportedByMap.items():
  a = model.predict_proba([[fi, 12, 3]])[0]
  print(f, a)

# COMMAND ----------

# MAGIC %md ## Pickle model and push to Azure storage

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
  lookup["force"] = ReportedByMap
  lookup["crime"] = CrimeMap
  lookup["month"] = 0

  # Create output lookup
  flags = ["SafeRisk", "CaughtRisk"]

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