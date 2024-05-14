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


# Target values ----------

agent_log_env_one_instance <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")
input_params <- agent_log_env_one_instance[["input_params"]] # THE INPUT PARAMS NEED TO BE ADDED FOR THE CODE TO WORK

smoking_props <- input_params$SMOKING_PREV

## see background calculations at  https://rpubs.com/nwrousell/1075243.

##    SMOKESTATUS2        V1
## 1:        NEVER 0.6550938
## 2:       FORMER 0.2294748
## 3:      CURRENT 0.1154314

targets_smoking <- list()
targets_smoking[["CURRENT"]] <- 0.1154314
targets_smoking[["FORMER"]] <- 0.2294748
targets_smoking[["NEVER"]] <- 0.6550938

targets_smoking


# Compute metrics ----------

# Initialize a list to store  proportions for each instance
all_smoking_proportions_by_tick <- list()

for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  last_tick <- max(agent_dt$tick)
  selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)

  smoking_by_tick <- 
    agent_dt[tick %in% selected_ticks, .(
      "Current" = sum(smoking_status == "Current") / .N,
      "Former" = sum(smoking_status == "Former") / .N,
      "Never" = sum(smoking_status == "Never") / .N
    ), 
    by = tick]
  
  # Convert to long format for easier aggregation later
  smoking_proportions_long <- melt(smoking_by_tick,
                       id.vars = "tick",
                       variable.name = "smoking_status",
                       value.name = "proportion")
  
  # Add instance identifier
  smoking_proportions_long$instance <- i
  
  # Append these calculations to list created above
  all_smoking_proportions_by_tick[[i]] <- smoking_proportions_long
  
  }

# Combine all smoking proportions into a single data frame
combined_smoking_proportions <- do.call(rbind, all_smoking_proportions_by_tick)

# Calculate mean and range for each sampled tick across all instances
aggregated_smoking_proportions <- 
  combined_smoking_proportions[, .(mean_proportion = mean(proportion),
                                   min_proportion = min(proportion), 
                                   max_proportion = max(proportion)), 
                               by = .(tick, smoking_status)]


# Convert data.tables to data.frames for ggplot2
aggregated_smoking_proportions_df <- as.data.frame(aggregated_smoking_proportions)


# Plot ----------------------

# Define colors for each category of smoking
smoking_colors <- c("Current" = "#377eb8", "Former" = "#ff7f00", 
                "Never" = "#4daf4a"
                )

names(smoking_colors)
print(smoking_colors)

# Calculate the x-position for the annotations
half_time <- max(aggregated_smoking_proportions_df$tick)/365/2

# Create a data frame for the target proportions
target_smoking_df <- data.frame(
  smoking_status = names(smoking_colors),
  target_pct = as.numeric(targets_smoking),
  color = smoking_colors
)


# Generate the plot
smoking_time_plot_base <- 
  ggplot(aggregated_smoking_proportions_df, aes(x = tick/365, y = mean_proportion, color = smoking_status, group = smoking_status)) +
  geom_ribbon(aes(ymin = min_proportion, ymax = max_proportion, fill = smoking_status), alpha = 0.3) +
  geom_line() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1))

smoking_time_plot_base


smoking_time_plot_base_labels <- 
  smoking_time_plot_base + 
  geom_text(data = target_smoking_df, 
            aes(x = half_time, y = target_pct, label = sprintf("Target: %.2f%%", target_pct * 100)), 
            color = "black", vjust = 0) +  # Set color to black for visibility
  labs(title = "",
       x = "Time (Years)",
       y = "Proportion") +
  theme_minimal() +
  theme(legend.title = element_blank()) +
  guides(color = guide_legend(override.aes = list(alpha = 1)))


smoking_time_plot_base_labels


ggsave(filename = here("agent-log-analysis", "multiple-runs", "plots", "smoking_time_plot_base_labels.png"), 
       plot = smoking_time_plot_base_labels, 
       width = 10, height = 8, units = "in")
