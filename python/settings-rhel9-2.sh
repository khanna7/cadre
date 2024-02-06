module load python/3.11.0s-ixrhc3q
module load hpcx-mpi/4.1.5rc2s-yflad4v
module load r/4.3.1-lmofgb4
source /gpfs/data/akhann16/sfw/pyenvs/repast4py-py3.11/bin/activate

gcc -v #check that gcc/11 is loaded

export cadre_dt_output=$(realpath /gpfs/data/akhann16/akhann16/cadre_simulated_data/)
