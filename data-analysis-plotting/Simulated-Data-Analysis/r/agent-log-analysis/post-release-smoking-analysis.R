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
source("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-analysis/utils/post-release-smoking.R")


# Read RDS file ------------

#agent_log_env <- readRDS(here("agent-analysis", "rds-outs", "agent_log_env.RDS"))
agent_log_env <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-analysis/rds-outs/agent_log_env.RDS")


# Load data ------------

agent_dt <- agent_log_env[["agent_dt"]]
input_params <- agent_log_env[["input_params"]]


# Tick variables ------------

last_tick <- max(agent_dt$tick)
selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)
last_tick_data <- agent_dt[tick==last_tick,]


# Smoking ratio at last tick of current smoking to all persons ----------

smoking_ratio <- 
  last_tick_data[, .(
    n_current_smokers = sum(smoking_status == "Current"),
    n_total_persons = sum(smoking_status %in% c("Current", "Former", "Never"))
  ), by = .(group = n_releases >= 1)]

# Compute the ratio of current smokers to total smokers in each group

smoking_ratio
smoking_ratio[, ratio := n_current_smokers / n_total_persons][]



# Compute change in current smoking over time since release ----------

## computation
time_periods <- c(1, 7, 14, 30, 90, 180, 365)
labels <- c("1D", "1W", "2W", "1M", "3M", "6M", "1Y")
summaries_smoking <- lapply(time_periods, function(x) summary_after_release(x))

summaries_smoking


# Visualization (smoking in released persons) ----------

current_smoker_proportions <- sapply(
  summaries_smoking, 
  function(x) {
    if ("Current" %in% x$proportions$Category){
      return(x$proportions[x$proportions$Category == "Current", "Proportion"])
    }
    else {
      return(0)
    }
  }
)

current_smoker_df <- data.frame(Time = time_periods,
                                Labels = labels,
                                Proportion = current_smoker_proportions)

p <- 
  ggplot(current_smoker_df, aes(x = Time, y = Proportion, group = 1)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  scale_y_continuous(breaks = seq(0, 1, 0.2), limits = c(0, 1)) +
  labs(title = "",
       x = "Time After Release",
       y = "Proportion of Current Smoking") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))


# Visualization (smoking in general population) ----------

# calculate the proportion of current, former, and never smokers at the specified time ticks
smokers_by_tick <- agent_dt[tick %in% selected_ticks, .(
  current_smokers = sum(smoking_status == "Current") / .N,
  former_smokers = sum(smoking_status == "Former") / .N,
  never_smokers = sum(smoking_status == "Never") / .N
), by = tick]

# mean from the the last last 10 rows
mean_current_smoker <- mean(tail(smokers_by_tick$current_smokers, 10))

# create a new data frame for the general population
general_population <- data.frame(
  Time = current_smoker_df$Time,
  Proportion = rep(mean_current_smoker, length(current_smoker_df$Time))
)

# create the plot
p <- ggplot() +
  geom_line(data = current_smoker_df, aes(x = Time, y = Proportion, color = "Previously Incarcerated"), linewidth=1.5) +
  geom_line(data = general_population, aes(x = Time, y = Proportion, color = "Overall"), linewidth=1.5) +
  scale_color_manual(values = c("Previously Incarcerated" = "blue", "Overall" = "red")) +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  scale_y_continuous(breaks = seq(0, 1, 0.2), limits = c(0, 1)) +
  labs(
    title = "",
    x = "Time After Release",
    y = "",
    color = "Current Smoking Rate"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1),
        text = element_text(size = 24, face = "bold"))
p


