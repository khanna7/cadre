# EMEWS Instructions from PYCADRE model

## Installing EMEWS:
- See [here](https://emews.github.io) for general instructions from the EMEWS dev team.  

- See instructions [here](https://github.com/khanna-lab/alc-smoking-transition-use/blob/main/misc/oscar_setup.md) from Noah on installing EMEWS on OSCAR.

## Reference for general repast4py model from Nick

[Here](https://github.com/khanna-lab/cadre/blob/master/python/docs/emews_instructions.md)

## My Working Setup

- The EMEWS root has been moved in the project [directory](https://github.com/khanna-lab/cadre/tree/network-analysis/emews).

- The module set-up is explained [here](https://github.com/khanna-lab/cadre/blob/network-analysis/python/docs/mpi-and-virtualenvs.md).

### Filetree

The EMEWS project root contains the following files:

<img width="272" alt="Screen Shot 2023-02-07 at 1 56 30 PM" src="https://user-images.githubusercontent.com/8194564/217339644-5bc4fdf5-b883-4846-aa7e-a6e6fb61ab4b.png">



### To run the model using EMEWS

```
source envs/oscar_env.sh
cd swift
./run_pytest.sh testY cfgs/pycadre.cfg
```


💡 If swift-t cannot be found, it probably means `oscar_env.sh` has not been sourced.

💡💡 Do not submit the jobs in an interactive session on Oscar. Submit them through the login node. Jobs submitting through an interactive session produce strange errors:

```srun: fatal: SLURM_MEM_PER_CPU, SLURM_MEM_PER_GPU, and SLURM_MEM_PER_NODE are mutually exclusive.```




Only one "source" per login is needed. Replace testY with an experiment id (e.g., "t1").

The swift-t directory will look like:
 

```bash
drwxr-xr-x 2 akhann16 akhann16 4096 Jan 24 14:07 cfgs
-rw-r--r-- 1 akhann16 akhann16 1379 Jan 27 12:01 pytest.swift
-rwxr-xr-x 1 akhann16 akhann16 3409 Jan 27 13:23 run_pytest.sh
lrwxrwxrwx 1 akhann16 akhann16   71 Jan 27 14:38 turbine-output -> /gpfs/home/akhann16/code/cadre/python/docs/emews_test/experiments/testY
```

The `turbine-output -> /oscar/home/akhann16/code/cadre/emews/experiments/testY` provides the path to the location of the simulated data folder. This should be checked for the `instance` directories, and for any errors in the `instance` directories.

### Set up files

1) In file [run_pycadre.sh](https://github.com/khanna-lab/cadre/blob/74a45608342f5e7e090cbe6671d62d3b15a6416f/python/docs/emews_test/scripts/run_model_pycadre.sh), 

- Update [lines](https://github.com/khanna-lab/cadre/blob/74a45608342f5e7e090cbe6671d62d3b15a6416f/python/docs/emews_test/scripts/run_model_pycadre.sh#L35-L38) with the Python and `venv` information:

```bash
module load python/3.9.0
source /gpfs/home/akhann16/code/cadre/python/new_cadre_env_4/bin/activate
```

- Update [arg_array](https://github.com/khanna-lab/cadre/blob/c1915e1c8a9ed3329c81ea54d517135333b0ad8a/python/docs/emews_test/scripts/run_model_pycadre.sh#L58) with the command to execute the model.

2) In file [swift/cfgs/pycadre.cfg](https://github.com/khanna-lab/cadre/blob/master/python/docs/emews_test/swift/cfgs/pycadre.cfg), 

- Specify the [path](https://github.com/khanna-lab/cadre/blob/c1915e1c8a9ed3329c81ea54d517135333b0ad8a/python/docs/emews_test/swift/cfgs/pycadre.cfg#L9) to  the unrolloed parameter file (UPF)
- Specify the path of the [parameters YAML](https://github.com/khanna-lab/cadre/blob/c1915e1c8a9ed3329c81ea54d517135333b0ad8a/python/docs/emews_test/swift/cfgs/pycadre.cfg#L10)
- Change job run parameters above as needed:
    
    ```bash
    CFG_WALLTIME=00:05:00
    CFG_QUEUE=batch
    CFG_PROJECT=akhann16
    NODES=1
    CFG_PPN=5
    ```
    

3) In the [job submission script](https://github.com/khanna-lab/cadre/blob/master/python/docs/emews_test/swift/run_pytest.sh), specify:

- The [location](https://github.com/khanna-lab/cadre/blob/c1915e1c8a9ed3329c81ea54d517135333b0ad8a/python/docs/emews_test/swift/run_pytest.sh#L58) of the site packages
    
    
    💡 This should point to the site packages directory in the virtual environment.
    
    
    
- The [PYTHONPATH](https://github.com/khanna-lab/cadre/blob/c1915e1c8a9ed3329c81ea54d517135333b0ad8a/python/docs/emews_test/swift/run_pytest.sh#L59) variable:
    
    
    💡 Note that this should contain the path to the `pycadre` module. A module is defined as a python file, or a directory containing the `__init__.py` file.  In this case, the name path ends at `:/gpfs/home/akhann16/code/cadre/python:`because the `pycadre/__init__.py` is found at this location.
    
   
### Generating a UPF
    
    Example from Jonathan
    
    ```bash
    > dta <- data.table(param1 = c(1,2,3), param2 = c("hi","there", "ak"))
    > dta
       param1 param2
    1:      1     hi
    2:      2  there
    3:      3     ak
    > jsonlite::stream_out(dta)
    {"param1":1,"param2":"hi"}
    {"param1":2,"param2":"there"}
    {"param1":3,"param2":"ak"}
    ```
    
    [https://cche-group.slack.com/archives/D9K0E293J/p1674860539271499](https://cche-group.slack.com/archives/D9K0E293J/p1674860539271499)
    
    
