from pycadre import cadre_model 
import pycadre.load_params
from mpi4py import MPI
import cProfile


def main():
    
    size = MPI.COMM_WORLD.Get_size()    
    rank = MPI.COMM_WORLD.Get_rank()

    params_list = pycadre.load_params.load_params('../../cadre/python/myparams/model_params.yaml', '')
    STOP_AT = params_list['STOP_AT']
    N = params_list['N_AGENTS']
    model = cadre_model.Model(n=N, verbose=True, comm=MPI.COMM_WORLD)
    model.run(MAXTIME=STOP_AT, params=params_list)
  
if __name__ == "__main__":
    main()
    
