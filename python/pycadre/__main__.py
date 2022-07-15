from pycadre import cadre_model 
import pycadre.load_params
import cProfile


def main():

    params_list = pycadre.load_params.load_params()
    STOP_AT = params_list['STOP_AT']
    N = params_list['N_AGENTS']
    model = cadre_model.Model(n=N, verbose=True)
    model.run(MAXTIME=STOP_AT, params=params_list)
  
if __name__ == "__main__":
    main()
    
