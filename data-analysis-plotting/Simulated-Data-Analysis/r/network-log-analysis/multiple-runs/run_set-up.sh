#!/bin/bash

#SBATCH --job-name=network-setup        # Job name
#SBATCH --output=logs/result_%j.out          # Standard output and error log
#SBATCH --error=logs/error_%j.err            # Error log
#SBATCH --ntasks=1                      # Run on a single CPU
#SBATCH --mem=24gb                       # Job memory request
#SBATCH --time=02:00:00                 # Time limit hrs:min:sec
#SBATCH --mail-type=ALL
#SBATCH --mail-user=aditya_khanna@brown.edu

echo "Point 2"

# Create the log directory if it doesn't exist
mkdir -p logs

# Create rds-outs directory if it doesn't exist
mkdir -p rds-outs

echo "Point 3"
module load R/4.2.0                     # Load R module 
module load gcc/10.2 pcre2/10.35 intel/2020.2 texlive/2018

echo "Point 4"
cd /oscar/home/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/

echo "Point 5"
R CMD BATCH network-log-analysis/multiple-runs/set-up.R network-log-analysis/multiple-runs/logs/network-set-up_${SLURM_JOB_ID}.Rout

echo "Point 6"