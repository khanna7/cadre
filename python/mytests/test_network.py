import unittest
import random
from mpi4py import MPI
from pycadre import cadre_network
from pycadre.person_creator import init_person_creator
from pycadre import load_params


class TestNetwork(unittest.TestCase):
    params_list = load_params.load_params(
        "../../cadre/python/test_data/test_params.yaml", ""
    )

    def test_mean_degree(self):
        n_agents = self.params_list['N_AGENTS']
        target_mean_degree = self.params_list['TARGET_MEAN_DEGREE']
        comm = MPI.COMM_WORLD

        # Create and initialize the network
        network = cadre_network.ErdosReyniNetwork(comm, n_agents, target_mean_degree)
        network.init_network(n_agents)

        # Calculate the mean degree
        mean_degree = network.mean_degree()

        # Test if the mean degree is approximately equal to the target_mean_degree
        self.assertAlmostEqual(mean_degree, target_mean_degree, delta=0.1)
        
    def test_create_new_edges(self):
        network = cadre_network.ErdosReyniNetwork(MPI.COMM_WORLD, 
                                                  self.params_list['N_AGENTS'], 
                                                  self.params_list['TARGET_MEAN_DEGREE'])
        network.init_network(self.params_list['N_AGENTS'])
        person_creator = init_person_creator()
        for i in range(self.params_list['N_AGENTS']):
            all_agents = network.get_agents()
            network.remove_agent(random.choice(all_agents))
            new_agent = person_creator.create_person()
            network.add(new_agent)
        self.assertAlmostEqual(network.get_num_edges(), (self.params_list['N_AGENTS']*self.params_list['TARGET_MEAN_DEGREE'])/2, delta=10)
