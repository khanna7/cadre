import os
import yaml
import itertools
import json  

# Read the YAML data
yaml_path = os.path.join(os.sep, 'oscar', 'home', 'akhann16', 'code', 'cadre', 'python', 'myparams', 'model_params.yaml')
with open(yaml_path, 'r') as f:
    base_data = yaml.safe_load(f)

# Extract the base values 
random_seed_base_val = base_data['random.seed']
original_smoking_onset = base_data['SMOKING_NETWORK_EFFECTS']['ONSET']['FIRST_DEGREE']
original_alcohol_onset = base_data['ALCOHOL_NETWORK_EFFECTS']['ONSET']['FIRST_DEGREE']

# Define the range for each parameter
random_seed_values = range(random_seed_base_val, random_seed_base_val+5)
smoking_onset_values = [original_smoking_onset + i*0.2 for i in range(-2, 3)] # Gives [-0.4, -0.2, 0, 0.2, 0.4] offsets
alcohol_onset_values = [original_alcohol_onset + i*0.2 for i in range(-2, 3)]

# Generate combinations
combinations = list(itertools.product(random_seed_values, smoking_onset_values, alcohol_onset_values))

# Write to UPF
with open('upf_output.txt', 'w') as upf:
    for combo in combinations:
        entry = {
            'random.seed': combo[0],
            'SMOKING_NETWORK_EFFECTS': {'ONSET': {'FIRST_DEGREE': combo[1]}},
            'ALCOHOL_NETWORK_EFFECTS': {'ONSET': {'FIRST_DEGREE': combo[2]}}
        }
        upf.write(json.dumps(entry) + '\n')  # Convert dictionary to string before writing

print("UPF generated.")
