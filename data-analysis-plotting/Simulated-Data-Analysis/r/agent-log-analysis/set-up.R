rm(list=ls())

# Load libraries ------------

library(here)
library(data.table)
library(yaml)


# Activate environment ------------

# renv::load()
renv::activate()


# Input params ------------




# Read simulated data ------------


#sim_data_path <- "~/data/akhann16/cadre_simulated_data/output_20231128_194046/" #noah's data
#sim_data_path <- "/users/akhann16/code/cadre/python/output_20231110_152817/"
#sim_data_path <- "~/data/akhann16/cadre_simulated_data/output_20231106_082519/"

sim_data_path <- "~/data/akhann16/cadre_simulated_data/output_20231207_211453/" 

agent_dt <- fread(paste0(sim_data_path, "agent_log.csv"))
str(agent_dt)
last_tick <- max(agent_dt$tick)
print(last_tick)


# Read input parameters ------------

input_params <- yaml.load_file(paste0(sim_data_path, "parameters.txt"))


# Create environment to save ------------

agent_log_env <- new.env()
agent_log_env$agent_dt <- agent_dt
agent_log_env$input_params <- input_params


# Save environment ------------

saveRDS(agent_log_env, here("agent-log-analysis", "rds-outs", "agent_log_env.RDS"))
