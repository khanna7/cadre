import io;
import sys;
import files;
import string;
import python;
import launch;

string emews_root = getenv("EMEWS_PROJECT_ROOT");
string turbine_output = getenv("TURBINE_OUTPUT");
string site = getenv("SITE");
string param_file = argv("param_file");

//file model_sh = input(emews_root+"/scripts/run_p4m4py.sh");
file upf = input(argv("f"));

string run_pycadre_code = """
import pycadre.__main__
import turbine_helpers
import json

upf_line = '%s'
param_file = '%s'
output_directory = '%s'

param_json = json.loads(upf_line)
param_json['output.directory'] = output_directory

json_s = json.dumps(param_json)
comm = turbine_helpers.get_task_comm()
pycadre.__main__.run(comm, param_file, json_s)
""";

string create_json_param = """
import json

upf_line = '%s'
param_file = '%s'
derived_param_file = '%s'
output_directory = '%s'
r_ergm_file = '%s'
init_data_file = '%s'

param_json = json.loads(upf_line)
param_json['derived.parameters.file'] = derived_param_file
param_json['r.ergm.file'] = r_ergm_file
param_json['output.directory'] = output_directory
param_json['initial.data.file'] = init_data_file

json_s = json.dumps(param_json)
""";

// app function used to run the model
app (file out, file err) launch_model(string param_line, string instance)
{
    "bash" model_sh param_line emews_root instance param_file @stdout=out @stderr=err;
}

(string v) run_model(string upf_line, string instance) {
    // upf_line, param_file, derived_param_file, output_dir, r_ergm_file, init_data_file
    string output_dir = "%s/output" % instance;
    string code = run_pycadre_code % (upf_line, param_file, output_dir);
    v = @par=1 python_parallel_persist(code, "str(1)");
}

// (void v) run_model(string upf_line, string instance) {
//     // upf_line, param_file, derived_param_file, output_dir, r_ergm_file, init_data_file
//     string output_dir = "%s/output" % instance;
//     string code = create_json_param % (upf_line, param_file, derived_param_file, output_dir, 
//                                   r_ergm_file, init_data_file);
//     js = python_persist(code, "json_s");
//     file out <instance+"/out.txt">;
//     file err <instance+"/err.txt">;
//     (out, err) = launch_model(js, instance) =>
//     // need to quote the json string with single quotes
//     // string args[] = [ "'" + js + "'", emews_root, instance, param_file];
//     // string envs[] = [ ("SITE=%s" % site) ];
//     // @par=1 launch_envs(filename(model_sh), args, envs) =>
//     v = propagate();
// }

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
    // run_prerequisites() => {
    string upf_lines[] = file_lines(upf);
    foreach line ,i in upf_lines {
        string instance = "%s/instance_%i/" % (turbine_output, i + 1);
        make_dir(instance) => {
            run_model(line, instance);
        }
    }
    // }
}
