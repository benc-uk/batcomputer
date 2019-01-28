# Model API service / Wrapper App

The model API wrapper is a Python Flask app, designed to wrap the model with a REST based API. It is standalone, lightweight and designed to run in a container

The app will load the trained model and other pickle files at startup from the local filesystem, located in the `./pickles/` directory. A helper script `./scripts/get-pickles.sh` is provided which uses the Azure CLI to fetch the pickles from Azure Blob storage (aka the model registry)

The app has been designed to be as re-usable and generic as possible, so it can serve a range of models, assuming they have been developed and trained with Scikit-learn, and the corresponding `lookup.pkl` and `flags.pkl` are also provided

For more info on the pickle files and the model registry [please refer to the main docs](../#model-registry)

## Source Code
Source is located in the [`./src`](./src) directory

## Configuration & Networking
The app is written using Flask, and listens on port 8000 by default. If the `PORT` environmental variable is found and set, that value will be used instead

When running as a container Gunicorn is used as a WSGI HTTP server protecting Flask from direct HTTP access

The Flask server ignores CORS and will accept requests from any origin

## Local Development
If you want to build locally you will need Python 3.6 and/or Docker. These steps all assume the model pickle files have already been trained and pushed into Blob storage (by the training job/Notebook) for the corresponding version you are trying to run and build

You must work from the `/model-api` directory not the root of the project

Create a `.env` file based from a copy of the provided `.env.sample` and configure the values as per your environment

- Set the model version you are working to in the `.env` file as described above
- Run `./scripts/get-pickles.sh` to fetch the pickle files to your local system

## Running Directly in Python
- Create Python virtual environment `python3 -m venv pyvenv`
- Activate virtual environment `source ./pyvenv/bin/activate`
- Install requirements `pip3 install -r requirements.txt`
- Run `python3 src/server.py`

## Building Container Image
Manually building and tagging the container locally is done as follows:

- Carry out the steps in [Local Development](#local-development) above
- `docker build . -f Dockerfile -t batcomputer-api`
- `docker run -p 8000:8000 batcomputer-api`

## API Description
The wrapper app dynamically creates a Swagger definition from the provided `lookup.pkl` and `flags.pkl` files at startup. So in effect it is a generic app that could wrap any Scikit-Learn model. 

The Swagger definition provides guidance to callers of the API on what parameters are expected and allowed values in the request 

API and routes exposed by the app are:
- **GET** `/api/info` - Return simple status as JSON, for status checking
- **GET** `/api/docs` - Swagger UI
- **GET** `/swagger.json` - Base Swagger definition file describing the API
- **POST** `/api/predict` - Payload body should be JSON, will return prediction response in JSON. See the Swagger file for example payload
- **GET** `/api/predict/params` - Return a list of parameters to invoke the predict API. The parameters names and possible values are returned (as an array of acceptable strings). If a parameter accepts a number rather than a string then `0` will be shown
e.g.
```
GET /api/predict/params
{
  "gender": [ "male", "female" ],
  "age: 0
  "location": [ "London", "New York", "Bognor Regis" ]
}
```
