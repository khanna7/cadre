# Set up a virtual environment

## Load needed modules

```
module load python/3.11.0s-ixrhc3q
module load openmpi/4.1.2-s5wtoqb
module load r/4.3.1-lmofgb4

MPI_LIB="/oscar/rt/9.2/software/0.20-generic/0.20.1/opt/spack/linux-rhel9-x86_64_v3/gcc-11.3.1/openmpi-4.1.2-s5wtoqbqirz4ivubo6uzp2ndglheablu/lib"
export LD_LIBRARY_PATH=$MPI_LIB:$LD_LIBRARY_PATH
                        
```

Updated [settings.sh](https://github.com/khanna-lab/cadre/commit/3f7ee2b12e99b6bd446738179f935e7d2167dd9d)

Check what has been loaded:

```
[akhann16@login005 python]$ module list
java/8u111                           R/4.2.0                              
matlab/R2017b                        pcre2/10.35                          
gcc/10.2                             intel/2020.2                         
mpi/mvapich2-2.3.5_gcc_10.2_slurm22  texlive/2018                         
cuda/11.7.1                          python/3.9.0                         
[akhann16@login005 python]$                        
```

## Create new virtual environment

```
virtualenv new_cadre_env_3
```

## Activate the virtual environment

```
source new_cadre_env_3/bin/activate
```

## Reinstall mpi4py (if needed)

```
pip3 install --no-cache-dir mpi4py
```

(The `--no-cache-dir` is to make sure that the mpi isn't installed just from the cache.)

## To check if the mpi4py is compiled using the correct module:

```
ldd  <your venv directory>/lib/python3.9/site-packages/mpi4py/MPI.cpython-39-x86_64-linux-gnu.so
```

## Install repast4py

```
 env CC=mpicxx pip3 install repast4py
```

This ensures that repast4py is installed from pypi.

To install from requirements, 


```
 env CC=mpicxx pip3 install -r requirements.txt 
```

## Update requirements.txt when needed:

```
pip freeze > requirements.txt
```

** Remember to udpate the virtual environmnet activation path before submitting the jobscript **
