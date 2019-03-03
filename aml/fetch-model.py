import os, sys, argparse
sys.path.append("..")
from dotenv import load_dotenv
from amllib.utils import connectToAML, downloadPickles
from azureml.core.model import Model
from azureml.core import Experiment, Run

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP

# For local dev and testing, using .env files. 
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--model-ver', type=str, dest='ver', help='Model version')
args, unknown = parser.parse_known_args()

if not all(k in os.environ for k in ['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL']):
  print('### Required AZML env vars are not set, we gotta leave...')
  exit()

# You must run `az login` before running locally
ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit()

if args.ver:
  downloadPickles(ws, os.environ['AZML_MODEL'], '../model-api/pickles', int(args.ver))
else:
  print(f"### No model version specified, latest will be used")
  downloadPickles(ws, os.environ['AZML_MODEL'], '../model-api/pickles')