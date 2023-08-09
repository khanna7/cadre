import yaml
import json

# Read the YAML data
with open('/oscar/home/akhann16/code/cadre/python/myparams/model_params.yaml', 'r') as f:
    base_data = yaml.safe_load(f)

# Define the variations for UPF
  ## stop_at_values = [100, 200, 300]
  ## n_agents_values = [500, 1000]

# Define variations for FIRST_DEGREE onset in smoking and alcohol
original_smoking_onset = base_data['SMOKING_NETWORK_EFFECTS']['ONSET']['FIRST_DEGREE']
original_alcohol_onset = base_data['ALCOHOL_NETWORK_EFFECTS']['ONSET']['FIRST_DEGREE']

smoking_onset_values = [original_smoking_onset - 0.4, original_smoking_onset - 0.2, original_smoking_onset, original_smoking_onset + 0.2, original_smoking_onset + 0.4]
alcohol_onset_values = [original_alcohol_onset - 0.4, original_alcohol_onset - 0.2, original_alcohol_onset, original_alcohol_onset + 0.2, original_alcohol_onset + 0.4]

# Generate UPF file
with open('upf_output.txt', 'w') as upf:
    for smoking_onset in smoking_onset_values:
        for alcohol_onset in alcohol_onset_values:
            upf_entry = {
                'SMOKING_NETWORK_EFFECTS': {
                    'ONSET': {'FIRST_DEGREE': smoking_onset}
                },
                'ALCOHOL_NETWORK_EFFECTS': {
                    'ONSET': {'FIRST_DEGREE': alcohol_onset}
                }
            }
            upf.write(json.dumps(upf_entry) + '\n')

print("UPF generated.")
