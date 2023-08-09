# Oscar EMEWS Test Project #

Example code for running a parameter sweep of repast4py model
using Oscar. The example runs 3 instances of the repast4py Zombies model
with different numbers of zombies as specified by a upf file.

## Files ##

* data/upf.txt - sample upf file
* envs/oscar_env.sh - environment file for Oscar

```bash
module load gcc/10.2
module load mpi/mvapich2-2.3.5_gcc_10.2_slurm22 cuda/11.7.1
module load R/4.2.0
module load python/3.9.0

export PATH=/gpfs/data/akhann16/sfw/tcl-8.6.12/bin:/gpfs/data/akhann16/sfw/apache-ant-1.10.12/bin:$PATH
export R_LIBS_USER=/gpfs/data/akhann16/sfw/rlibs/4.2.0
export PATH=/gpfs/data/akhann16/sfw/swift-t/gcc-10.2/mvapich-2.3.5/12022022/stc/bin:$PATH
```

* scripts/run_model.sh - script to launch individual model runs, i.e., calls `python3 model.py ...`
* swift/run_pytest.sh - swift job submission script, submits the job to the Oscar scheduler using swift.
* swift/pytest.swift - swift file that iterates through the upf, calling `scripts/run_model.sh` passing a row from the upf.
* swift/cfgs/pytest.cfg - configuration file for the job submission, set the walltime etc. with this.

```bash
CFG_WALLTIME=00:05:00
CFG_QUEUE=batch
# I think this is ignored
CFG_PROJECT=akhann16
NODES=1
CFG_PPN=32
CFG_PROCS=$(( NODES * CFG_PPN ))
# TODO: Update with path to upf file, relative
# to emews project root directory.
CFG_UPF=data/upf.txt
CFG_PARAM_FILE=/gpfs/data/akhann16/ncollie1/src/r4py_examples/zombies/zombie_model.yaml
```

## Running ##

```bash
source envs/oscar_env.sh
cd swift
./run_pytest.sh <exp_id> cfgs/pycadre.cfg
```

Note that you only need to do the "source" once per login, and 
replace <exp_id> with an experiment id (e.g., "t1").

## Adapting for a Different Model ##

To adapt the example for a different repast4py model

1. Edit `scripts/run_model.sh` as follows:

  * lines 36 - 37: Update with your python and virtual environment
  * line 50: Update with the location of your model file

2. Edit `swift/cfgs/pytest.cfg`

  * Update walltime, nodes, PPN as appropriate
  * Update CFG_UPF to upf file location
  * Update CFG_PARAM_FILE to the location of your parameter file. Note that this is copied into the experiment directory and that copy
    is used to run the model.



