import json
import os

# Imports for the REST API
from flask import Flask, request, jsonify, Response
from swagger import register_swagger_ui, generate_swagger

# Import for the model scoring
from predictor import Predictor

# Pickle filenames
pickleFolder = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../pickles")
print('### Looking for pickles in:', pickleFolder)
MODEL_NAME  = pickleFolder + '/model.pkl'
LOOKUP_NAME = pickleFolder + '/lookup.pkl'
FLAGS_NAME  = pickleFolder + '/flags.pkl'
METADATA_NAME  = pickleFolder + '/metadata.json'

# Set up Flask
application = Flask(__name__)

# Load and initialize the model
predictor = Predictor(MODEL_NAME, LOOKUP_NAME, FLAGS_NAME)

# Swagger stuff
generate_swagger(predictor.lookup, predictor.flags)
register_swagger_ui(application)


#
# API route - for prediction
#
@application.route('/api/predict', methods=['POST'])
def main_api(project=None):
  try:
    request_dict = json.loads(request.get_data().decode('utf-8'))
    results = predictor.predict(request_dict)
    return jsonify(results)

  except KeyError as key_error:
    print('### KEY_ERROR:', str(key_error))
    return Response(json.dumps({'error': 'Value: '+str(key_error)+' not found in model lookup'}), status=400, mimetype='application/json')
  except Exception as err:
    print('### EXCEPTION:', str(err))
    return Response(json.dumps({'error': str(err)}), status=500, mimetype='application/json')


#
# API route - for status/info
#
@application.route('/api/info', methods=['GET'])
def info_api(project=None):
  metadata = {}
  try:
    with open(METADATA_NAME) as f:
      metadata = json.load(f)
  except Exception as err:
    print('### EXCEPTION:', str(err))
    return Response(json.dumps({'error': str(err)}), status=500, mimetype='application/json')
  return Response(json.dumps({'status': 'alive', 'metadata': metadata}), status=200, mimetype='application/json')


#
# API route - for getting lookup parameters
#
@application.route('/api/predict/params', methods=['GET'])
def params_api(project=None):
  resp = {}
  for key in predictor.lookup:
    if type(predictor.lookup[key]) == type(dict()):
      resp[key] = [subkey for subkey in predictor.lookup[key].keys()]
    else:
      resp[key] = 0

  return Response(json.dumps(resp), status=200, mimetype='application/json')


#
# CORS - Allow everyone & everything
#
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# ===========================================================================================================================

# Run the server if not running under WSGI
if __name__ == "__main__":
  PORT = os.getenv('SERVER_PORT', '8000')
  application.run(host='0.0.0.0', port=int(PORT))
