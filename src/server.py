import json
import os

# Imports for the REST API
from flask import Flask, request, jsonify, Response
from swagger import register_swagger_ui, generate_swagger

# Import for the model scoring
from predictor import predict, initialize

MODEL_NAME  = './model.pkl'
LOOKUP_NAME = './lookup.pkl'
FLAGS_NAME  = './flags.pkl'

application = Flask(__name__)

# Load and initialize the model
initialize(MODEL_NAME, LOOKUP_NAME, FLAGS_NAME)

# Swagger stuff
generate_swagger(LOOKUP_NAME, FLAGS_NAME)
register_swagger_ui(application)

# Main API route(s)
@application.route('/api/predict', methods=['POST'])
def main_api(project=None):
  try:
    request_dict = json.loads(request.get_data().decode('utf-8'))
    results = predict(request_dict)
    return jsonify(results)

  except KeyError as key_error:
    print('### KEY_ERROR:', str(key_error))
    return Response(json.dumps({'error': 'Value: '+str(key_error)+' not found in model lookup'}), status=400, mimetype='application/json')
  except Exception as err:
    print('### EXCEPTION:', str(err))
    return Response(json.dumps({'error': str(err)}), status=500, mimetype='application/json')

@application.route('/api/info', methods=['GET'])
def info_api(project=None):
  return Response(json.dumps({'status': 'alive', 'model_ver': os.getenv('VERSION')}), status=200, mimetype='application/json')


# Run the server if not running under WSGI
if __name__ == "__main__":
  PORT = os.getenv('SERVER_PORT', '8000')
  application.run(host='0.0.0.0', port=int(PORT))
