import logging
import os
import json
import azure.functions as func

# Import for the model scoring
#from predictor import Predictor
from __app__.lib.predictor import Predictor

pickleFolder = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../pickles")
print('### Looking for pickles in:', pickleFolder)
MODEL_NAME  = pickleFolder + '/model.pkl'
LOOKUP_NAME = pickleFolder + '/lookup.pkl'
FLAGS_NAME  = pickleFolder + '/flags.pkl'
METADATA_NAME  = pickleFolder + '/metadata.json'

def main(req: func.HttpRequest) -> func.HttpResponse:
  logging.info('Python HTTP trigger function processed a request.')

  predictor = Predictor(MODEL_NAME, LOOKUP_NAME, FLAGS_NAME)
  try:
    request_dict = json.loads(req.get_data().decode('utf-8'))
    results = predictor.predict(request_dict)
    return jsonify(results)

  except KeyError as key_error:
    print('### KEY_ERROR:', str(key_error))
    return func.HttpResponse(json.dumps({'error': 'Value: '+str(key_error)+' not found in model lookup'}), status=400, mimetype='application/json')
  except Exception as err:
    print('### EXCEPTION:', str(err))
    return func.HttpResponse(json.dumps({'error': str(err)}), status_code=500, mimetype='application/json')

  # if name:
  #   return func.HttpResponse(f"Hello {name}!")
  # else:
  #   return func.HttpResponse(
  #      "Please pass a name on the query string or in the request body",
  #      status_code=400
  #   )
