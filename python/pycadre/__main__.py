from pycadre import cadre_model 
#from pycadre.load_params import params_list
import pycadre.load_params



def main():
    params_list = pycadre.load_params.load_params()
    STOP_AT = params_list['STOP_AT']
    N = params_list['N_AGENTS']
    model = cadre_model.Model(n=N, verbose=True)
    model.run(MAXTIME=STOP_AT)
  
if __name__ == "__main__":
    main()
    
        