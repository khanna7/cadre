# Analyze simulated demographic data 

rm(list=ls())


# Load R environment ---------

renv::activate()
.libPaths()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)


# Read RDS file ------------

all_instances_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))


# Input parameters for target values -----
agent_log_env_one_instance <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")
input_params <- agent_log_env_one_instance[["input_params"]] # THE INPUT PARAMS NEED TO BE ADDED FOR THE CODE TO WORK


# Race distribution ------------

target_values <- data.frame(race = names(input_params$RACE_DISTRIBUTION), 
                            target_pct = unlist(input_params$RACE_DISTRIBUTION))

all_race_proportions_by_tick <- list()

for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  last_tick <- max(agent_dt$tick)
  selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)
  
  # Calculate race proportions for each instance
  race_proportions <- agent_dt[tick %in% selected_ticks, .(
    White = sum(race == "White") / .N,
    Black = sum(race == "Black") / .N,
    Hispanic = sum(race == "Hispanic") / .N,
    Asian = sum(race == "Asian") / .N
  ), by = tick]
  
  # Convert to long format for easier aggregation later
  race_proportions_long <- melt(race_proportions, id.vars = "tick", variable.name = "race", value.name = "proportion")
  
  # Add instance identifier
  race_proportions_long$instance <- i
  
  # Append these calculations to all_race_proportions_by_tick
  all_race_proportions_by_tick[[i]] <- race_proportions_long
}

# Combine all race proportions into a single data frame
combined_race_proportions <- do.call(rbind, all_race_proportions_by_tick)

# Calculate mean and SD for each sampled tick across all instances
aggregated_race_proportions <- combined_race_proportions[, .(mean_proportion = mean(proportion),
                                                             sd_proportion = sd(proportion)), 
                                                         by = .(tick, race)]

# Calculate min and max proportion for each race and tick across all instances
race_proportions_stats <- combined_race_proportions[, .(min_proportion = min(proportion),
                                                        max_proportion = max(proportion)), 
                                                    by = .(tick, race)]

# Plot

target_values$color <- c("#377eb8", "#ff7f00", "#4daf4a", "#e41a1c")[match(target_values$race, c("White", "Black", "Hispanic", "Asian"))]

# calculate the x-position for the annotations
half_time <- max(combined_race_proportions$tick)/365/2

# convert data.tables to data.frames for ggplot2
race_proportions_stats_df <- as.data.frame(race_proportions_stats)
aggregated_race_proportions_df <- as.data.frame(aggregated_race_proportions)
target_values_df <- as.data.frame(target_values)

# initialize plot
p_race_base <- ggplot() +
  # First plot the individual trajectories as ribbons
  geom_ribbon(data = race_proportions_stats_df, aes(x = tick/365, ymin = min_proportion, ymax = max_proportion, fill = race), alpha = 0.3) +
  scale_fill_manual(values = c("#377eb8", "#ff7f00", "#4daf4a", "#e41a1c")) +
  # Next, plot the mean proportions as lines
  geom_line(data = aggregated_race_proportions_df, aes(x = tick/365, y = mean_proportion, color = race, group = race)) +
  scale_color_manual(values = c("#377eb8", "#ff7f00", "#4daf4a", "#e41a1c")) +
  theme(legend.title = element_blank())+
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) +
  labs(title = "",
       x = "Time (Days)",
       y = "Proportion")+
  theme_minimal()

p_race <- p_race_base + 
  geom_text(data = target_values_df, aes(x = half_time, y = target_pct + 0.03,
                                                label = sprintf("Target: %.3f", target_pct)), color = target_values_df$color, check_overlap = TRUE, size=5)

p_race



# Sex distribution ----------

# Initialize a list to store sex proportions for each instance
all_gender_proportions_by_tick <- list()

for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  last_tick <- max(agent_dt$tick)
  selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)
  
  # Calculate sex proportions for each instance
  gender_proportions <- agent_dt[tick %in% selected_ticks, .(
    male = sum(female == 0) / .N,
    female = sum(female == 1) / .N
  ), by = tick]
  
  # Convert to long format for easier aggregation later
  gender_proportions_long <- melt(gender_proportions, id.vars = "tick", variable.name = "gender", value.name = "proportion")
  
  # Add instance identifier
  gender_proportions_long$instance <- i
  
  # Append these calculations to all_gender_proportions_by_tick
  all_gender_proportions_by_tick[[i]] <- gender_proportions_long
}

# Combine all gender proportions into a single data frame
combined_gender_proportions <- do.call(rbind, all_gender_proportions_by_tick)

# Calculate mean and optionally SD for each sampled tick across all instances
aggregated_gender_proportions <- combined_gender_proportions[, .(mean_proportion = mean(proportion),
                                                                 sd_proportion = sd(proportion)), 
                                                             by = .(tick, gender)]

# Calculate min and max proportion for each sex and tick across all instances
gender_proportions_stats <- combined_gender_proportions[, .(min_proportion = min(proportion),
                                                            max_proportion = max(proportion)), 
                                                        by = .(tick, gender)]

# Convert data.tables to data.frames for ggplot2
gender_proportions_stats_df <- as.data.frame(gender_proportions_stats)
aggregated_gender_proportions_df <- as.data.frame(aggregated_gender_proportions)


# plot

# Define colors for male and female
colors <- c("male" = "#1b9e77", "female" = "#d95f02")

# Calculate the x-position for the annotations
half_time <- max(aggregated_gender_proportions_df$tick)/365/2

# Target percentages for each gender
female_target_pct <- input_params$FEMALE_PROP
male_target_pct <- 1 - female_target_pct

# Create a data frame for the target sex distribution
target_sex_distribution_df <- data.frame(
  gender = c("male", "female"),
  target_pct = c(male_target_pct, female_target_pct),
  color = c("#1b9e77", "#d95f02")  # Use the appropriate colors for male and female
)

# Plot
p_sex_distribution_base <- 
  ggplot() +
  # Shaded area for variability across instances
  geom_ribbon(data = gender_proportions_stats_df, 
              aes(x = tick/365, ymin = min_proportion, ymax = max_proportion, fill = gender), alpha = 0.3) +
  scale_fill_manual(values = colors) +
  # Mean proportion lines
  geom_line(data = aggregated_gender_proportions_df, 
            aes(x = tick/365, y = mean_proportion, color = gender, group = gender)) +
  scale_color_manual(values = colors) 

p_sex_distribution_base

# Adjust the target_sex_distribution_df to include specific y-values for the labels
target_sex_distribution_df$label_y <- c(male_target_pct - 0.05, female_target_pct+0.03)  # Adjust these values as needed

# Plot
p_sex_distribution <- 
  p_sex_distribution_base +
  # Annotations for target values with specific y-values
  geom_text(data = target_sex_distribution_df, 
            aes(x = half_time, y = label_y, label = sprintf("Target: %.3f", target_pct)), 
            color = target_sex_distribution_df$color, size = 5) +
  # Aesthetics and labels
  labs(title = "",
       x = "Time (Years)",
       y = "Proportion",
       fill = "Gender",
       color = "Gender") +
  theme_minimal() +
  # theme(legend.title = element_blank(),
  #       axis.text.x = element_text(size = 14, face = "bold"),  
  #       axis.text.y = element_text(size = 14, face = "bold"),  
  #       legend.text = element_text(size = 14),
  #       axis.title.x = element_text(size = 16, face = "bold"),
  #       axis.title.y = element_text(size = 16, face = "bold")) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1))

# Print the plot
p_sex_distribution




# Add age distribution later if needed