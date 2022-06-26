import yaml

with open("myparams/model_params.yaml", mode="rt", encoding="utf-8") as file:
    params_list = yaml.safe_load(file)
