# Analyze incarceration data

rm(list=ls())
  
renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)
library(dplyr)


# Utility functions ------------

source("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/utils/post-release-alcohol.R")


# Read RDS file ------------

all_instances_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))


# Compute metrics (at single tick) ------------

# Initialize a list to store alcohol use state distributions for each instance
all_instances_alcohol_summaries <- list()

# Loop through each instance data
for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  last_tick <- max(agent_dt$tick)
  
  # Calculations for various subsets
  all_agents_summary <- calculate_proportions(agent_dt[tick == last_tick])
  never_released_agents_summary <- calculate_proportions(agent_dt[tick == last_tick & n_releases == 0])
  released_agents_summary <- calculate_proportions(agent_dt[tick == last_tick & n_releases >= 1])
  
  # Add other specific calculations as needed, such as short-term post-release analysis
  # ...
  
  # Store summaries for the current instance
  instance_summary <- list(
    all_agents_summary = all_agents_summary,
    never_released_agents_summary = never_released_agents_summary,
    released_agents_summary = released_agents_summary
    # Add other summaries here
  )
  
  all_instances_alcohol_summaries[[i]] <- instance_summary
}


# data aggregation
aggregated_alcohol_data <- data.frame()

# Aggregating data for 'all_agents_summary' across instances
all_agents_aggregated <- rbindlist(lapply(all_instances_alcohol_summaries, "[[", "all_agents_summary"), idcol = "instance")

# Calculating mean and standard deviation for each category across instances
all_agents_stats <- all_agents_aggregated[, .(mean_proportion = mean(Proportion), sd_proportion = sd(Proportion)), by = .(Category)]


# Aggregating data for 'never_released_agents_summary'
never_released_agents_aggregated <- rbindlist(lapply(all_instances_alcohol_summaries, "[[", "never_released_agents_summary"), idcol = "instance")

never_released_agents_stats <- never_released_agents_aggregated[, .(mean_proportion = mean(Proportion), sd_proportion = sd(Proportion)), by = .(Category)]


# Aggregating data for 'released_agents_summary'
released_agents_aggregated <- rbindlist(lapply(all_instances_alcohol_summaries, "[[", "released_agents_summary"), idcol = "instance")

released_agents_stats <- released_agents_aggregated[, .(mean_proportion = mean(Proportion), sd_proportion = sd(Proportion)), by = .(Category)]


# Plot (at single tick) -----------

ggplot(all_agents_stats, aes(x = Category, y = mean_proportion)) +
  geom_bar(stat = "identity", position = position_dodge()) +
  geom_errorbar(aes(ymin = mean_proportion - sd_proportion, ymax = mean_proportion + sd_proportion), width = 0.25, position = position_dodge(0.9)) +
  labs(title = "Alcohol Use Proportions for All Agents Across Instances",
       x = "Category",
       y = "Mean Proportion") +
  theme_minimal()


# Compute metrics (time series) ------------

selected_ticks <- c(1, 7, 14, 30, 90, 180, 365)
labels <- c("1D", "1W", "2W", "1M", "3M", "6M", "1Y")

# Assuming selected_ticks is defined and all_instances_data is available

all_instances_time_series <- list()

for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  
  # Calculate proportions at each tick
  instance_time_series <- lapply(selected_ticks, function(tick) {
    agents_at_tick <- agent_dt[tick == tick, ]
    proportions <- calculate_proportions(agents_at_tick)
    return(list("proportions" = proportions, "tick" = tick))
  })
  
  all_instances_time_series[[i]] <- instance_time_series
}

