# Batcomputer Helm Chart

Simple Helm chart to deploy the model API image from Azure Container Registry to Kubernetes, and expose using an Ignress

Make a copy of `values.sample.yaml` and name it something like `myvalues.yaml`

The values used by the chart are explained in the comments
Values that must be set are `registryPrefix`, `image` and `modelVersion`. If you built the image using the supplied Azure Pipeline then `image` will not need to change

```yaml
# Change to the name of your ACR instance
registryPrefix: changeme.azurecr.io/

# Leave blank if not using DNS with your ingress
# If you have enabled the HTTP routing add on you may set the DNS zone here
domainName: batcomputer.changeme.region.aksapp.io

# Change if not using AKS with HTTP routing add on, otherwise ignore
ingressClass: addon-http-application-routing

# Leave blank if you haven't set up cert-manager, and HTTPS will not be used
cmCertIssuer: 

# Model API settings, change image and modelVersion as required
api:
  image: batcomputer-model-api
  replicas: 1
  imagePullPolicy: Always
  modelVersion: 1
```

Deploy using Helm with a released called "demo"
```
cd kubernetes/helm
helm upgrade demo batcomputer -i -f myvalues.yaml
```
