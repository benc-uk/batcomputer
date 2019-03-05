#
# Azure ML Orchestration Script, Ben C 2019
# Upload data from local machine to Azure ML workspace in default datastore
# - Requires env vars: AZML_WORKSPACE, AZML_SUBID, AZML_RESGRP, AZML_DATAPATH
#

import os, argparse
from dotenv import load_dotenv
from amllib.utils import connectToAML, checkVars

# When local testing, load .env files for convenience
load_dotenv()
checkVars(['AZML_SUBID', 'AZML_RESGRP', 'AZML_WORKSPACE', 'AZML_DATAPATH'])

parser = argparse.ArgumentParser()
parser.add_argument('--data-dir', type=str, dest='data_dir', help='Directory holding local data to upload')
args, unknown = parser.parse_known_args()

# --data-dir is a mandatory arg
if not args.data_dir:
  parser.print_help()
  exit(1)

ws = connectToAML(os.environ['AZML_SUBID'], os.environ['AZML_RESGRP'], os.environ['AZML_WORKSPACE'])

localFolder = os.path.join(os.getcwd(), args.data_dir)
print(f"### Local path resolves to {localFolder}")

ds = ws.get_default_datastore()
print(f"### Remote DS path is {os.environ['AZML_DATAPATH']}")
print(f"### Uploading data to {ds.datastore_type}, {ds.account_name}, {ds.container_name}")
ds.upload(src_dir=localFolder, target_path=os.environ['AZML_DATAPATH'], overwrite=True, show_progress=True)
