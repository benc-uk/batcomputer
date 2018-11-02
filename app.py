import json
import os
import traceback
import pprint

# Imports for the REST API
from flask import Flask, request, jsonify, Response
from predictor import predict, initialize

APP_NAME    = 'batcomputer-api'
MODEL_NAME  = './model.pkl'
LOOKUP_NAME = './lookup.pkl'
FLAGS_NAME  = './flags.pkl'

app = Flask(APP_NAME)

# Load and initialize the model
initialize(MODEL_NAME, LOOKUP_NAME, FLAGS_NAME)

@app.route('/api/predict', methods=['POST'])
def main_api(project=None):
  try:
    request_json = json.loads(request.get_data().decode('utf-8'))

    print(request_json['force_name'])
    results = predict(request_json) #request_json['force_name'], request_json['offence_description'], request_json['offence_subgroup'], request_json['offence_subgroup'])
    
    resp_data = {
      'score': results,
    }
    pprint.pprint(results)
    return jsonify(results)

  except KeyError as key_error:
    #traceback.print_exc()
    print('### EXCEPTION (KeyError):', str(key_error))
    #return jsonify({'error': 'Value: '+str(key_error)+' not found in model lookup'})
    return Response(json.dumps({'error': 'Value: '+str(key_error)+' not found in model lookup'}), status=400, mimetype='application/json')
  except Exception as err:
    #traceback.print_exc()
    print('### EXCEPTION:', str(err))
    return Response(json.dumps({'error': str(err)}), status=500, mimetype='application/json')


# Run the server
PORT = os.getenv('APP_PORT', '8000')
app.run(host='0.0.0.0', port=int(PORT))
