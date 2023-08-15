import networkx as nx
from repast4py import network, context as ctx, random
from pycadre.person_creator import init_person_creator


class ErdosReyniNetwork:
    def __init__(self, comm, n_agents, target_mean_degree):
        self.comm = comm
        self.context = ctx.SharedContext(self.comm)
        self.rank = self.comm.Get_rank()
        #self.edge_prob = edge_prob
        self.n_agents = n_agents
        self.target_mean_degree = target_mean_degree
        self.edge_prob = self.calculate_edge_prob(n_agents, target_mean_degree)

    def calculate_edge_prob(self, n_agents, target_mean_degree):
        edge_prob = target_mean_degree / (n_agents-1)
        return edge_prob
    
    def mean_degree(self):
        total_degrees = sum([degree for _, degree in self.network.graph.degree()])
        num_nodes = self.get_num_agents()
        return total_degrees / num_nodes

    def init_network(self, n_agents):
        network_init = nx.erdos_renyi_graph(n_agents, self.edge_prob)
        self.network = network.UndirectedSharedNetwork("erdos_renyi_network", self.comm)
        self.context.add_projection(self.network)
        persons = []
        for node in network_init.nodes:
            person = init_person_creator().create_person(tick=0)
            persons.append(person)
            self.add_without_edges(person)
        for edge in network_init.edges:
            self.network.add_edge(persons[edge[0]], persons[edge[1]])

    def add(self, agent):
        self.add_without_edges(agent)
        self.form_new_edges(agent)

    def add_without_edges(self, agent):
        self.context.add(agent)
        agent.graph = self.network.graph

    def add_edge(self, agent1, agent2):
        self.network.add_edge(agent1, agent2)

    def remove_agent(self, agent):
        self.context.remove(agent)

    def get_agents(self):
        return list(self.context.agents())

    def get_num_agents(self):
        return self.context.size()[-1]

    def get_neighbors(self, node):
        return list(self.network.graph.neighbors(node))
        
    def get_edges(self):
        return self.network.graph.edges

    def get_num_edges(self):
        return self.network.edge_count

    def form_new_edges(self, new_agent):
        all_agents = self.get_agents()
        for agent in all_agents:
            if agent is new_agent:
                continue
            if random.default_rng.binomial(1, self.edge_prob):
                self.add_edge(new_agent, agent)
