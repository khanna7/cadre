#!/bin/bash

#SBATCH --mail-user=aditya_khanna@brown.edu  
#SBATCH --mail-type=ALL
#SBATCH -n 1
#SBATCH --mem=16G
#SBATCH -t 1:00:00

module load python/3.9.0

export PATH=/gpfs/home/akhann16/sfw/swift-t/stc/bin:$PATH
source /users/akhann16/code/cadre/python/new_cadre_env/bin/activate


python3 -m pycadre myparams/model_params.yaml
