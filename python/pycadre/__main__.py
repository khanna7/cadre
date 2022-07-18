from pycadre import cadre_model 
import pycadre.load_params
from mpi4py import MPI
from repast4py import parameters
import cProfile


def main():

    parser = parameters.create_args_parser()    
    args = parser.parse_args() 

    params_list = pycadre.load_params.load_params(args.parameters_file, args.parameters)
    
    STOP_AT = params_list['STOP_AT']
    N = params_list['N_AGENTS']
    model = cadre_model.Model(n=N, verbose=True, comm=MPI.COMM_WORLD)
    model.run(MAXTIME=STOP_AT, params=params_list)
  
if __name__ == "__main__":
    main()
    
