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



def predict(req): #force_name, crime, group, subgroup):
  force_name_num = lookup['force_name'][req['force_name']]
  crime_num = lookup['offence_description'][req['offence_description']]
  group_num = lookup['offence_subgroup'][req['offence_subgroup']]
  subgroup_num = lookup['office_group'][req['office_group']]

  prediction = model.predict_proba([[force_name_num, crime_num, group_num, subgroup_num]])
  prediction_list = dict(zip(flags, prediction[0]))

  return prediction_list