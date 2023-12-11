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


## plot
# Define the time ticks you want to analyze
time_ticks <- c(seq(1, last_tick, by = 10), last_tick)

# Calculate the proportion of each race at the specified time ticks
race_proportions_by_tick <- agent_dt[tick %in% time_ticks, .(
  White = sum(race == "White") / .N,
  Black = sum(race == "Black") / .N,
  Hispanic = sum(race == "Hispanic") / .N,
  Asian = sum(race == "Asian") / .N
), by = tick]

# Convert the data from wide to long format
race_proportions_long <- melt(race_proportions_by_tick, id.vars = "tick", variable.name = "race", value.name = "proportion")

# Create a time series plot of race proportions

# Create a time series plot of race proportions
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