# DataBricks Configs

Requires DataBricks CLI to use. https://docs.databricks.com/user-guide/dev-tools/databricks-cli.html  

In order to use the DataBricks CLI a PAT first needs to be created https://docs.databricks.com/api/latest/authentication.html#authentication


## Create cluster
```
databricks clusters create --json-file databricks/cluster.json
```

## Create jobs
 **IMPORTANT!** Before running edit the JSON files and put the cluster id in the `existing_cluster_id` field
```
databricks clusters create --json-file databricks/job-train-batcomputer-model.json
databricks clusters create --json-file databricks/job-train-titanic-model.json
```

Note. The job-ids are used by the pipelines and are currently hard coded, after creation run `databricks jobs list` to get each job's id. In a fresh deployment the job-ids start at **1**