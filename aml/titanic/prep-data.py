import os, sys, urllib.request
sys.path.append("..")
from dotenv import load_dotenv
from amllib.utils import connectToAML, createComputeAML

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP

# For local dev and testing, using .env files. 
load_dotenv()

# Some consts
localDataPath = '../../data/titanic'
dataPathRemote = os.environ['AZML_DATAPATH']

# You must run `az login` before running locally
ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit(1)

localFolder = os.path.join(os.getcwd(), localDataPath)

ds = ws.get_default_datastore()
print(f"### Remote DS path is {dataPathRemote}")
print(f"### Uploading data to {ds.datastore_type}, {ds.account_name}, {ds.container_name}")
ds.upload(src_dir=localFolder, target_path=dataPathRemote, overwrite=True, show_progress=True)
