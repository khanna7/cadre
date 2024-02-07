import io;
import sys;
import files;
import string;
import emews;
import python;

string emews_root = getenv("EMEWS_PROJECT_ROOT");
string turbine_output = getenv("TURBINE_OUTPUT");

#file model_sh = input(emews_root+"/scripts/run_model_pytest.sh");
file model_sh = input(emews_root+"/scripts/run_model_pycadre.sh");
file upf = input(argv("f"));
string param_file = argv("param_file");

string run_pycadre_code = """
import pycadre.__main__
import turbine_helpers
import json
import os

upf_line = '%s'
param_file = '%s'
instance_directory = '%s'

print(f'STARTING: {upf_line}', flush=True)
os.chdir(instance_directory)

# json_s = json.dumps(param_json)

comm = turbine_helpers.get_task_comm()
pycadre.__main__.main(comm, param_file, upf_line)
print(f'END: {upf_line}', flush=True)
""";


(string v) run_model(string upf_line, string instance) {
    // upf_line, param_file, derived_param_file, output_dir, r_ergm_file, init_data_file
    // string instance_dir = "%s/output" % instance;
    string code = run_pycadre_code % (upf_line, param_file, instance);
    v = @par=1 python_parallel_persist(code, "str(1)");
}



// app function used to run the model
// app (file out, file err) run_model(file shfile, string param_line, string instance)
//{
     // "mpiexec" "-n" 1 "-launcher" "fork" "bash" shfile param_line emews_root instance param_file @stdout=out @stderr=err;
//}


// call this to create any required directories
app (void o) make_dir(string dirname) {
    "mkdir" "-p" dirname;
}




// Anything that needs to be done prior to a model
// run (e.g. file creation) should be done within this
// function.
// app (void o) run_prerequisites() {
//
// }

// Iterate over each line in the upf file, passing each line 
// to the model script to run
main() {
    printf("hello");
    string upf_lines[] = file_lines(upf);
    foreach s,i in upf_lines {
        string instance = "%s/instance_%i/" % (turbine_output, i+1);
        make_dir(instance) => {
           // file out <instance+"out.txt">;
           // file err <instance+"err.txt">;
           // (out,err) = run_model(model_sh, s, instance);
	   run_model(s, instance);
        }
    }
}
