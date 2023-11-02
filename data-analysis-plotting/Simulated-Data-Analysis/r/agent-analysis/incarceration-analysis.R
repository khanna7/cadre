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


# Ever incarcerated ----------

# how many?

# To answer this question, we can group the last incarceration times by agent ID.
# If last incarceration time is -1, the person has never been incarcerated. 
# If last incarceration time is > -1, the person has been incarcerated at least once. 

last_incarceration_time <- agent_dt[, 
                                    .(last_incarceration_time = max(last_incarceration_tick)), 
                                    by = id]

n_ever_incarcerated <- sum(last_incarceration_time$last_incarceration_time != -1)

prop_ever_incarcerated <- n_ever_incarcerated / nrow(last_incarceration_time)


# agent-level analysis of those ever incarcerated 

ever_incarcerated_times <- last_incarceration_time[last_incarceration_time > 1]
dim(ever_incarcerated_times)

## demographics

### generate dataset
ever_incarcerated_ids <-
  unique(agent_dt[id %in% ever_incarcerated_times$id, id])
ever_incarcerated_info <- agent_dt[id %in% ever_incarcerated_ids,
                                   .SD[.N, list(
                                     id,
                                     age = last(age),
                                     race = last(race),
                                     female = last(female)
                                   )],
                                   by = id]


### create distributions

# Disparity analysis ----------
## defined as ratio of % representation in incarcerated population
## to representation in general population



