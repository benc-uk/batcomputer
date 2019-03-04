import os, sys
from dotenv import load_dotenv
from amllib.utils import connectToAML
from azureml.core.model import Model
from azureml.core import Experiment, Run

# For local dev and testing, using .env files. 
load_dotenv()

if not all(k in os.environ for k in ['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL']):
  print('### Required AZML env vars are not set, we gotta leave...')
  exit()

# You must run `az login` before running locally
ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit()

models = Model.list(ws)
for model in models:
  model.delete()
  print("### Deleted model", model.version)