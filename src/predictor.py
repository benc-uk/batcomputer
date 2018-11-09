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
  features = []

  # Dynamically build params array from request and lookup table
  # ORDER IS IMPORTANT! this is why we use OrderedDict

  # We assume lookup has been created in the correct order
  for lookup_key in lookup:
    val = request[lookup_key]
    # If the value is a string we need to map to number using the lookup
    if type(val) == type(str()):
      val = lookup[lookup_key][val]

    # Push features array IN ORDER
    features.append(val)

  prediction = model.predict_proba([features]) 
  prediction_list = dict(zip(flags, prediction[0]))
  print("### Prediction result:", prediction_list)

  return prediction_list