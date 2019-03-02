import os
import azureml
from azureml.core import Workspace
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.compute import AmlCompute, ComputeTarget


def connectToAzureML(subId, resGrp, ws):
  try:
    cli_auth = AzureCliAuthentication()

    ws = Workspace(subscription_id = subId, resource_group = resGrp, workspace_name = ws)
    print('### Connected to Azure ML workspace:', ws.name)
    return ws
  except:
    print('### ERROR: Unable to connect to workspace')
    return None


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