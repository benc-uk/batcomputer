import pickle
import sklearn
import pprint

model = None
lookup = None
flags = None

def initialize(model_name, lookup_name, flags_name):
  global model, lookup, flags 

  pkl_loader = open(model_name, 'rb')
  model = pickle.load(pkl_loader)
  pkl_loader.close()

  pkl_loader = open(lookup_name, 'rb')
  lookup = pickle.load(pkl_loader)
  #pprint.pprint(lookup)
  pkl_loader.close()

  pkl_loader = open(flags_name, 'rb')
  flags = pickle.load(pkl_loader)
  #pprint.pprint(flags)
  pkl_loader.close()


def predict(request):
  print("### Prediction request for:", request)

  # Dynamically build params array from request and lookup table
  params = []
  for req_param in request:
    val = request[req_param]
    
    # If the key is pointing at a dict, then get mapped value
    if type(lookup[req_param]) == type(dict()):
      params.append(lookup[req_param][val])
    else:
      params.append(val)

  prediction = model.predict_proba([params]) 
  prediction_list = dict(zip(flags, prediction[0]))
  print("### Prediction result:", prediction_list)

  return prediction_list