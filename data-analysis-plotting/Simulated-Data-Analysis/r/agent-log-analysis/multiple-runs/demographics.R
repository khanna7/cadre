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
p_race <- ggplot() +
  # First plot the individual trajectories as ribbons
  geom_ribbon(data = race_proportions_stats_df, aes(x = tick/365, ymin = min_proportion, ymax = max_proportion, fill = race), alpha = 0.3) +
  scale_fill_manual(values = c("#377eb8", "#ff7f00", "#4daf4a", "#e41a1c")) +
  # Next, plot the mean proportions as lines
  geom_line(data = aggregated_race_proportions_df, aes(x = tick/365, y = mean_proportion, color = race, group = race)) +
  scale_color_manual(values = c("#377eb8", "#ff7f00", "#4daf4a", "#e41a1c")) +
  theme(legend.title = element_blank())+
  scale_y_continuous(limits = c(0, 0.8), breaks = seq(0, 0.8, by = 0.1)) +
  labs(title = "",
       x = "Time (Days)",
       y = "Proportion") 

p_race <- p + geom_text(data = target_values_df, aes(x = half_time, y = target_pct + 0.03,
                                                label = sprintf("Target: %.3f", target_pct)), color = target_values_df$color, check_overlap = TRUE, size=5)

p_race

# Sex distribution ------------

agent_dt[tick==last_tick, .N, by=female][,"%":=N/sum(N)][order(female)]
female_target <- input_params$FEMALE_PROP

gender_pct <- agent_dt[tick == last_tick, .N, by = female][, "%":= N/sum(N)][order(female)]

female_target <- input_params$FEMALE_PROP

# calculate target percentages for each gender
female_target_pct <- female_target
male_target_pct <- 1 - female_target

# calculate actual percentages for each gender
female_actual_pct <- gender_pct[female == 1, `%`]
male_actual_pct <- gender_pct[female == 0, `%`]


# create plot for last tick
ggplot(gender_pct, aes(x = ifelse(female == 0, "Male", "Female"), y = `%`, fill = ifelse(female == 0, "Male", "Female"))) +
  geom_bar(stat = "identity", color = "black") +
  scale_fill_manual(values = c("#1b9e77", "#d95f02")) +
  annotate("text", x = 1, y = female_actual_pct, 
           label = paste0("Female Target = ", round(female_actual_pct*100, 1), "%"), 
           color = "#1b9e77", size = 4, vjust = 0) +
  annotate("text", x = 2, y = male_actual_pct, 
           label = paste0("Male Target = ", round(male_actual_pct*100, 1), "%"), 
           color = "#d95f02", size = 4, vjust = 0) +
  labs(title = "",
       x = "Time (Days)",
       y = "Sex Distributions",
       fill = "") +
  theme_minimal()




# plot over time:
  
# calculate the proportion of males and females at the specified time ticks
gender_proportions_by_tick <- agent_dt[tick %in% time_ticks, .(
  male = sum(female == 0) / .N,
  female = sum(female == 1) / .N
), by = tick]

# convert the data from wide to long format
gender_proportions_long <- melt(gender_proportions_by_tick, id.vars = "tick", variable.name = "gender", value.name = "proportion")

ggplot(gender_proportions_long, aes(x = tick, y = proportion, color = gender, group = gender)) +
  geom_line(linewidth=1.5) +
  labs(title = "",
       x = "Time (Days)",
       y = "Proportion") +
  scale_color_manual(values = c("#1b9e77", "#d95f02"), labels = c("Male", "Female")) +
  theme_minimal() +
  theme(
    legend.title = element_blank(),
    axis.text.x = element_text(size = 16, face = "bold"),  
    axis.text.y = element_text(size = 16, face = "bold"),  
    legend.text = element_text(size = 16),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold")
  ) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0.4, 0.6, by = 0.1)) +
  geom_text(aes(x = max(tick)/2, y = (female_target+0.03), label = sprintf("Target: %.3f", female_target)), color = "#d95f02", check_overlap = TRUE, size = 5) + 
  geom_text(aes(x = max(tick)/2, y = (1 - female_target - 0.03), label = sprintf("Target: %.3f", 1 - female_target)), color = "#1b9e77", check_overlap = TRUE, size = 5)



# Age distribution ------------

agebreaks <- c(18, 25, 35, 45, 55, 65)
agelabels <- c("18-24", "25-34", "35-44", "45-54", "55-64")

agent_dt[tick == last_tick, .N, ]
setDT(agent_dt)[ , age_groups := cut(age, 
                                     breaks = agebreaks, 
                                     include.lowest = TRUE,
                                     right = FALSE, 
                                     labels = agelabels)]
nrow(agent_dt[tick == last_tick])

agent_dt[tick == last_tick, .N, by=c("age_groups", "race", "female")][order(age_groups, race, female)]
agent_dt[tick == last_tick, .N, by=c("race", "age_groups", "female")][order(race, age_groups)]

agent_dt[tick==last_tick, .N, by=c("race", "female")][,"%":=N/sum(N)*100][order(race)]



agent_dt[tick==last_tick, .N, by=c("age_groups")][,"%":=round(N/sum(N)*100)][order(age_groups)]

#Median age at the start: 
  
agent_dt[tick==1, median(age)]


# Median age at the end:
  
nrow(agent_dt[tick==last_tick])
agent_dt[tick==last_tick, median(age)]


# Create age groups
agent_dt_by_age_group <- agent_dt[tick==last_tick, .N, 
                                  by = .(age_group = cut(age, breaks = c(18, 25, 35, 45, 55, 65, 75, 80, 84)))]

# Create bar chart
ggplot(agent_dt_by_age_group, aes(x = age_group, y = N, fill = age_group)) +
  geom_bar(stat = "identity", color = "black") +
  scale_fill_manual(values = c("#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf")) +
  labs(title = "Agent Age Distribution",
       x = "Age Group",
       y = "Count",
       fill = "Age Group") +
  theme_minimal()

