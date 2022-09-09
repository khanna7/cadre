import networkx as nx
import yaml
from repast4py import network
from repast4py.network import write_network

# Read YAML params file
with open("myparams/model_params.yaml", 'r') as stream:
    params = yaml.safe_load(stream)

n_agents = params['N_AGENTS']
fpath = params['network_file']
edge_prob = params['EDGE_PROB']
network_init = nx.erdos_renyi_graph(n_agents, edge_prob)
print(network_init)
write_network(graph=network_init, network_name='network_init', fpath=fpath, n_ranks=1)
