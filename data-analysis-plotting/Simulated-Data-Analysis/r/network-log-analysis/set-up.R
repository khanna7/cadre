rm(list=ls())


# Load libraries ------------

library(data.table)
library(here)
library(DiagrammeR)
library(yaml)
library(igraph)
library(ggraph)
library(ggplot2)


# Activate environment ------------

renv::activate()
here()





# Read simulated data ------------

sim_data_loc <- "/users/akhann16/code/cadre/python/output_20231207_211453/"

network_dt <- fread(paste0(sim_data_loc, "network_log.csv")) #simulated network data
agent_dt <- fread(paste0(sim_data_loc, "agent_log.csv"))#simulated agent data
last_tick <- max(network_dt$tick) 


# Input params ------------

input_params <- yaml.load_file(paste0(sim_data_loc, "parameters.txt"))


# Create environment to save ------------

network_log_env <- new.env()
network_log_env$agent_dt <- agent_dt
network_log_env$input_parms <- input_params
network_log_env$network_dt <- network_dt


# Save environment ------------

saveRDS(network_log_env, here("network-log-analysis", "rds-outs", "network_log_env.RDS"))

