import networkx as nx
import numpy as np
from repast4py import network, context as ctx
from pycadre.person_creator import init_person_creator


class ErdosReyniNetwork:
    def __init__(self, comm, edge_prob):
        self.comm = comm
        self.context = ctx.SharedContext(comm)
        self.rank = comm.Get_rank()
        self.person_creator = init_person_creator()
        self.edge_prob = edge_prob

    def init_network(self, n_agents):
        network_init = nx.erdos_renyi_graph(n_agents, self.edge_prob)
        self.network = network.UndirectedSharedNetwork("erdos_renyi_network", self.comm)
        self.context.add_projection(self.network)
        persons = []
        for node in network_init.nodes:
            person = self.person_creator.create_person(tick=0)
            persons.append(person)
            self.add_without_edges(person)
        for edge in network_init.edges:
            self.network.add_edge(persons[edge[0]], persons[edge[1]])

    def step(self, tick):
        for p in self.get_agents():
            if p.exit_of_age(tick):
                self.remove_agent(p)
                new = self.person_creator.create_person(tick=tick)
                self.add(new)

    def add(self, agent):
        self.add_without_edges(agent)
        self.form_new_edges(agent)

    def add_without_edges(self, agent):
        self.context.add(agent)

    def add_edge(self, agent1, agent2):
        self.network.add_edge(agent1, agent2)

    def remove_agent(self, agent):
        self.context.remove(agent)

    def get_agents(self):
        return list(self.context.agents())

    def get_num_agents(self):
        return self.context.size()[-1]

    def get_edges(self):
        return self.network.graph.edges

    def get_num_edges(self):
        return self.network.edge_count

    def form_new_edges(self, new_agent):
        all_agents = self.get_agents()
        for agent in all_agents:
            if agent is new_agent:
                continue
            if np.random.binomial(1, self.edge_prob):
                self.add_edge(new_agent, agent)
