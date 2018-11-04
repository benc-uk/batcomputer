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
  # Dynamically build params from request and lookup table
  params = []
  for param in request:
    val = request[param]
    params.append(lookup[param][val])

  prediction = model.predict_proba([params]) 
  prediction_list = dict(zip(flags, prediction[0]))
  print("### Prediction result:", prediction_list)

  return prediction_list