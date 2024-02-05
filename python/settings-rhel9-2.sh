module load openmpi/4.1.2-s5wtoqb  
module load gcc
gcc -v #check that gcc/11 is loaded

module load r/4.3.1-lmofgb4


module load  python/3.11.0s-ixrhc3q

export cadre_dt_output=$(realpath /gpfs/data/akhann16/akhann16/cadre_simulated_data/)
