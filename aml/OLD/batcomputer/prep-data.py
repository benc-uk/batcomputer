import os, sys
sys.path.append("..")
from dotenv import load_dotenv
from amllib.utils import connectToAML, getComputeDataBricks
from azureml.core import Experiment, ScriptRunConfig
from azureml.pipeline.steps import DatabricksStep
from azureml.pipeline.core import Pipeline

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_MODEL, AZML_EXPERIMENT, AZML_DATABRICKS_TARGET

# For local dev and testing, using .env files. 
load_dotenv()

if not all(k in os.environ for k in ['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL', 'AZML_EXPERIMENT', 'AZML_DATABRICKS_TARGET']):
  print('### Required AZML env vars are not set, we gotta leave...')
  exit()

# Some consts
trainingScriptDir = '../../training'
trainingScript = 'scikit-batcomputer.py'

# You must run `az login` before running locally
ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit()

# Create or get existing AML compute cluster 
computeTarget = getComputeDataBricks(ws, os.environ['AZML_DATABRICKS_TARGET'])
if not computeTarget:
  print('### Failed! Bye!')
  exit()

# Create AML experiment and connect to default data store
exp = Experiment(workspace=ws, name=os.environ['AZML_EXPERIMENT'])
print(f"### Working with experiment name '{exp.name}'")

python_script_name = "dataprep-batcomputer.py"
source_directory = "../../training/"

dbPythonInLocalMachineStep = DatabricksStep(
  name="DBPythonInLocalMachine",
  num_workers=1,
  python_script_name=python_script_name,
  source_directory=source_directory,
  run_name='batcomputer-dataprep',
  compute_target=computeTarget,
  allow_reuse=True,
  existing_cluster_id="0125-150225-khans508"
)

steps = [dbPythonInLocalMachineStep]
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline_run = exp.submit(pipeline)
pipeline_run.wait_for_completion(show_output = True)