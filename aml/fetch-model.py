#
# Azure ML Orchestration Script, Ben C 2019
# Fetch model and pickle files for building the model API app 
# - Requires env vars: AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_MODEL
#

import os, argparse
from dotenv import load_dotenv
from amllib.utils import connectToAML, downloadPickles, checkVars

# When local testing, load .env files for convenience
load_dotenv()
checkVars(['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_MODEL'])

parser = argparse.ArgumentParser()
parser.add_argument('--model-ver', type=str, dest='ver', help='Model version')
parser.add_argument('--use-best', dest='best', help='Find best model based on accuracy', default=False, action='store_true')
parser.add_argument('--output-path', type=str, dest='output', help='Output path for pickles', default='../model-api/pickles')
args, unknown = parser.parse_known_args()

outputPath = args.output

ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])

if args.best:
  downloadPickles(ws, os.environ['AZML_MODEL'], outputPath, "best")
if args.ver:
  downloadPickles(ws, os.environ['AZML_MODEL'], outputPath, int(args.ver))
elif not args.best:
  print(f"### No model version specified, latest will be used")
  downloadPickles(ws, os.environ['AZML_MODEL'], outputPath)

  