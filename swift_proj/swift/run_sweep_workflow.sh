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
export TURBINE_OUTPUT=$EMEWS_PROJECT_ROOT/experiments/$EXPID
check_directory_exists

CFG_FILE=$2
source $CFG_FILE

echo "----------------------------------------------------"
echo "WALLTIME:                   $CFG_WALLTIME"
echo "PROCS:                      $CFG_PROCS"
echo "PPN:                        $CFG_PPN"
echo "QUEUE:                      $CFG_QUEUE"
echo "PROJECT:                    $CFG_PROJECT"
echo "UPF FILE:                   $CFG_UPF"
echo "PARAM FILE:                 $CFG_PARAM_FILE"
echo "SITE:                       $CFG_SITE"
echo "----------------------------------------------------"

export PROCS=$CFG_PROCS
export QUEUE=$CFG_QUEUE
export PROJECT=$CFG_PROJECT
export WALLTIME=$CFG_WALLTIME
export PPN=$CFG_PPN
export TURBINE_JOBNAME="${EXPID}_job"

#export TURBINE_SBATCH_ARGS="--exclusive --mem-per-cpu=${CFG_MEM_PER_CPU}"
export SITE=$CFG_SITE

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
export PYTHONPATH=$EMEWS_PROJECT_ROOT/../python

EMEWS_EXT=$EMEWS_PROJECT_ROOT/ext/emews

# Copies UPF file to experiment directory
U_UPF_FILE=$CFG_UPF
UPF_FILE=$TURBINE_OUTPUT/upf.txt
cp $U_UPF_FILE $UPF_FILE

PARAM_FILE=$TURBINE_OUTPUT/params.yaml
cp $CFG_PARAM_FILE $PARAM_FILE

# CFG_DERIVED_PARAM_FILE=$EMEWS_PROJECT_ROOT/../params/params/derived_parameters.py
# CFG_R_ERGM_FILE=$EMEWS_PROJECT_ROOT/../r/network_model/transmission_model_tergmlite.R
# CFG_INIT_DATA_FILE=EMEWS_PROJECT_ROOT/../r/network_model/chi_net_n5000.RData

#DERIVED_PARAM_FILE=$TURBINE_OUTPUT/dervived_params.py
#cp $CFG_DERIVED_PARAM_FILE $DERIVED_PARAM_FILE

#R_ERGM_FILE=$TURBINE_OUTPUT/ergm.R
#cp $CFG_R_ERGM_FILE $R_ERGM_FILE

#INIT_DATA_FILE=$TURBINE_OUTPUT/init_net_data.RData
#cp $CFG_INIT_DATA_FILE $INIT_DATA_FILE

CMD_LINE_ARGS="$* -f=$UPF_FILE -param_file=$PARAM_FILE" 
#CMD_LINE_ARGS+="-init_data_file=$INIT_DATA_FILE -derived_param_file=$DERIVED_PARAM_FILE"
# CMD_LINE_ARGS can be extended with +=:
# CMD_LINE_ARGS+="-another_arg=$ANOTHER_VAR"

# TODO: Set MACHINE to your schedule type (e.g. pbs, slurm, cobalt etc.),
# or empty for an immediate non-queued unscheduled run
MACHINE="slurm"

if [ -n "$MACHINE" ]; then
  MACHINE="-m $MACHINE"
fi

export PATH=/gpfs/home/akhann16/sfw/swift-t/stc/bin:$PATH

# TODO: Some slurm machines may expect jobs to be run
# with srun, rather than mpiexec (for example). If
# so, uncomment this export.
# export TURBINE_LAUNCHER=srun

# TODO: Add any script variables that you want to log as
# part of the experiment meta data to the USER_VARS array,
# for example, USER_VARS=("VAR_1" "VAR_2")
USER_VARS=()
# log variables and script to to TURBINE_OUTPUT directory
#log_script
# echo's anything following this to standard out
set -x
SWIFT_FILE=sweep_workflow.swift
swift-t -n $PROCS $MACHINE -p \
    -I $EMEWS_EXT -r $EMEWS_EXT \
    $EMEWS_PROJECT_ROOT/swift/$SWIFT_FILE \
    $CMD_LINE_ARGS
