import os
import azureml
from azureml.core import Workspace, Experiment, Run
from azureml.core.model import Model
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.compute import AmlCompute, ComputeTarget


def connectToAML(subId, resGrp, ws):
  try:
    #cli_auth = AzureCliAuthentication()

    #ws = Workspace(subscription_id = subId, resource_group = resGrp, workspace_name = ws, auth=cli_auth)
    ws = Workspace.get(name = ws, subscription_id = subId, resource_group = resGrp)
    print(f"### Connected to Azure ML workspace '{ws.name}'")
    return ws
  except:
    print('### ERROR: Unable to connect to workspace')
    return None


def downloadPickles(ws, modelName, outputPath="./pickles"):
  model = Model(ws, modelName)
  # These are special tags, lets us get back to the run that created the model 
  runId = model.tags['aml-runid']
  experimentName = model.tags['aml-experiment']

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


def createComputeAML(ws, name="amlcluster", nodesMin=0, nodesMax=3, vmSize="Standard_D3_v2"):
  # Azure ML compute configuration
  if name in ws.compute_targets:
      compute_target = ws.compute_targets[name]
      if compute_target and type(compute_target) is AmlCompute:
          print(f"### Found existing cluster '{name}' so will use it")
          return compute_target
  else:
      print(f"### Creating cluster '{name}' this could take time...")
      provisioning_config = AmlCompute.provisioning_configuration(vm_size = vmSize, min_nodes = nodesMin, max_nodes = nodesMax)

      # create the cluster
      compute_target = ComputeTarget.create(ws, name, provisioning_config)
      
      # can poll for a minimum number of nodes and for a specific timeout. 
      # if no min node count is provided it will use the scale settings for the cluster
      compute_target.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)
      
      # For a more detailed view of current AmlCompute status, use get_status()
      print(compute_target.get_status().serialize())
      return compute_target