module load python/3.9.0
module load gcc/8.3
module load mpi/openmpi_4.0.4_gcc 
module unload java #WHY IS THIS NECESSARY?
module load R/4.0.3

#export MPICH_ROOT=/software/mpich-3.3-el7-x86_64+gcc-9.2.0 #SINCE WE ARE LOADING OPENMPI, DO WE ALSO NEED THIS?
export TCL_ROOT=/gpfs/home/akhann16/sfw/tcl-8.6.12
export R_LIBS_SITE=/gpfs/home/akhann16/sfw/r-4.0.3_libs
#export LD_LIBRARY_PATH=/software/mpich-3.3-el7-x86_64+gcc-9.2.0/lib:$R_LIBS_SITE/RInside/lib:$LD_LIBRARY_PATH #AND THIS?
