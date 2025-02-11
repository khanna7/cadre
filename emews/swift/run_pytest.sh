#! /usr/bin/env bash
set -eu

if [ "$#" -ne 2 ]; then
  script_name=$(basename $0)
  echo "Usage: ${script_name} exp_id cfg_file"
  exit 1
fi

# Uncomment to turn on swift/t logging. Can also set TURBINE_LOG,
# TURBINE_DEBUG, and ADLB_DEBUG to 0 to turn off logging
# export TURBINE_LOG=1 TURBINE_DEBUG=1 ADLB_DEBUG=1
export EMEWS_PROJECT_ROOT=$( cd $( dirname $0 )/.. ; /bin/pwd )
# source some utility functions used by EMEWS in this script
source "${EMEWS_PROJECT_ROOT}/etc/emews_utils.sh"

export EXPID=$1
# export TURBINE_OUTPUT=$EMEWS_PROJECT_ROOT/experiments/$EXPID
export TURBINE_OUTPUT=/oscar/data/akhann16/akhann16/cadre_simulated_data/emews_experiments/$EXPID
check_directory_exists

CFG_FILE=$2
source $CFG_FILE

echo "--------------------------"
echo "WALLTIME:              $CFG_WALLTIME"
echo "PROCS:                 $CFG_PROCS"
echo "PPN:                   $CFG_PPN"
echo "QUEUE:                 $CFG_QUEUE"
# echo "PROJECT:               $CFG_PROJECT"
echo "UPF FILE:              $CFG_UPF"
echo "MAIL USER:             $CFG_MAIL_USER"
echo "MAIL TYPE:             $CFG_MAIL_TYPE"
echo "--------------------------"

export PROCS=$CFG_PROCS
export QUEUE=$CFG_QUEUE
# export PROJECT=$CFG_PROJECT
export WALLTIME=$CFG_WALLTIME
export PPN=$CFG_PPN
export MAIL_USER=$CFG_MAIL_USER
export MAIL_TYPE=$CFG_MAIL_TYPE
export TURBINE_JOBNAME="${EXPID}_job"
export TURBINE_MPI_THREAD=1


mkdir -p $TURBINE_OUTPUT
cp $CFG_FILE $TURBINE_OUTPUT/cfg.cfg

# TODO: If R cannot be found, then these will need to be
# uncommented and set correctly.
# export R_HOME=/path/to/R
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$R_HOME/lib

# TODO: If Python cannot be found or there are "Cannot find 
# X package" type errors then these two environment variables
# will need to be uncommented and set correctly.
# export PYTHONHOME=/path/to/python

# TODO: Update with VENV
#VENV_SITE_PACKAGES=/gpfs/data/akhann16/ncollie1/venv/3.9/lib/python3.9/site-packages
#export PYTHONPATH=$EMEWS_PROJECT_ROOT/python:/gpfs/data/akhann16/ncollie1/src/r4py_examples/zombies:$VENV_SITE_PACKAGES

VENV_SITE_PACKAGES=/gpfs/data/akhann16/sfw/pyenvs/repast4py-py3.11/lib/python3.11/site-packages
#export PYTHONPATH=$EMEWS_PROJECT_ROOT/python:/gpfs/home/akhann16/code/cadre/python:$VENV_SITE_PACKAGES 
export PYTHONPATH=$EMEWS_PROJECT_ROOT/../python:$EMEWS_PROJECT_ROOT/python:/gpfs/home/akhann16/code/cadre/python:$VENV_SITE_PACKAGES


EMEWS_EXT=$EMEWS_PROJECT_ROOT/ext/emews

# Copies UPF file to experiment directory
U_UPF_FILE=$EMEWS_PROJECT_ROOT/$CFG_UPF
UPF_FILE=$TURBINE_OUTPUT/upf.txt
cp $U_UPF_FILE $UPF_FILE

TARGET_PARAM_FILE=$TURBINE_OUTPUT/params.yaml
cp $CFG_PARAM_FILE $TARGET_PARAM_FILE

CMD_LINE_ARGS="$* -f=$UPF_FILE -param_file=$TARGET_PARAM_FILE"
# CMD_LINE_ARGS can be extended with +=:
# CMD_LINE_ARGS+="-another_arg=$ANOTHER_VAR"

# TODO: Set MACHINE to your schedule type (e.g. pbs, slurm, cobalt etc.),
# or empty for an immediate non-queued unscheduled run
MACHINE="slurm"

if [ -n "$MACHINE" ]; then
  MACHINE="-m $MACHINE"
fi

# TODO: Some slurm machines may expect jobs to be run
# with srun, rather than mpiexec (for example). If
# so, uncomment this export.
export TURBINE_LAUNCHER=mpirun
# export TURBINE_SBATCH_ARGS="--exclusive"
export TURBINE_SBATCH_ARGS="--mail-user=$MAIL_USER --mail-type=$MAIL_TYPE"
export TURBINE_LAUNCH_OPTIONS="--mca opal_warn_on_missing_libcuda 0 --mca btl '^openib' --mca opal_common_ucx_opal_mem_hooks 1"

# See https://www.mail-archive.com/devel@lists.open-mpi.org/msg21434.html
# MPI_LIB="/oscar/runtime/software/hpcx-mpi/4.1.5rc2/hpcx-ompi/lib"
MPI_LIB="/oscar/rt/9.2/software/0.20-generic/0.20.1/opt/spack/linux-rhel9-x86_64_v3/gcc-11.3.1/openmpi-4.1.2-s5wtoqbqirz4ivubo6uzp2ndglheablu/lib"
CUDA_LIB="/oscar/rt/9.2/software/0.20-generic/0.20.1/opt/spack/linux-rhel9-x86_64_v3/gcc-11.3.1/cuda-12.1.1-ebglvvqo7uhjvhvff2qlsjtjd54louaf/lib64"
# export LD_PRELOAD="$CUDA_LIB/libcudart.so"


# TODO: Add any script variables that you want to log as
# part of the experiment meta data to the USER_VARS array,
# for example, USER_VARS=("VAR_1" "VAR_2")
USER_VARS=()
# log variables and script to to TURBINE_OUTPUT directory
log_script
# echo's anything following this to standard out
set -x
SWIFT_FILE=pytest.swift
swift-t -n $PROCS $MACHINE -p \
    -I $EMEWS_EXT -r $EMEWS_EXT \
    -e TURBINE_MPI_THREAD \
    -e TURBINE_OUTPUT \
    -e EMEWS_PROJECT_ROOT \
    -e LD_LIBRARY_PATH=$MPI_LIB:$LD_LIBRARY_PATH \
    $EMEWS_PROJECT_ROOT/swift/$SWIFT_FILE \
    $CMD_LINE_ARGS
