module load python/3.11.0s-ixrhc3q
module load hpcx-mpi/4.1.5rc2s-yflad4v
module load r/4.3.1-lmofgb4
source /gpfs/data/akhann16/sfw/pyenvs/repast4py-py3.11/bin/activate

gcc -v #check that gcc/11 is loaded

#module load gcc/10.2
#module load mpi/mvapich2-2.3.5_gcc_10.2_slurm22 cuda/11.7.1
#module load R/4.2.0
#module load python/3.9.0

export PATH=/gpfs/data/akhann16/sfw/tcl-8.6.12/bin:/gpfs/data/akhann16/sfw/apache-ant-1.10.12/bin:$PATH
export R_LIBS_USER=/gpfs/data/akhann16/sfw/rlibs/4.3.1
SWIFT_T_HOME=/oscar/data/akhann16/sfw/swift-t-02062024
export PATH=$SWIFT_T_HOME/stc/bin:$PATH


