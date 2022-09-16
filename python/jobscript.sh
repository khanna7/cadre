#!/bin/bash

#SBATCH -n 1
#SBATCH --mem=16G
#SBATCH -t 1:00:00

python3 pycadre myparams/model_params.yaml
