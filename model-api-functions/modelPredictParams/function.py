import logging
import os
import json
import azure.functions as func

# Import for the model scoring
from __app__.lib.predictor import Predictor

# Location of our trained model
modelPath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../models")
print('### Looking for model in:', modelPath)
MODEL_NAME  = modelPath + '/model.pkl'
LOOKUP_NAME = modelPath + '/lookup.pkl'
FLAGS_NAME  = modelPath + '/flags.pkl'
METADATA_NAME  = modelPath + '/metadata.json'

# Instantiate our predictor
predictor = Predictor(MODEL_NAME, LOOKUP_NAME, FLAGS_NAME)

#
# Function entrypoint, passed a HttpRequest object
#
def main(req: func.HttpRequest) -> func.HttpResponse:
  resp = {}
  for key in predictor.lookup:
    if type(predictor.lookup[key]) == type(dict()):
      resp[key] = [subkey for subkey in predictor.lookup[key].keys()]
    else:
      resp[key] = 0

  return func.HttpResponse(json.dumps(resp), mimetype='application/json')
