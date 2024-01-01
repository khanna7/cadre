#!/bin/bash

#SBATCH --job-name=agent-setup        # Job name
#SBATCH --output=logs/result_%j.out          # Standard output and error log
#SBATCH --error=logs/error_%j.err            # Error log
#SBATCH --ntasks=1                      # Run on a single CPU
#SBATCH --mem=24gb                       # Job memory request
#SBATCH --time=02:00:00                 # Time limit hrs:min:sec

# Create the log directory if it doesn't exist
mkdir -p logs

# Create rds-outs directory if it doesn't exist
mkdir -p rds-outs

module load R/4.2.0                     # Load R module 

cd /oscar/home/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/

R CMD BATCH agent-log-analysis/multiple-runs/set-up.R agent-log-analysis/multiple-runs/logs/agent-set-up_${SLURM_JOB_ID}.Rout
