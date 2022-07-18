from repast4py import parameters
params_list = None

def load_params (filename, parameters_string):
    parser = parameters.create_args_parser()    
    args = parser.parse_args() 

    global params_list        
    params_list = parameters.init_params(filename, parameters_string)
    
    return params_list
