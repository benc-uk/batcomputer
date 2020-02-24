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
  logging.info('Python HTTP trigger function processed a request.')

  try:
    # Get input request POST data
    request_dict = req.get_json()
    
    # It's all about this single line of code...
    # ... get a prediction from the model
    results = predictor.predict(request_dict)

    # Pass back results as JSON
    return json.dumps(results)

  except KeyError as key_error:
    print('### KEY_ERROR:', str(key_error))
    return func.HttpResponse(json.dumps({'error': 'Value: '+str(key_error)+' not found in model lookup'}), status_code=400, mimetype='application/json')
  except Exception as err:
    print('### EXCEPTION:', str(err))
    return func.HttpResponse(json.dumps({'error': str(err)}), status_code=500, mimetype='application/json')
