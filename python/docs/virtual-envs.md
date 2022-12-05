# Set up a virtual environment

## Load needed modules

```
module load gcc/10.2
module load mpi/openmpi_4.0.5_gcc_10.2_slurm20 cuda/11.1.1
module load R/4.2.0 pcre2/10.35 intel/2020.2 texlive/2018
module load python/3.9.0
```

Check what has been loaded:

```
[akhann16@login005 ~]$ module list
java/8u111                          R/4.2.0                             
matlab/R2017b                       pcre2/10.35                         
gcc/10.2                            intel/2020.2                        
mpi/openmpi_4.0.5_gcc_10.2_slurm20  texlive/2018                        
cuda/11.1.1                         python/3.9.0                        
```
## Create new virtual environment

```
virtualenv cadre_env_openmpi_4.0.5_gcc_10.2_slurm20
```

## Activate the virtual environment

```
source cadre_env_openmpi_4.0.5_gcc_10.2_slurm20/bin/activate
```

## Install the requirements

```
env CC=mpicxx pip3 install -r requirements2.txt
```

Confirm that the mpi4py is installed:

```
(cadre_env_openmpi_4.0.5_gcc_10.2_slurm20) [akhann16@login005 python]$ env MPICC=/gpfs/runtime/opt/mpi/openmpi_4.0.5_gcc_10.2_slurm20/bin/mpicc pip3 install mpi4py
Requirement already satisfied: mpi4py in ./cadre_env_openmpi_4.0.5_gcc_10.2_slurm20/lib/python3.9/site-packages (3.1.3)
```
## Reinstall mpi4py
(cadre_env_openmpi_4.0.5_gcc_10.2_slurm20) [akhann16@login005 python]$ env MPICC=/gpfs/runtime/opt/mpi/openmpi_4.0.5_gcc_10.2_slurm20/bin/mpicc pip3 install mpi4py --force-reinstal
l


## Update requirements.txt when needed:

```
pip freeze > requirements.txt
```

** Remember to udpate the virtual environmnet activation path before submitting the jobscript **
