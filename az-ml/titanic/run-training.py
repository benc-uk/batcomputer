import os, sys
sys.path.append("..")
from dotenv import load_dotenv
from azml_lib.utils import connectToAzureML, createComputeAML
from azureml.core import Experiment, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, RunConfiguration, DataReferenceConfiguration

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP

# For local dev and testing, using .env files. 
load_dotenv()

# Some consts
experimentName = 'titanic'
dataPathRemote = 'titanic'
trainingScriptDir = 'training'
script = 'train.py'

if not all(k in os.environ for k in ['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE']):
  print('### Required AZML env vars are not set, we gotta leave...')
  exit()

# You must run `az login` before running locally
ws = connectToAzureML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit()

# Create or get existing compute 
computeTarget = createComputeAML(ws, os.environ['AZML_COMPUTE_NAME'], os.environ['AZML_COMPUTE_MIN_NODES'], os.environ['AZML_COMPUTE_MAX_NODES'], os.environ['AZML_COMPUTE_VMSIZE'])
if not computeTarget:
  print('### Failed! Bye!')
  exit()

# Create AML experiment and connect to default data store
exp = Experiment(workspace=ws, name=experimentName)
ds = ws.get_default_datastore()

# This allows us to mount/upload data to remote compute job
dataRef = DataReferenceConfiguration(datastore_name=ds.name, 
                  path_on_datastore=dataPathRemote, 
                  path_on_compute='/tmp',
                  mode='download',
                  overwrite=False)

# Create a new RunConfiguration this is tightly bound to the AML computeTarget
runConfig = RunConfiguration()
runConfig.target = computeTarget
runConfig.environment.docker.enabled = True
runConfig.environment.docker.base_image = DEFAULT_CPU_IMAGE
runConfig.environment.python.user_managed_dependencies = False
runConfig.auto_prepare_environment = True
runConfig.environment.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn', 'pandas'])
runConfig.data_references = { ds.name: dataRef } 

scriptArgs = ["--data-path", "/tmp/"+dataPathRemote, "--estimators", 6000]

scriptRunConf = ScriptRunConfig(source_directory = trainingScriptDir, script = script, arguments = scriptArgs, run_config = runConfig)
run = exp.submit(scriptRunConf)
run.wait_for_completion(show_output = True, wait_post_processing = True)
