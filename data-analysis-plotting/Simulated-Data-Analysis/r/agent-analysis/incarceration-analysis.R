# Analyze incarceration data


# Load R environment ---------

renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)


# Read RDS file ------------

agent_log_env <- readRDS(here("agent-analysis", "rds-outs", "agent_log_env.RDS"))


# Load data ------------

agent_dt <- agent_log_env[["agent_dt"]]
input_params <- agent_log_env[["input_params"]]


# Summary ------------

selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)

# mean incarceration rate over time
incarceration_summary <- agent_dt[tick %in% selected_ticks, 
                                  .(n_incarcerated = sum(current_incarceration_status == 1),
                                    n_agents = .N), 
                                  by = tick]

incarceration_summary[, rate_per_100k := n_incarcerated / n_agents * 100000]

ggplot(incarceration_summary, aes(x = tick, y = rate_per_100k)) +
  geom_line() +
  theme_minimal() +
  labs(title = "",
       x = "Time (Days)",
       y = "Incarceration Rate (per 100,000 persons)")#+


# number incarcerated
ggplot(incarceration_summary, aes(x = tick, y = n_incarcerated)) +
  geom_line() +
  theme_minimal() +
  labs(title = "",
       x = "Time (Days)",
       y = "Number Incarcerated")


# Last tick analysis ----------

# number and proportion of incarcerated persons at last tick:
incarceration_summary <- agent_dt[tick %in% selected_ticks, 
                                  .(n_incarcerated = sum(current_incarceration_status == 1),
                                    n_agents = .N), 
                                  by = tick]
tail(incarceration_summary)

# race distribution
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("race")][,"prop":=round(N/sum(N)*100, 0)][]

# sex distribution
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("female")][,"prop":=round(N/sum(N)*100, 0)][]


# race-sex distribution
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("race", "female")][,"prop":=round(N/sum(N)*100, 0)][]

# smoking
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("smoking_status")][,"prop":=round(N/sum(N)*100, 0)][]

# alcohol 
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("alc_use_status")][,"prop":=round(N/sum(N)*100, 0)][]
