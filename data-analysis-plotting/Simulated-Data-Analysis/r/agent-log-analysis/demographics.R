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

agent_log_env <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")


# Load data ------------

agent_dt <- agent_log_env[["agent_dt"]]
input_params <- agent_log_env[["input_params"]] # THE INPUT PARAMS NEED TO BE ADDED FOR THE CODE TO WORK


# View data --------

head(agent_dt)


# Summary ------------

last_tick <- max(agent_dt$tick)
selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)


length(unique(agent_dt$id)) # n unique agents in dataset
range(unique(agent_dt$id))


# Race distribution ------------

## compute
agent_dt_by_race <- agent_dt[tick == last_tick, .N, by=race][,
                                                             "per_cent":=round(N/sum(N)*100)][order(race)]
target_values <- data.frame(race = names(input_params$RACE_DISTRIBUTION), 
                            target_pct = unlist(input_params$RACE_DISTRIBUTION))
agent_dt_by_race[]



time_ticks <- c(seq(1, last_tick, by = 10), last_tick)

# calculate the proportion of each race at the specified time ticks
race_proportions_by_tick <- agent_dt[tick %in% time_ticks, .(
  White = sum(race == "White") / .N,
  Black = sum(race == "Black") / .N,
  Hispanic = sum(race == "Hispanic") / .N,
  Asian = sum(race == "Asian") / .N
), by = tick]

# convert the data from wide to long format
race_proportions_long <- melt(race_proportions_by_tick, id.vars = "tick", variable.name = "race", value.name = "proportion")

# create a time series plot of race proportions
race_plot <-
  ggplot(race_proportions_long, aes(x = tick, y = proportion, color = race, group = race)) +
  geom_line(linewidth=1.2) +
  labs(title = "",
       x = "Time (Days)",
       y = "Proportion") +
  scale_color_manual(values = c("#377eb8", "#ff7f00", "#4daf4a", "#e41a1c")) +
  theme_minimal() +
  theme(
    legend.title = element_blank(),
    axis.text.x = element_text(size = 14, face = "bold"),  
    axis.text.y = element_text(size = 14, face = "bold"),  
    legend.text = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold")
  ) +
  theme(legend.title = element_blank())+
  scale_y_continuous(limits = c(0, 0.8), breaks = seq(0, 0.8, by = 0.1)) +
  
  geom_text(aes(x = max(tick)/2, y = target_values$target_pct[target_values$race == "White"] + 0.03,
                label = sprintf("Target: %.3f", target_values$target_pct[target_values$race == "White"])), color = "#377eb8", check_overlap = TRUE, size=5) +
  
  geom_text(aes(x = max(tick)/2, y = target_values$target_pct[target_values$race == "Black"] + 0.03,
                label = sprintf("Target: %.3f", target_values$target_pct[target_values$race == "Black"])), color = "#ff7f00", check_overlap = TRUE, size=5) +
  
  geom_text(aes(x = max(tick)/2, y = target_values$target_pct[target_values$race == "Hispanic"] + 0.03, 
                label = sprintf("Target: %.3f", target_values$target_pct[target_values$race == "Hispanic"])), color = "#4daf4a", check_overlap = TRUE, size=5) +
  
  geom_text(aes(x = max(tick)/2, y = target_values$target_pct[target_values$race == "Asian"] + 0.03,
                label = sprintf("Target: %.3f", target_values$target_pct[target_values$race == "Asian"])), color = "#e41a1c", check_overlap = TRUE, size=5)

race_plot


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

