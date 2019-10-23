#
# Azure ML Orchestration Script, Ben C 2019
# Run a Python training script in remote Azure ML computer cluster
# - Requires env vars: AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_MODEL
#   AZML_EXPERIMENT, AZML_DATAPATH, AZML_SCRIPT, AZML_COMPUTE_NAME
# - Optional: AZML_RUN_LOCAL set to "true" in order to run training locally

import os, argparse
from dotenv import load_dotenv
from amllib.utils import connectToAML, getComputeAML, checkVars
from azureml.core import Experiment, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration, DataReferenceConfiguration

# When local testing, load .env files for convenience
load_dotenv()
checkVars(['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL', 'AZML_EXPERIMENT', 'AZML_DATAPATH', 'AZML_SCRIPT', 'AZML_COMPUTE_NAME'])

parser = argparse.ArgumentParser()
parser.add_argument('--estimators', type=int, dest='estimators', help='Number of estimators', default=40)
args, unknown = parser.parse_known_args()

# Some consts
trainingScriptDir = "../training"
dataPathRemote = os.environ['AZML_DATAPATH']
trainingScript = os.environ['AZML_SCRIPT']
estimators = args.estimators

ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])

# Create or get existing AML compute cluster 
computeTarget = getComputeAML(ws, os.environ['AZML_COMPUTE_NAME'])
if not computeTarget:
  print('### Failed! Bye!')
  exit()

# Create AML experiment and connect to default data store
exp = Experiment(workspace=ws, name=os.environ['AZML_EXPERIMENT'])
ds = ws.get_default_datastore()
print(f"### Working with experiment name '{exp.name}'")

# This allows us to mount/upload data to remote compute job
print(f"### Will mount datapath '{dataPathRemote}' on remote compute")
dataRef = DataReferenceConfiguration(
  datastore_name=ds.name, 
  path_on_datastore=dataPathRemote, 
  path_on_compute='/tmp',
  mode='download',
  overwrite=False
)

# Create a new RunConfiguration and attach data
runConfig = RunConfiguration()
runConfig.data_references = { ds.name: dataRef } # This syntax is not documented!

if not os.environ.get('AZML_RUN_LOCAL', 'false') == "true":
  # Set it up for running in Azure ML compute
  runConfig.target = computeTarget
  runConfig.environment.docker.enabled = True
  runConfig.auto_prepare_environment = True
  runConfig.environment.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn==0.20.3', 'pandas', 'matplotlib'])
  print(f"### Will execute script {trainingScriptDir}/{trainingScript} on REMOTE compute")
else:
  # OR set up RunConfig to run local, needs a pre-set up Python 3 virtual env
  runConfig.environment.python.user_managed_dependencies = True
  runConfig.environment.python.interpreter_path = os.environ['VIRTUAL_ENV'] + "/bin/python"
  print(f"### Will execute script {trainingScriptDir}/{trainingScript} on LOCAL compute")

# Pass two args to the training script
scriptArgs = ["--data-path", "/tmp/"+dataPathRemote, "--estimators", estimators]
scriptRunConf = ScriptRunConfig(source_directory = trainingScriptDir, script = trainingScript, arguments = scriptArgs, run_config = runConfig)

run = exp.submit(scriptRunConf)
print(f"### Run '{run.id}' submitted and started...")
run.wait_for_completion(show_output = True, wait_post_processing = True)

# ===== Training Complete =====

if run.status == "Failed":
  print(f'### ERROR! Run did not complete. Training failed!')
  exit(1)

accuracy = run.get_metrics()['accuracy'] or 0.0

model = run.register_model(
  model_path = 'outputs/model.pkl',
  model_name = os.environ['AZML_MODEL'],
  tags = {
    'accuracy': accuracy, 
    'aml-runid': run.id, 
    'aml-experiment': os.environ['AZML_EXPERIMENT']
  }
)

print(f"### Created model '{os.environ['AZML_MODEL']}' version: {model.version}")
