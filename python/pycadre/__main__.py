from pycadre import cadre_model 
import pycadre.load_params
from mpi4py import MPI
from repast4py import parameters
import time

import cProfile


def main():
    parser = parameters.create_args_parser()    
    args = parser.parse_args() 

    params_list = pycadre.load_params.load_params(args.parameters_file, args.parameters)
    
    STOP_AT = params_list['STOP_AT']
    N = params_list['N_AGENTS']
    model = cadre_model.Model(params=params_list, comm=MPI.COMM_WORLD)
    #model.run(params=params_list)
    model.start()
  
if __name__ == "__main__":
    tic = time.perf_counter()
    main()
    toc = time.perf_counter()    
    print(f"Model ran in  {toc-tic:0.2f} seconds")
    
