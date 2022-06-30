from pycadre import cadre_model 
from pycadre.load_params import params_list

STOP_AT = params_list['STOP_AT']
N = params_list['N_AGENTS']

def main():
    model = cadre_model.Model(n=N, verbose=True)
    model.run(MAXTIME=STOP_AT)
  
if __name__ == "__main__":
    main()
    
        