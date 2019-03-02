import os, sys, urllib.request
sys.path.append("..")
from dotenv import load_dotenv
from azml_lib.utils import connectToAzureML, createComputeAML

# *** Expected external env variables ***
# AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP

# For local dev and testing, using .env files. 
load_dotenv()

# Some consts
dataFolderName = 'data'
dataPathRemote = 'titanic'

# You must run `az login` before running locally
ws = connectToAzureML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])
if not ws:
  print('### Failed! Bye!')
  exit()

dataFolder = os.path.join(os.getcwd(), dataFolderName)
os.makedirs(dataFolder, exist_ok = True)

ds = ws.get_default_datastore()
print(f"### Uploading data to {ds.datastore_type}, {ds.account_name}, {ds.container_name}")
ds.upload(src_dir=dataFolder, target_path=dataPathRemote, overwrite=True, show_progress=True)
