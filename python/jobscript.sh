#!/bin/bash

#SBATCH --mail-user=aditya_khanna@brown.edu  
#SBATCH --mail-type=ALL
#SBATCH -n 1
#SBATCH --mem=16G
#SBATCH -t 00:10:00
#SBATCH -o slurm_output/job_%j.out
#SBATCH -e slurm_output/job_%j.err

source settings-rhel9-2.sh
module list

python3 -m pycadre myparams/model_params.yaml
    