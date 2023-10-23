#!/bin/bash

#SBATCH --mail-user=aditya_khanna@brown.edu  
#SBATCH --mail-type=ALL
#SBATCH -n 1
#SBATCH --mem=16G
#SBATCH -t 10:30:00
#SBATCH -o slurm_output/job_%j.out
#SBATCH -e slurm_output/job_%j.err

source settings.sh
module list
ldd new_cadre_env_4/lib/python3.9/site-packages/mpi4py/MPI.cpython-39-x86_64-linux-gnu.so 
source new_cadre_env_4/bin/activate
python -m pycadre myparams/model_params.yaml
    