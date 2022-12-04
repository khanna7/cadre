#!/bin/bash

#SBATCH --mail-user=aditya_khanna@brown.edu  
#SBATCH --mail-type=ALL
#SBATCH -n 1
#SBATCH --mem=16G
#SBATCH -t 1:00:00

module load python/3.9.0
#source /users/akhann16/code/cadre/python/new_cadre_env/bin/activate
source /gpfs/home/akhann16/code/cadre/python/cadre_env_openmpi_4.0.5_gcc_10.2_slurm20/bin/activate  
python3 -m pycadre myparams/model_params.yaml
