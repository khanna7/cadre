rm(list=ls())

# Load libraries ------------

library(here)
library(data.table)
library(yaml)


# Activate environment ------------

# renv::load()
renv::activate()

# Input params ------------

input_params <- read_yaml("~/code/cadre/python/myparams/model_params.yaml")


# Read simulated data ------------

sim_data_path <- "/users/akhann16/code/cadre/python/output_20231029_214346/agent_log.csv"
agent_dt <- fread(sim_data_path)
str(agent_dt)
last_tick <- max(agent_dt$tick)
print(last_tick)


# Create environment to save ------------

agent_log_env <- new.env()
agent_log_env$agent_dt <- agent_dt
agent_log_env$input_parms <- input_params


# Save environment ------------

saveRDS(agent_log_env, here("agent-analysis", "rds-outs", "agent_log_env.RDS"))
