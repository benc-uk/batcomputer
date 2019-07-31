# Databricks notebook source
# Load all CSVs! Wildcard magic!
file_location = "/police-data/2017-*/*.csv"
file_type = "csv"

# CSV options
infer_schema = "true"
first_row_is_header = "true"
delimiter = ","

# The applied options are for CSV files. For other file types, these will be ignored.
df = spark.read.format(file_type) \
  .option("inferSchema", infer_schema) \
  .option("header", first_row_is_header) \
  .option("sep", delimiter) \
  .load(file_location)

# Rename the columns, removing spaces
df = df.toDF("CrimeID", "Month", "ReportedBy", "FallsWithin", "Lat", "Long", "Location", "LSOACode", "LSOAName", "Crime", "Outcome", "Context")

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE policedata

# COMMAND ----------

# Store as table
df.write.format("parquet").saveAsTable("policedata")

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from policedata

# COMMAND ----------

df = spark.table("policedata")
df.count()

# COMMAND ----------

