import os.path
import pickle
import json
from flask import Response
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/swagger.json'  # URL of source swagger file
SWAGGER_FILE = './swagger.json'  

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
  SWAGGER_URL, 
  API_URL,
  config={ 
    'app_name': "Batcomputer"
  }
)

def generate_swagger(lookup, flags):
  outfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), SWAGGER_FILE)
  swagger_obj = format_swagger(lookup, flags)

  open(outfile, "w+").writelines(json.dumps(swagger_obj))


def register_swagger_ui(app):
  # Register blueprint at URL
  # (URL must match the one given to factory function above)
  app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

  # Route for Swagger file
  @app.route('/swagger.json', methods=['GET'])
  def get_swagger():  # pragma: no cover
      content = __get_file(SWAGGER_FILE)
      return Response(content, mimetype="application/json")


def __get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)


def format_swagger(lookup, flags):
  input_props = {
  }
  for lookup_key in lookup.keys():
    if type(lookup[lookup_key]) == type(dict()):
      input_props[lookup_key] = {
        "type": "string",
        "example": list(lookup[lookup_key].keys())[0]
      }
    else:
      input_props[lookup_key] = {
        "type": "number"
      }

  output_props = {
  }
  for flag in flags:
    output_props[flag] = {
      "type": "number",
      "format": "float",
      "example": "0.5"
    }

  swagger_template = {
    "swagger": "2.0",
    "info": {
      "version": os.getenv('VERSION', '1.0.0'),
      "title": "Batcomputer API",
      "description": "REST API getting predictions from the Batcomputer ML model. Model version: "+os.getenv('VERSION', '1.0.0')
    },
    "basePath": "/api",
    "schemes": [
      "http"
    ],
    "paths": {
      "/predict": {
        "post": {
          "tags": ["Predictions"],
          "description": "Get a prediction from the model",
          "operationId": "predict",
          "produces": [
            "application/json"
          ],       
          "parameters": [
            {
              "in": "body",
              "name": "body",
              "description": "Request object",
              "required": "true",
              "schema": {
                "properties": input_props
              }            
            }
          ],        
          "responses": {
            "200": {
              "description": "Prediction scores as probabilities",
              "schema": {
                "properties": output_props
              }
            },
            "400": {
              "description": "Input is invalid, check key names in request object"
            }
          }
        }
      },
      "/info": {
        "get": {
          "tags": ["Info"],
          "description": "Get system info, health check",
          "operationId": "info",
          "produces": [
            "application/json"
          ],       
          "parameters": [],        
          "responses": {
            "200": {
              "description": "Simple system information in JSON format"
            }
          }
        }
      },
      "/predict/params": {
        "get": {
          "tags": ["Predictions"],
          "description": "Get mapping parameters for calling the predict API",
          "operationId": "params",
          "produces": [
            "application/json"
          ],       
          "parameters": [],        
          "responses": {
            "200": {
              "description": "List of parameters and their possible values as a dictionary"
            }
          }
        }
      }      
    }
  }
  return swagger_template