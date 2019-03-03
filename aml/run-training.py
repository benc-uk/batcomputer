import os, sys, argparse
sys.path.append("..")
from dotenv import load_dotenv
from amllib.utils import connectToAML, getComputeAML
from azureml.core import Experiment, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, RunConfiguration, DataReferenceConfiguration

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_MODEL, AZML_EXPERIMENT, AZML_DATAPATH, AZML_SCRIPT, AZML_COMPUTE_NAME

# For local dev and testing, using .env files. 
load_dotenv()

if not all(k in os.environ for k in ['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL', 'AZML_EXPERIMENT', 'AZML_DATAPATH', 'AZML_SCRIPT', 'AZML_COMPUTE_NAME']):
  print('### Required AZML env vars are not set, we gotta leave...')
  exit()

# Some consts
dataPathRemote = os.environ['AZML_DATAPATH']
trainingScriptDir = "../training"
trainingScript = os.environ['AZML_SCRIPT']
estimators = 50

# You must run `az login` before running locally
ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit()

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
dataRef = DataReferenceConfiguration(datastore_name=ds.name, 
                  path_on_datastore=dataPathRemote, 
                  path_on_compute='/tmp',
                  mode='download',
                  overwrite=False)

# Create a new RunConfiguration 
runConfig = RunConfiguration()
runConfig.data_references = { ds.name: dataRef } 

# Set it up for running in Azure ML compute
runConfig.target = computeTarget
runConfig.environment.docker.enabled = True
runConfig.environment.docker.base_image = DEFAULT_CPU_IMAGE
runConfig.environment.python.user_managed_dependencies = False
runConfig.auto_prepare_environment = True
runConfig.environment.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn', 'pandas'])

# OR set up RunConfig to run local, needs a pre-set up Python 3 virtual env
# runConfig.environment.python.user_managed_dependencies = True
# runConfig.environment.python.interpreter_path = "/home/ben/dev/py-venv/bin/python3"

print(f"### Will execute script {trainingScriptDir}/{trainingScript} on remote compute")
scriptArgs = ["--data-path", "/tmp/"+dataPathRemote, "--estimators", estimators]
scriptRunConf = ScriptRunConfig(source_directory = trainingScriptDir, script = trainingScript, arguments = scriptArgs, run_config = runConfig)
run = exp.submit(scriptRunConf)
print(f"### Run '{run.id}' submitted and started...")
run.wait_for_completion(show_output = True, wait_post_processing = True)

# ===== Training Complete =====

if run.status == "Failed":
  print(f'### ERROR! Run did not complete. Training failed!')
  exit(1)

modelTags = {'aml-runid': run.id, 
             'aml-experiment': os.environ['AZML_EXPERIMENT']}
model = run.register_model(model_path = 'outputs/model.pkl',
                           model_name = os.environ['AZML_MODEL'],
                           tags = modelTags)