import yaml

# Read the YAML data
with open('/oscar/home/akhann16/code/cadre/python/myparams/model_params.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Define the variations for UPF
stop_at_values = [100, 200, 300]
n_agents_values = [500, 1000]

# Generate UPF file
with open('upf_output.txt', 'w') as upf:
    for stop_at in stop_at_values:
        for n_agents in n_agents_values:
            upf_entry = {
                'STOP_AT': stop_at,
                'N_AGENTS': n_agents
            }
            upf.write(str(upf_entry) + '\n')

print("UPF generated.")
