from statistics import mean as mean
import unittest
import numpy as np
import pandas as pd
from pycadre import cadre_model
import pycadre.load_params
from mpi4py import MPI
from repast4py import context as ctx


class TestModel(unittest.TestCase):
    params_list = pycadre.load_params.load_params(
        "../../cadre/python/test_data/test_params.yaml", ""
    )

    def test_edge_formation(self):

        """Test edge formation for newly entering agents
        set edge probability = 1 (done in test parameters)
        and check that all newly entering agents are forming ties with everyone
        """

        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=TestModel.params_list)
        model.start()

        if model.n_entries > 0:
            for key in model.new_agent_ties_dict.keys():
                value = model.new_agent_ties_dict[key]
                for i in range(model.n_entries):
                    self.assertEqual(value[i], 1)

            # print("New agent tie matrix is: ", model.new_agent_ties_dict.values(), "\n")


if __name__ == "__main__":
    unittest.main()
