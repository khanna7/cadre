import yaml

with open("model_params.yaml", mode="rt", encoding="utf-8") as file:
    params_list = yaml.safe_load(file)

print(params_list)
print(type(params_list))

print(params_list['stop_at'])
print(params_list['RACE_CATS'])
print(params_list['SMOKING_PREV'])
print(params_list['FEMALE_PROP'])
