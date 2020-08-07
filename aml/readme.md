# Azure ML Orchestration Scripts
These scripts are at the heart of the Batcomputer project; driving the training & model generation, and tie closely into the operationalization process of building the model API

These are Python scripts that use the [Azure ML Python SDK](https://docs.microsoft.com/python/api/overview/azure/ml/intro) to run & drive several processes. They are described as 'orchestration' scripts in order to differentiate them from the Python scripts that perform the actual machine learning & training. 

Scripts have been developed in such a way they are re-usable and generic as possible, hence the high degree of parameterization. With a switch of a few variables a totally different model can be trained on different data

However few choices are fixed into the scripts to simplify matters:
- The remote compute target is always [Azure ML Compute](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute), which is simple to configure and use
- The cluster will scale down after 1 hour of idle time
- Training scripts are located in the `training` folder from the root of the project

The scripts can be run locally, but they are intended to be run by Azure DevOps in a pipeline

## Prereqs
- You must have an Azure ML Workspace  
You can use the [provided script](../azure) to create one or use the Azure Portal
- Python 3.6

## Running / Testing Locally
- Follow the [Python Environment steps in the setup guide](../docs/setup#python-environment)
- Copy/rename the `.env.sample` file to `.env` and edit to match your setup, the only variables you MUST change are the first three settings. See below
- Simply run with `python <script-name>` some scripts take command line parameters, all scripts rely on environmental variables

## Environmental Variables
The scripts make heavy use of system environmental variables, this allows them to used in Azure DevOps pipelines, where pipeline variables are automatically passed into scripts as environmental variables

| Variable Name            | Purpose                                                                                                            | Required By                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------- |
| `AZML_WORKSPACE`         | Name of your AML workspace                                                                                         | All scripts                     |
| `AZML_RESGRP`            | Resource group containing your workspace                                                                           | All scripts                     |
| `AZML_SUBID`             | Azure subscription ID                                                                                              | All scripts                     |
| `AZML_DATAPATH`          | Location in remote AML datastore to hold data, can simply be a name, e.g. `batcomputer-data`                       | upload-data.py, run-training.py |
| `AZML_SCRIPT`            | Model training script to be run by AML, must be located in the `training/` directory, e.g. `scikit-batcomputer.py` | run-training.py                 |
| `AZML_EXPERIMENT`        | Name of experiment in AML, will be created if doesn't exist. e.g. `batcomputer`                                    | run-training.py                 |
| `AZML_MODEL`             | Name of model to be registered in AML, will be created if doesn't exist. e.g. `batcomputer-model`                  | run-training.py, fetch-model.py |
| `AZML_RUN_LOCAL`         | When set to `true` run the training through AML but execute locally                                                | run-training.py (OPTIONAL)      |
| `AZML_COMPUTE_NAME`      | Name of AML Compute cluster, will be created if it doesn't exist, e.g. `demo-cluster`                              | run-training.py                 |
| `AZML_COMPUTE_VMSIZE`    | VM size used by AML Compute cluster, e.g. `Standard_D3_v2`                                                         | run-training.py                 |
| `AZML_COMPUTE_MAX_NODES` | Max number of nodes in the cluster, e.g. `3`                                                                       | run-training.py                 |
| `AZML_COMPUTE_MIN_NODES` | Min number of nodes in the cluster, e.g. `0`                                                                       | run-training.py                 |

When running locally these variables should be set in the `.env` file

## amllib.utils
This is a utility library containing some common routines and shared functions wrapping the AML SDK
- checkVars
- connectToAML
- getComputeAML
- downloadPickles

---

# Script: upload-data.py
This script simply uploads data from the local filesystem to the default datastore in the AML workspace, it takes a locally directory and the entire contents will be uploaded.

## Required Variables
`AZML_SUBID`, `AZML_RESGRP`, `AZML_WORKSPACE`, `AZML_DATAPATH`

## Params
- `--data-dir` Local filesystem path to be uploaded to the datastore and into `AZML_DATAPATH` (**Required**)

---

# Script: run-training.py
This script instructs the AML Service to carry out a training job. An overview of the steps carried out are:
- Connects to AML *Workspace*, (Set by `AZML_WORKSPACE`)
- Gets a *ComputeTarget* pointing to the AML cluster, creating it if it doesn't exist (Set by `AZML_COMPUTE_NAME`)
- Creates an *Experiment*, or reuses existing one (set by `AZML_EXPERIMENT`)
- Gets default *Datastore* in *Workspace*
- Creates a *DataReference* so that the `AZML_DATAPATH` in the *Datastore* is mounted to `/tmp` on the compute target for downloading data
- Sets up other *RunConfiguration* configuration, e.g. required Python packages (pandas, scikit-learn)
- Executes a *Run* using *ScriptRunConfig* pointing at `AZML_SCRIPT` training script
- Waits for completion
- On successful run, registers all files in `outputs/` with AML as a *Model*
- *Model* is tagged with meta-data

## Required Variables
`AZML_SUBID`, `AZML_RESGRP`, `AZML_WORKSPACE`, `AZML_MODEL`, `AZML_EXPERIMENT`, `AZML_DATAPATH`, `AZML_SCRIPT`, `AZML_COMPUTE_NAME`


## Params
- `--estimators` Number of estimators used when training, passed down to training script (**Optional**)  

---

# Script: fetch-model.py
This script accesses the AML Service to download a model as `model.pkl`, but also downloads associated `lookup.pkl` and `flags.pkl` files which are unique to the Batcomputer project and required for the model API

The script requires that the model registered with AML is uploaded with the path "outputs", all files from the model are downloaded and anything found in the "outputs" folder moved to the target `--output-path`

Along with the three .pkl files, a JSON file `metadata.json` is created with information such as the model version, which can then be used at runtime by the model API

The files are downloaded to `../model-api/pickles` by default, to be picked up and used by the model API at runtime during Docker image build

## Required Variables
`AZML_SUBID`, `AZML_RESGRP`, `AZML_WORKSPACE`, `AZML_MODEL`

## Params
- `--model-ver` Download a specific version, if omitted the newest version will be fetched (**Optional**)  
- `--use-best` Try to use the "best" version, based on accuracy. Models must be tagged with `accuracy` as a float (**Optional**)  
- `--output-path` Override the default output path which is `../model-api`,  (**Optional**)  
