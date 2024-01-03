# Analyze incarceration data


# Load R environment ---------

renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)


# Utility functions ------------
#source(here("agent-analysis", "utils", "post-release-smoking.R"))
source("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/utils/post-release-smoking.R")


# Read RDS file ------------

all_instances_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))




# Compute current smoking rates in groups with and without incarceration across all instances ------------

# Initialize a dataframe to store aggregated smoking ratios
aggregated_smoking_ratios <- data.frame()

# Loop through each instance data
for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  
  # Your existing code for smoking ratio calculation
  last_tick_data <- agent_dt[tick == max(agent_dt$tick),]
  smoking_ratio <- last_tick_data[, .(
    n_current_smokers = sum(smoking_status == "Current"),
    n_total_persons = sum(smoking_status %in% c("Current", "Former", "Never"))
  ), by = .(group = n_releases >= 1)]
  smoking_ratio[, ratio := n_current_smokers / n_total_persons][]
  
  # Add instance identifier to smoking_ratio
  smoking_ratio$instance <- i
  
  # Aggregate data
  aggregated_smoking_ratios <- rbind(aggregated_smoking_ratios, smoking_ratio)
}

# Compute overall statistics (mean, sd, etc.) for each group across instances
overall_smoking_stats <- aggregated_smoking_ratios[, .(
  mean_ratio = mean(ratio),
  sd_ratio = sd(ratio)
), by = .(group)]

overall_smoking_stats

# Compute current smoking rates in groups with and without incarceration across all instances ------------

time_periods <- c(1, 7, 14, 30, 90, 180, 365)
labels <- c("1D", "1W", "2W", "1M", "3M", "6M", "1Y")
summaries_smoking <- lapply(time_periods, function(x) summary_after_release(x))

# Initialize a list to store time-series data for each instance
all_summaries_smoking <- list()

# Loop through each instance data
for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  
  # Compute the summary for each time period and store it
  summaries_smoking_instance <- lapply(time_periods, function(x) summary_after_release_multiple(agent_dt, x))
  all_summaries_smoking[[i]] <- summaries_smoking_instance
}


# Initialize a dataframe to store aggregated data
aggregated_smoking_data <- data.frame()

# Loop through each time period
for (time_period in time_periods) {
  # Extract data for the current time period from all instances
  time_period_data <- lapply(all_summaries_smoking, function(x) x[[which(time_periods == time_period)]])
  
  # Aggregate data across instances
  mean_proportion <- mean(sapply(time_period_data, function(x) x$proportions[x$proportions$Category == "Current", "Proportion"]))
  sd_proportion <- sd(sapply(time_period_data, function(x) x$proportions[x$proportions$Category == "Current", "Proportion"]))
  
  # Combine into a dataframe
  aggregated_smoking_data <- rbind(aggregated_smoking_data, data.frame(Time = time_period, Mean = mean_proportion, SD = sd_proportion))
}

p_prev_inc <-
  ggplot(aggregated_smoking_data, aes(x = Time, y = Mean)) +
  geom_line(color = "blue") +
  geom_ribbon(aes(ymin = Mean - SD, ymax = Mean + SD), fill = "blue", alpha = 0.3) +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  labs(title = "",
       x = "Time After Release",
       y = "Mean Proportion of Current Smoking") +
  theme_minimal() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1))

p_prev_inc


# Compute and add plot of current smoking rate in the overall population ---------

# Initialize a list to store smoking ratios for each instance
smoking_ratios_list <- list()

# Loop through each instance data
for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  proportion_data <- calculate_proportions_smoking(agent_dt)
  
  # Extract proportion for "Current" smokers
  current_smokers_proportion <- proportion_data[proportion_data$Category == "Current", "Proportion"]
  smoking_ratios_list[[i]] <- current_smokers_proportion
}

# Convert the list to a vector
smoking_ratios_vector <- unlist(smoking_ratios_list)

# Compute overall statistics (mean, sd, etc.) for "Current" smokers across instances
overall_mean_smoking <- mean(smoking_ratios_vector, na.rm = TRUE)
overall_sd_smoking <- sd(smoking_ratios_vector, na.rm = TRUE)

# Add to Plot

p_base <- 
  ggplot(aggregated_smoking_data, aes(x = Time, y = Mean)) +
  geom_line(aes(color = "Previously Incarcerated")) +
  geom_ribbon(aes(ymin = Mean - SD, ymax = Mean + SD, fill = "Previously Incarcerated"), alpha = 0.3) +
  geom_hline(aes(yintercept = overall_mean_smoking, color = "Overall Population")) +
  geom_ribbon(aes(ymin = overall_mean_smoking - overall_sd_smoking, ymax = overall_mean_smoking + overall_sd_smoking, fill = "Overall Population"), alpha = 0.3) +
  scale_color_manual(values = c("Previously Incarcerated" = "blue", "Overall Population" = "red"), 
                     name = "Group", 
                     labels = c("Previously Incarcerated", "Overall Population")) +
  scale_fill_manual(values = c("Previously Incarcerated" = "blue", "Overall Population" = "red"), 
                    name = "Group", 
                    labels = c("Previously Incarcerated", "Overall Population")) +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  labs(title = "",
       x = "Time After Release",
       y = "Proportion of Current Smoking") +
  theme_minimal() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1))

p_base


