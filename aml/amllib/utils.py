import os, json
from azureml.core import Workspace, Experiment, Run
from azureml.core.model import Model
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.compute import AmlCompute, ComputeTarget, DatabricksCompute
from azureml.exceptions import ComputeTargetException

#
#
#
def checkVars(envVars):
  for var in envVars:
    if var not in os.environ:
      print(f"### ERROR: Environmental variable '{var}' not set! Exiting now, bye...")
      exit(1)

#
#
#
def connectToAML(subId, resGrp, ws):
  try:
    #cli_auth = AzureCliAuthentication()
    #ws = Workspace(subscription_id = subId, resource_group = resGrp, workspace_name = ws, auth=cli_auth)
    ws = Workspace.get(name = ws, subscription_id = subId, resource_group = resGrp)
    print(f"### Connected to Azure ML workspace '{ws.name}'")
    return ws
  except:
    print('### ERROR: Unable to connect to workspace! Exiting now, bye...')
    exit(1)

#
#
#
def downloadPickles(ws, modelName, outputPath="./pickles", modelVer=None):
  if modelVer == 'best':
    bestModel = None
    maxAcc = -1
    for model in Model.list(ws, modelName, ["accuracy"]):
      modelAcc = float(model.tags["accuracy"])
      if modelAcc > maxAcc:
        bestModel = model
        maxAcc = modelAcc
    
    print(f"### Best model with highest accuracy of {maxAcc} found")

    if not bestModel:
      model = Model(ws, modelName)
      print("### WARNING! No best model found, using latest instead")
  elif modelVer is not None:
    model = Model(ws, modelName, version=modelVer)
  else:
    model = Model(ws, modelName)

  print(f"### Using model version {model.version}")
  # Echo'ing out this magic string sets an output variable in Azure DevOps pipeline
  # Set AZML_MODEL_VER for use by subsequent steps
  print(f"##vso[task.setvariable variable=AZML_MODEL_VER]{model.version}")

  # These are special tags, lets us get back to the run that created the model 
  try:
    runId = model.tags['aml-runid']
    experimentName = model.tags['aml-experiment']
  except:
    print("### ERROR! Model missing `aml-runid` and `aml-experiment` tags, Can't continue!")
    exit()

  exp = Experiment(workspace=ws, name=experimentName)
  run = Run(exp, runId)
  if run.status != "Completed":
    print(f'### ERROR! Run {runId} did not complete!')
    return

  print(f'### Will download from run {runId} in {experimentName}')

  # Now we can get all the files created with the run, grab all the .pkls
  for f in run.get_file_names():
    if f.endswith('.pkl'):
      output_file_path = os.path.join(outputPath, f.split('/')[-1])
      print('### Downloading from {} to {} ...'.format(f, output_file_path))
      run.download_file(name=f, output_file_path=output_file_path)

  # Add some extra metadata, handy to have
  metadata = { 'name': model.name, 'version': model.version, 'tags': model.tags }
  with open(f"{outputPath}/metadata.json", 'w') as metadata_file:
    print(f"### Storing metadata in {outputPath}/metadata.json")
    json.dump(metadata, metadata_file)

#
#
#
def getComputeAML(ws, name="amlcluster"):
  # Azure ML compute configuration
  if name in ws.compute_targets:
      compute_target = ws.compute_targets[name]
      if compute_target and type(compute_target) is AmlCompute:
          print(f"### Found existing cluster '{name}' so will use it")
          return compute_target
  else:
      nodesMin = int(os.environ.get('AZML_COMPUTE_MIN_NODES', "0"))
      nodesMax = int(os.environ.get('AZML_COMPUTE_MAX_NODES', "3"))
      vmSize = os.environ.get('AZML_COMPUTE_VMSIZE', "Standard_D3_v2")

      print(f"### Creating cluster '{name}' this could take time...")
      provisioning_config = AmlCompute.provisioning_configuration(vm_size = vmSize, 
                            min_nodes = nodesMin, 
                            max_nodes = nodesMax,
                            idle_seconds_before_scaledown = 3600)

      # create the cluster
      compute_target = ComputeTarget.create(ws, name, provisioning_config)
      
      # can poll for a minimum number of nodes and for a specific timeout. 
      # if no min node count is provided it will use the scale settings for the cluster
      compute_target.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)
      
      # For a more detailed view of current AmlCompute status, use get_status()
      print(compute_target.get_status().serialize())
      return compute_target
