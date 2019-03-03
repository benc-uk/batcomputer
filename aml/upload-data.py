import os, sys, urllib.request, argparse
from dotenv import load_dotenv
from amllib.utils import connectToAML

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_DATAPATH

# For local dev and testing, using .env files. 
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--data-dir', type=str, dest='data_dir', help='Directory holding local data to upload')
args, unknown = parser.parse_known_args()

if not args.data_dir:
  parser.print_help()
  exit(1)

dataPathRemote = os.environ['AZML_DATAPATH']

# You must run `az login` before running locally
ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit(1)

localFolder = os.path.join(os.getcwd(), args.data_dir)
print(f"### Local path resolves to {localFolder}")

ds = ws.get_default_datastore()
print(f"### Remote DS path is {dataPathRemote}")
print(f"### Uploading data to {ds.datastore_type}, {ds.account_name}, {ds.container_name}")
ds.upload(src_dir=localFolder, target_path=dataPathRemote, overwrite=True, show_progress=True)
