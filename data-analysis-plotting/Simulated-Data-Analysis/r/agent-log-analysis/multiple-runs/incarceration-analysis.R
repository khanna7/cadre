# Analyze incarceration data (This is from the agent log, there is a separate incarceartion log)
rm(list=ls())


# Load R environment ---------

#renv::activate()
#.libPaths()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)


# Read RDS file ------------

#agent_log_env <- readRDS(here("agent-analysis", "rds-outs", "agent_log_env.RDS"))
#agent_log_env <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")
all_instances_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))



# Summary ------------

# Initialize a list to store incarceration summaries for each instance
all_incarceration_summaries <- list()

# Loop through each instance data
for (i in 1:length(all_instances_data)){
  agent_dt <- all_instances_data[[i]]$agent_dt
  selected_ticks <- c(seq(1, max(agent_dt$tick), by = 10), max(agent_dt$tick))
  
  # Calculate incarceration rate for the current instance
  incarceration_summary <- agent_dt[tick %in% selected_ticks, 
                                    .(n_incarcerated = sum(current_incarceration_status == 1),
                                      n_agents = .N), 
                                    by = tick]
  incarceration_summary[, rate_per_100k := n_incarcerated / n_agents * 100000]
  
  # Store the summary
  all_incarceration_summaries[[i]] <- incarceration_summary
}

# Combine all summaries into a single data frame
combined_summary <- rbindlist(all_incarceration_summaries, idcol = "instance")

# Calculate mean and standard deviation of rate_per_100k for each tick across all instances
aggregated_summary <- combined_summary[, .(mean_rate_per_100k = mean(rate_per_100k),
                                           sd_rate_per_100k = sd(rate_per_100k)), 
                                       by = tick]

# Plotting

# Create a common theme object
common_theme <- theme_minimal() +
  theme(legend.title = element_blank(),
        axis.text.x = element_text(size = 14, face = "bold"),  
        axis.text.y = element_text(size = 14, face = "bold"),  
        legend.text = element_text(size = 14),
        axis.title.x = element_text(size = 16, face = "bold"),
        axis.title.y = element_text(size = 16, face = "bold"),
        plot.margin = margin(10, 10, 10, 10),
        panel.grid.major = element_line(color = "black", linewidth=0.1),  # Set major grid lines to black
        panel.grid.minor = element_line(color = "black", linewidth=0.05)
        ) 

# Apply common theme to the mean incarceration rate plot
ggplot(aggregated_summary, aes(x = tick, y = mean_rate_per_100k)) +
  geom_line() +
  geom_errorbar(aes(ymin = mean_rate_per_100k - sd_rate_per_100k, ymax = mean_rate_per_100k + sd_rate_per_100k), width = 0.5) +
  common_theme +  # Apply the common theme
  labs(title = "Mean Incarceration Rate Over Time",
       x = "Time (Days)",
       y = "Mean Incarceration Rate (per 100,000 persons)") +
  ylim(c(0, 500))

# Plotting with individual trajectories and standard deviation
p_inc_traj <- 
  ggplot() +
    # Individual trajectories in light gray
    geom_line(data = combined_summary, aes(x = tick/365, y = rate_per_100k, group = instance), 
              color = "gray80", alpha = 0.2, linewidth = 0.5) +
    # Mean rate in black
    geom_line(data = aggregated_summary, aes(x = tick/365, y = mean_rate_per_100k), 
              color = "black", linewidth = 1) +
    # Standard deviation range in blue
    geom_ribbon(data = aggregated_summary, 
                aes(x = tick/365, ymin = mean_rate_per_100k - sd_rate_per_100k, 
                    ymax = mean_rate_per_100k + sd_rate_per_100k), 
                fill = "blue", alpha = 0.3) +
    # Apply common theme
    common_theme +
    labs(title = "",
         x = "Years",
         y = "Incarceration Rate (per 100,000 persons)") +
    theme(legend.position = "bottom")

# Save the plot with 400 DPI
ggsave(filename = here("agent-log-analysis", "multiple-runs", "plots", "incarceration_trajs.png"), 
       plot = p_inc_traj, 
       width = 10, height = 8, units = "in", dpi = 400)
