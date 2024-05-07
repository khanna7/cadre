import os
import unittest
import random
from mpi4py import MPI

from pycadre import cadre_network
from pycadre.person_creator import init_person_creator
from pycadre import load_params


print("Current network test class working directory:", os.getcwd())

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.params_list = load_params.load_params(
            "test_data/test_params.yaml", ""
        )

    def test_mean_degree(self):
        n_agents = self.params_list["N_AGENTS"]
        target_mean_degree = self.params_list["TARGET_MEAN_DEGREE"]
        comm = MPI.COMM_WORLD

        # Create and initialize the network
        network = cadre_network.ErdosReyniNetwork(
            comm, n_agents, target_mean_degree
        )
        network.init_network(n_agents)

        # Calculate the mean degree
        mean_degree = network.mean_degree()

        print()
        print("Target mean degree is ..", target_mean_degree, "\n")
        print("Generated mean degree is ..", mean_degree, "\n")

        # Test if the mean degree is approximately equal to the target_mean_degree
        self.assertAlmostEqual(mean_degree, target_mean_degree, delta=0.2)

    def test_create_new_edges(self):
        network = cadre_network.ErdosReyniNetwork(
            MPI.COMM_WORLD,
            self.params_list["N_AGENTS"],
            self.params_list["TARGET_MEAN_DEGREE"],
        )
        network.init_network(self.params_list["N_AGENTS"])
        person_creator = init_person_creator()
        N_start = network.get_num_edges()
        for i in range(self.params_list["N_AGENTS"]):
            all_agents = network.get_agents()
            network.remove_agent(random.choice(all_agents))
            new_agent = person_creator.create_person()
            network.add(new_agent)

        N_end = network.get_num_edges()
        end_to_start = N_end / N_start
        expected = (
            self.params_list["N_AGENTS"]
            * self.params_list["TARGET_MEAN_DEGREE"]
            / 2
        )
        self.assertAlmostEqual(end_to_start, 1.0, delta=0.1)
        end_to_expected = N_end / expected
        self.assertAlmostEqual(end_to_expected, 1.0, delta=0.1)
