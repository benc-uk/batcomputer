#
# Azure ML Orchestration Script, Ben C 2019
# ** WARNING ** Cleanup. Removes all models from the workspace
# - Requires env vars: AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_MODEL
#

import os
from dotenv import load_dotenv
from amllib.utils import connectToAML, checkVars
from azureml.core.model import Model

# When local testing, load .env files for convenience
load_dotenv()
checkVars(['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL'])

ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])

models = Model.list(ws)
for model in models:
  model.delete()
  print("### Deleted model", model.name, model.version)