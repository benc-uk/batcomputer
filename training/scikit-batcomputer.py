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
#df.registerTempTable("temp")
#df = sqlContext.sql("select * from temp where Month = '2017-01'")

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

