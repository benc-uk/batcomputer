# Azure ARM Template - Deploy to ACI
Simple standard ARM template to deploy the model API to Azure Container Instances

### Template Parameters

```json
"acrName": {
  "value": "myACR"
},
"acrPassword": {
  "value": "change-me"
},
"modelVersion": {
  "value": "1"
},
"imageName": {
  "value": "foo/myimage"
},
"containerName": {
  "value": "democontainer"
} 
```

### Connectivity
The ACI instance will be deployed with a DNS prefix, and listen on port 8000

The DNS prefix will be parameterized based on the `containerName` and `modelVersion` provided when deploying the template. 

So the URL for the API will be of the form:
```http
http://{containerName}-{modelVersion}.{region}.azurecontainer.io:8000/api
```

The template deployment will provide this in an output value `apiEndpoint`