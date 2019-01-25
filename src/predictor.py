import pickle
import sklearn
import pprint

class Predictor:
  model = None
  lookup = None
  flags = None

  #
  # Load pickles 
  #
  def __init__(self, model_name, lookup_name, flags_name):
    # Load model and sanity check it's what we expect
    with open(model_name, 'rb') as pickle_file:
      self.model = pickle.load(pickle_file)
      if not str(type(self.model).__module__).startswith("sklearn."):
        print("### !ERROR: {} is not a sklearn object".format(model_name))
        exit()

    # Load lookup table and sanity check it's what we expect
    with open(lookup_name, 'rb') as pickle_file:
      self.lookup = pickle.load(pickle_file)
      if not str(type(self.lookup).__name__).startswith("OrderedDict"):
        print("### !ERROR: {} is not a OrderedDict object".format(lookup_name))
        exit()

    # Load flags and sanity check it's what we expect
    with open(flags_name, 'rb') as pickle_file:
      self.flags = pickle.load(pickle_file)
      if not str(type(self.flags).__name__).startswith("list"):
        print("### !ERROR: {} is not a list object".format(flags_name))
        exit()

  #
  # Call the scoring/prediction function
  #
  def predict(self, request):
    print("### Prediction request for:", request)
    features = []

    # Dynamically build params array from request and lookup table
    # ORDER IS IMPORTANT! this is why we use OrderedDict

    # We assume lookup has been created in the correct order
    for lookup_key in self.lookup:
      val = request[lookup_key]
      # If the value is a string we need to map to number using the lookup
      if type(val) == type(str()):
        val = self.lookup[lookup_key][val]

      # Push features array IN ORDER
      features.append(val)

    # This is where it all happens
    prediction = self.model.predict_proba([features]) 
    prediction_list = dict(zip(self.flags, prediction[0]))
    print("### Prediction result:", prediction_list)

    return prediction_list
