from pycadre import cadre_model 
from pycadre.load_params import params_list

stop_at = params_list['stop_at']
N = params_list['n_agents']

def main():
    model = cadre_model.Model(n=N, verbose=True)
    model.run(MAXTIME=stop_at)
  
if __name__ == "__main__":
    main()
    
        