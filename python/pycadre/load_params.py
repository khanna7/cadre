import yaml

params_list = None

def load_params ():
  global params_list
  with open("myparams/model_params.yaml", mode="rt", encoding="utf-8") as file:
      params_list = yaml.safe_load(file)
  return params_list
