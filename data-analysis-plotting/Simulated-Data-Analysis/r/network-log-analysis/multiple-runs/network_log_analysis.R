rm(list=ls())


# Environment activation ----------

renv::activate()
.libPaths()


# Libraries --------


library(data.table)
library(here)
library(DiagrammeR)
library(yaml)
library(igraph)
library(ggraph)
library(ggplot2)

here()


# Read RDS file for all instance data ------------

all_instances_nework_data <- readRDS(here("network-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))

all_instances_agent_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))


# One instance data, for input parameters etc ---------

one_instance_network_data <- all_instances_network_data[[1]]
network_dt <- one_instance_data[["network_dt"]]

one_instance_agent_data <- all_instances_agent_data[[1]]
agent_dt <- one_instance_agent_data[["agent_dt"]]

input_params <- one_instance_data[["input_params"]]


# Last tick focus ---------

last_tick <- max(network_dt$tick) 
last_tick_network_dt <- network_dt[tick==last_tick,]
last_tick_network_dt

last_tick_agent_dt <- agent_dt[tick == last_tick,]
last_tick_agent_dt


# Single instance Analysis --------- 

# Identify the IDs of the recently released agents
recently_released_agents <- last_tick_agent_dt$id[last_tick_agent_dt$last_release_tick > (last_tick - 365)]

# Get the network data for the recently released agents
network_recently_released <- last_tick_network_dt[(last_tick_network_dt$p1 %in% recently_released_agents) | 
                                                    (last_tick_network_dt$p2 %in% recently_released_agents),]

# Get the first-degree network (neighbors) for each agent
first_degree_neighbors <- unique(c(network_recently_released$p1, network_recently_released$p2))

# Get agent data for the first-degree neighbors
first_degree_neighbors_agent_data <- last_tick_agent_dt[last_tick_agent_dt$id %in% first_degree_neighbors,]

# Create an edge data frame from your network data
edf <- data.frame(from = network_recently_released$p1, 
                  to = network_recently_released$p2)

# Create a node data frame with your agent data
ndf <- data.frame(id = first_degree_neighbors_agent_data$id, 
                  smoking_status = first_degree_neighbors_agent_data$smoking_status,
                  alc_use_status = first_degree_neighbors_agent_data$alc_use_status,
                  recently_released = ifelse(first_degree_neighbors_agent_data$id %in% recently_released_agents, "yes", "no"))

# Create a graph with DiagrammeR
graph <- create_graph(nodes_df = ndf, 
                      edges_df = edf,
                      directed = FALSE)


## Prevalence of Current Smoking and AUD among network members

# Number of agents with Current Smoking status
num_current_smoking <- sum(first_degree_neighbors_agent_data$smoking_status == "Current")

# Number of agents with AUD
num_aud <- sum(first_degree_neighbors_agent_data$alc_use_status == 3)

# Total number of agents in the network
total_agents <- nrow(first_degree_neighbors_agent_data)

# Calculate prevalence
prevalence_smoking <- num_current_smoking / total_agents
prevalence_aud <- num_aud / total_agents

# Print the results
prevalence_smoking
prevalence_aud

# Prevalence of Current Smoking and AUD among this set of egos

# Define selected_agents_df, which contains the data for the selected agents
recently_released_agents_df <- last_tick_agent_dt[last_tick_agent_dt$id %in% recently_released_agents,]

# Number of selected agents who are current smokers
num_ego_current_smoking <- sum(recently_released_agents_df$smoking_status == "Current")

# Number of selected agents with AUD
num_ego_aud <- sum(recently_released_agents_df$alc_use_status == 3)

# Total number of selected agents
total_ego_agents <- length(recently_released_agents)

# Calculate prevalence
prevalence_ego_smoking <- num_ego_current_smoking / total_ego_agents
prevalence_ego_aud <- num_ego_aud / total_ego_agents

# Print the results
prevalence_ego_smoking
prevalence_ego_aud





# Multiple instance analysis ---------

