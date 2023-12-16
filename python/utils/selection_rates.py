import yaml

# Goal: generate selection rates into incarceration for race-sex-smoking-alcohol combinations

# Before these rates are being generated on-the-fly (cadre_person.py line 202) using the current run's population
# which looked at the current smoking/alcohol proportions and the current race-sex proportions

## Import model params:
model_params_path = "..//myparams/model_params.yaml"
with open(model_params_path) as f:
    params = yaml.load(f, Loader=yaml.FullLoader)
    R = params["PROBABILITY_DAILY_INCARCERATION"]
    gen_pop_race_distributions = params["RACE_DISTRIBUTION"]
    female_proportion = params["FEMALE_PROP"]
    I = params["INC_RACE_SEX_PROP"]
    incarceration_smoking_association = params["INCARCERATION_SMOKING_ASSOC"] # Ives, et al. 2022. “Nine Years of...” Preventive Medicine Reports 29 (October): 101921.
    incarceration_AUD_association = params["INCARCERATION_AUD_ASSOC"] # Fazel S, Yoon IA, Hayes AJ. Addiction. 2017 Oct;112(10):1725-1739. doi: 10.1111/add.13877.
f.close()

smoking_general_population = 0.1154314 # from 2021 NHIS data: https://rpubs.com/nwrousell/1075243
aud_general_population = 0.056

## Average smoking/AUD rates
incarceration_smoking= (incarceration_smoking_association["MIN"] + incarceration_smoking_association["MAX"])/2

# TODO - check for different rates (this is using AUD instead of the new parameterization)
incarceration_AUD = (incarceration_AUD_association["MALES"] + incarceration_AUD_association["FEMALES"])/2 


## Compute G for race-sex combos
# G x female_proportion
G = {}
for key in gen_pop_race_distributions:
    upper_key = key.upper()
    G[f"{upper_key}_FEMALE"] = gen_pop_race_distributions[key] * female_proportion
    G[f"{upper_key}_MALE"] = gen_pop_race_distributions[key] * (1 - female_proportion)

## Compute R_i values for race-sex combos
# R_i = R * (I_i / G_i)
race_sex_incarceration_multiplier = {}
for i in I:
    race_sex_incarceration_multiplier[i] = (I[i] / G[i])

## Compute smoking/alc multipliers
smoking_multiplier = incarceration_smoking / smoking_general_population
alc_multiplier = incarceration_AUD / aud_general_population

## Export to yaml
output_fname = "output.yaml"
d = {
    "SMOKING_INCARCERATION_MULTIPLIER": smoking_multiplier,
    "AUD_INCARCERATION_MULTIPLIER": alc_multiplier,
    "RACE_SEX_INCARCERATION_SELECTION_MULTIPLIER": race_sex_incarceration_multiplier
}
print(d) # sanity check
with open(output_fname, "w") as f:
    yaml.dump(d, f, )