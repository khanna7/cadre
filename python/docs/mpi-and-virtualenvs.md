# Set up a virtual environment

## Load needed modules

```
module load gcc/10.2
module load mpi/mvapich2-2.3.5_gcc_10.2_slurm22 cuda/11.7.1
module load R/4.2.0 pcre2/10.35 intel/2020.2 texlive/2018
module load python/3.9.0                            
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
