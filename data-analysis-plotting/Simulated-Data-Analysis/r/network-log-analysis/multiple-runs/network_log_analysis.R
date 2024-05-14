rm(list=ls())


# Environment activation ----------

if (is.null(Sys.getenv("RENV_PROJECT"))) {
  renv::activate()
} else {
  message("renv is already activated.")
}

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

all_instances_network_data <- readRDS(here("network-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))

all_instances_agent_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))


# One instance data, for input parameters etc ---------

one_instance_network_data <- all_instances_network_data[[1]]
network_dt <- one_instance_network_data[["network_dt"]]

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

num_instances <- length(all_instances_nework_data)


# Initialize vectors to store metrics for each instance
prevalence_smoking_network <- numeric(num_instances)
prevalence_aud_network <- numeric(num_instances)
prevalence_smoking_ego <- numeric(num_instances)
prevalence_aud_ego <- numeric(num_instances)


# Loop through each instance to compute metrics
for (i in 1:num_instances) {
  cat("Entering instance ", i, "\n")
  
  network_dt <- all_instances_network_data[[i]][["network_dt"]]
  agent_dt <- all_instances_agent_data[[i]][["agent_dt"]]
  last_tick <- max(network_dt$tick)
  
  # Focus on the last tick data
  last_tick_network_dt <- network_dt[tick == last_tick,]
  last_tick_agent_dt <- agent_dt[tick == last_tick,]
  
  # Analysis for each instance
  
  # Identify the IDs of the recently released agents
  recently_released_agents <- last_tick_agent_dt$id[last_tick_agent_dt$last_release_tick > (last_tick - 365)]
  
  # Get the network data for the recently released agents
  network_recently_released <- last_tick_network_dt[(last_tick_network_dt$p1 %in% recently_released_agents) | 
                                                      (last_tick_network_dt$p2 %in% recently_released_agents),]
  
  # Get agent data for the first-degree neighbors
  first_degree_neighbors <- unique(c(network_recently_released$p1, network_recently_released$p2))
  first_degree_neighbors_agent_data <- last_tick_agent_dt[last_tick_agent_dt$id %in% first_degree_neighbors,]
  
  # Calculate metrics
  
  # Prevalence of Current Smoking and AUD among network members
  num_current_smoking <- sum(first_degree_neighbors_agent_data$smoking_status == "Current")
  num_aud <- sum(first_degree_neighbors_agent_data$alc_use_status == 3)
  total_agents <- nrow(first_degree_neighbors_agent_data)
  prevalence_smoking <- num_current_smoking / total_agents
  prevalence_aud <- num_aud / total_agents
  
  # Prevalence of Current Smoking and AUD among recently released agents (egos)
  recently_released_agents_df <- last_tick_agent_dt[last_tick_agent_dt$id %in% recently_released_agents,]
  num_ego_current_smoking <- sum(recently_released_agents_df$smoking_status == "Current")
  num_ego_aud <- sum(recently_released_agents_df$alc_use_status == 3)
  total_ego_agents <- length(recently_released_agents)
  prevalence_ego_smoking <- num_ego_current_smoking / total_ego_agents
  prevalence_ego_aud <- num_ego_aud / total_ego_agents
  
  # Store the results in the vectors
  prevalence_smoking_network[i] <- prevalence_smoking
  prevalence_aud_network[i] <- prevalence_aud
  prevalence_smoking_ego[i] <- prevalence_ego_smoking
  prevalence_aud_ego[i] <- prevalence_ego_aud
}


# Compute mean and SD

## released agents' network: current smoking
summary(prevalence_smoking_network)
sd(prevalence_smoking_network)

## released agents' network: heavy alcohol
summary(prevalence_aud_network)
sd(prevalence_aud_network)

## released agents: current smoking
summary(prevalence_smoking_ego)
sd(prevalence_smoking_ego)

## released agents: heavy alcohol
summary(prevalence_aud_ego)
sd(prevalence_aud_ego)



# Compare multiple instance results with smoking/alcohol rates in the entire population ----------

# Initialize vectors for overall population metrics
prevalence_smoking_overall <- numeric(num_instances)
prevalence_aud_overall <- numeric(num_instances)

# Loop through each instance to compute metrics for overall population
for (i in 1:num_instances) {
  
  cat("Entering instance ", i, "\n")
  agent_dt <- all_instances_agent_data[[i]][["agent_dt"]]
  
  # Calculate metrics for overall population
  num_current_smoking_overall <- sum(agent_dt$smoking_status == "Current")
  num_aud_overall <- sum(agent_dt$alc_use_status == 3)
  total_agents_overall <- nrow(agent_dt)
  
  prevalence_smoking_overall[i] <- num_current_smoking_overall / total_agents_overall
  prevalence_aud_overall[i] <- num_aud_overall / total_agents_overall
  
}

# After the loop, compute mean and SD for overall population metrics
summary(prevalence_smoking_overall)
sd(prevalence_smoking_overall)

mean(prevalence_aud_overall)
sd(prevalence_aud_overall)

