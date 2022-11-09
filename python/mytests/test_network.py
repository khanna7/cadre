import unittest
import random
from mpi4py import MPI
from pycadre import cadre_network
from pycadre import cadre_person
from pycadre import cadre_model
from pycadre.person_creator import init_person_creator
import pycadre


class TestNetwork(unittest.TestCase):
    params_list = pycadre.load_params.load_params(
        "../../cadre/python/test_data/test_params.yaml", ""
    )

    def test_create_new_edges(self):
        network = cadre_network.ErdosReyniNetwork(MPI.COMM_WORLD, 10000, 0.001, 25)
        person_creator = init_person_creator(0)
        for i in range(10000):
            all_agents = network.get_agents()
            network.remove_agent(random.choice(all_agents))
            new_agent = person_creator.create_person()
            network.add(new_agent)
        self.assertAlmostEqual(network.get_num_edges(), 50000, delta=1000)
