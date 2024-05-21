rm(list=ls())
  

# Activate environment ------------
renv::activate()
.libPaths()


# Load libraries ------------

library(here)
library(data.table)
library(yaml)


# Base path for simulated data ------------
base_sim_data_path <- "/oscar/data/akhann16/akhann16/cadre_simulated_data/emews_experiments/post-review-run/"


# Determine the number of instances ------------
num_instances <- length(list.files(base_sim_data_path, pattern = "instance_"))


# List to store data from each instance
all_instances_data <- list()

# Loop through each instance ------------

for (i in 1:num_instances){
  sim_data_path <- paste0(base_sim_data_path, "instance_", i, "/output/")
  
  # Read simulated data for the current instance
  agent_dt <- fread(paste0(sim_data_path, "agent_log.csv"))
  last_tick <- max(agent_dt$tick)
  print(paste("Last tick for instance", i, ":", last_tick))
  
  # Read input parameters
  input_params <- yaml.load_file(paste0(sim_data_path, "parameters.txt"))
  
  # Store data in a list or another preferred structure
  all_instances_data[[i]] <- list(
    agent_dt = agent_dt,
    input_params = input_params
  )
  
  # Save individual instance data
  # saveRDS(list(agent_dt = agent_dt, input_params = input_params), 
  #          here("agent-log-analysis", "multiple-runs" ,"rds-outs", paste0("agent_log_env_instance_", i, ".RDS")))

  
  }

# Save all instances data
saveRDS(all_instances_data, here("agent-log-analysis", "multiple-runs" ,"rds-outs", "all_instances_data.RDS"))

