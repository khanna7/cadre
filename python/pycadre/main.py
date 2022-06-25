from pycadre import cadre_model 
import yaml

with open("myparams/model_params.yaml", mode="rt", encoding="utf-8") as file:
    params_list = yaml.safe_load(file)

stop_at = params_list['stop_at']
N = params_list['n_agents']

#print(params_list)

def main():
    model = cadre_model.Model(n=N, verbose=True)
    model.run(MAXTIME=stop_at)
  
if __name__ == "__main__":
    main()
    
        