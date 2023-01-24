#!/bin/bash

set -eu

# Check for an optional timeout threshold in seconds. If the duration of the
# model run as executed below, takes longer that this threshhold
# then the run will be aborted. Note that the "timeout" command
# must be supported by executing OS.

# The timeout argument is optional. By default the "run_model" swift
# app fuction sends 3 arguments, and no timeout value is set. If there
# is a 4th (the TIMEOUT_ARG_INDEX) argument, we use that as the timeout value.

# !!! IF YOU CHANGE THE NUMBER OF ARGUMENTS PASSED TO THIS SCRIPT, YOU MUST
# CHANGE THE TIMEOUT_ARG_INDEX !!!
TIMEOUT=""
TIMEOUT_ARG_INDEX=5
if [[ $# ==  $TIMEOUT_ARG_INDEX ]]
then
	TIMEOUT=${!TIMEOUT_ARG_INDEX}
fi

TIMEOUT_CMD=""
if [ -n "$TIMEOUT" ]; then  TIMEOUT_CMD="timeout $TIMEOUT"
fi

# Set PARAM_LINE from the first argument to this script
# PARAM_LINE is the string containing the model parameters for a run.
PARAM_LINE="$1"

# Set EMEWS_ROOT to the root directory of the project (i.e. the directory
# that contains the scripts, swift, etc. directories and files)
EMEWS_ROOT=$2

# TODO: Activate the python venv
module load python/3.9.0
#source /gpfs/data/akhann16/ncollie1/venv/3.9/bin/activate
source /gpfs/home/akhann16/code/cadre/python/new_cadre_env_4/bin/activate 

# Each model run, runs in its own "instance" directory
# Set INSTANCE_DIRECTORY to that and cd into it.
INSTANCE_DIRECTORY=$3
cd $INSTANCE_DIRECTORY

# TODO: Define the command to run the model. For example,
MODEL_CMD="python3"
# TODO: Define the arguments to the MODEL_CMD. Each argument should be
# surrounded by quotes and separated by spaces. For example,
# arg_array=("$EMEWS_ROOT/python/my_model.py" "$PARAM_LINE")

#PY_FILE=/gpfs/data/akhann16/ncollie1/src/r4py_examples/zombies/zombies.py
YAML_FILE=$4

#arg_array=( "$PY_FILE"
#            "$YAML_FILE"
#            "$PARAM_LINE" )
arg_array=( "-m" "pycadre" "$PARAM_FILE" "-p" "$PARAM_LINE")

# Turn bash error checking off. This is
# required to properly handle the model execution
# return values and the optional timeout.
set +e
echo "Running $MODEL_CMD ${arg_array[@]}"

$TIMEOUT_CMD $MODEL_CMD "${arg_array[@]}"
# "$PY_FILE" "$YAML_FILE" "$PARAM_LINE"
# $? is the exit status of the most recently executed command (i.e the
# line above)
RES=$?
if [ "$RES" -ne 0 ]; then
	if [ "$RES" == 124 ]; then
    echo "---> Timeout error in $COMMAND"
  else
	   echo "---> Error in $COMMAND"
  fi
fi
