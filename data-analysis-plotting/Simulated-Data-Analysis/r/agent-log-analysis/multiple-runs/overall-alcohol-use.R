# Analyze simulated demographic data 

rm(list=ls())


# Load R environment ---------

renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)


# Read RDS file ------------

all_instances_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))


# Input parameters for target values ----------

agent_log_env_one_instance <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")
input_params <- agent_log_env_one_instance[["input_params"]] # THE INPUT PARAMS NEED TO BE ADDED FOR THE CODE TO WORK
alc_use_props <- input_params$ALC_USE_PROPS
alc_use_targets <- c(alc_use_props$`0`, alc_use_props$`1`, alc_use_props$`2`, alc_use_props$`3`)



# Compute metrics --------

# Assuming all_instances_data contains the data from all instances

# Initialize a list to store alcohol use proportions for each instance
all_alc_use_proportions_by_tick <- list()

for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  last_tick <- max(agent_dt$tick)
  selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)
  
  # Calculate alcohol use proportions for each instance
  alc_use_proportions <- agent_dt[tick %in% selected_ticks, .(
    Non_Drinking = sum(alc_use_status == 0) / .N,
    Category_I = sum(alc_use_status == 1) / .N,
    Category_II = sum(alc_use_status == 2) / .N,
    Category_III = sum(alc_use_status == 3) / .N
  ), by = tick]
  
  # Convert to long format for easier aggregation later
  alc_use_proportions_long <- melt(alc_use_proportions, id.vars = "tick", 
                                   variable.name = "alc_use_status", 
                                   value.name = "proportion")
  
  # Add instance identifier
  alc_use_proportions_long$instance <- i
  
  # Append these calculations to all_alc_use_proportions_by_tick
  all_alc_use_proportions_by_tick[[i]] <- alc_use_proportions_long
}

# Combine all alcohol use proportions into a single data frame
combined_alc_use_proportions <- do.call(rbind, all_alc_use_proportions_by_tick)

# Calculate mean and range for each sampled tick across all instances
aggregated_alc_use_proportions <- combined_alc_use_proportions[, .(mean_proportion = mean(proportion),
                                                                   min_proportion = min(proportion),
                                                                   max_proportion = max(proportion)), 
                                                               by = .(tick, alc_use_status)]

# Convert data.tables to data.frames for ggplot2
aggregated_alc_use_proportions_df <- as.data.frame(aggregated_alc_use_proportions)




# Plot ----------------------

# Define colors for each category of alcohol use
alc_colors <- c("Non_Drinking" = "#377eb8", "Category I" = "#ff7f00", 
                "Category II" = "#4daf4a", "Category III" = "#e41a1c")

names(alc_colors)
print(alc_colors)

# Calculate the x-position for the annotations
half_time <- max(aggregated_alc_use_proportions_df$tick)/365/2

# Create a data frame for the target alcohol use proportions
target_alc_use_df <- data.frame(
  alc_use_status = names(alc_colors),
  target_pct = as.numeric(alc_use_targets),
  color = alc_colors
)

# Generate the plot
alc_use_time_plot_base <- 
  ggplot(aggregated_alc_use_proportions_df, aes(x = tick/365, y = mean_proportion, color = alc_use_status, group = alc_use_status)) +
  geom_ribbon(aes(ymin = min_proportion, ymax = max_proportion, fill = alc_use_status), alpha = 0.3) +
  geom_line() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1))

alc_use_time_plot_base

alc_use_time_plot_base_labels <- 
  alc_use_time_plot_base + 
  geom_text(data = target_alc_use_df, 
            aes(x = half_time, y = target_pct, label = sprintf("Target: %.2f%%", target_pct * 100)), 
            color = "black", vjust = 0) +  # Set color to black for visibility
  labs(title = "",
       x = "Time (Years)",
       y = "Proportion") +
  theme_minimal() +
  theme(legend.title = element_blank()) +
  guides(color = guide_legend(override.aes = list(alpha = 1)))

# Print the plot
alc_use_time_plot_base_labels

  
