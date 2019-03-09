# Model API service / Wrapper App

The model API wrapper is a Python Flask app, designed to wrap the model with a REST based API. It is standalone, lightweight and designed to run in a container

The app will load the trained model and other pickle files at startup from the local filesystem, located in the `./pickles/` directory. To fetch these from Azure ML, use the `aml/fetch-model.py` script which will connect to to the service and download the files for any given model version. See the [AML scripts docs](#) for more details

The app has been designed to be as re-usable and generic as possible, so it can serve a range of models, assuming they have been developed and trained with Scikit-learn, and the corresponding `lookup.pkl` and `flags.pkl` are also provided

!TOUPDATE! For more info on the pickle files and the model registry [please refer to the main docs](../#model-registry)

## Source Code
Source is located in the [`./src`](./src) directory

## Configuration & Networking
The app is written using Flask, and listens on port 8000 by default. If the `PORT` environmental variable is found and set, that value will be used instead

When running as a container Gunicorn is used as a WSGI HTTP server protecting Flask from direct HTTP access

The Flask server ignores CORS and will accept requests from any origin

## Local Development
If you want to build locally you will need Python 3.6 and/or Docker.  
These steps all assume the model pickle files have **already been trained and are held in Azure ML, and you have downloaded them locally using `fetch-model.py` script**, resulting in a `pickles/` directory being created and populated with four files (3 .pkl and metadata.json) in the `/model-api` directory

You must work from the `/model-api` directory not the root of the project

## Running Directly in Python
- Follow the [Python Environment steps in the setup guide](../docs/setup#python-environment)
- `python ../aml/fetch-model.py`
- Run `python src/server.py`

## Building Container Image
Manually building and tagging the container locally is done as follows:

- Follow the [Python Environment steps in the setup guide](../docs/setup#python-environment)
- `python ../aml/fetch-model.py`
- `docker build . -f Dockerfile -t batcomputer-api`
- `docker run -p 8000:8000 batcomputer-api`

## API Description
The wrapper app dynamically creates a Swagger definition from the provided `lookup.pkl` and `flags.pkl` files at startup. So in effect it is a generic app that could wrap any Scikit-Learn model. 

The Swagger definition provides guidance to callers of the API on what parameters are expected and allowed values in the request 

API and routes exposed by the app are:
- **GET** `/api/info` - Return status and model metadata (name, version, tags)
- **GET** `/api/docs` - Swagger UI
- **GET** `/swagger.json` - Base Swagger definition file describing the API
- **POST** `/api/predict` - Payload body should be JSON, will return prediction response in JSON. See the Swagger file for example payload
- **GET** `/api/predict/params` - Return a list of parameters to invoke the predict API. The parameters names and possible values are returned (as an array of acceptable strings). If a parameter accepts a number rather than a string then `0` will be shown
e.g.
```
GET /api/predict/params
{
  "gender": [ "male", "female" ],
  "age: 0,
  "location": [ "London", "New York", "Bognor Regis" ]
}
```
