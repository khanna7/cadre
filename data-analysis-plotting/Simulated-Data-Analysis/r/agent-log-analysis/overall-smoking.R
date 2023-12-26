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

head(agent_dt)
str(agent_dt)


# Last tick --------

last_tick <- max(agent_dt$tick)
print(last_tick)


# Compute metrics and plot --------


smoking_last_tick <- 
  agent_dt[tick == last_tick, .N, by = c("smoking_status")][, 
                                                            "pct" := round(N /sum(N), 3)*100]

smoking_last_tick[]

# targets
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


ggplot(smoking_last_tick, 
       aes(x = smoking_status, y = pct, fill = smoking_status)) +
  geom_bar(stat = "identity", color = "black") +
  labs(title = " Smoking State Distribution",
       x = "State",
       y = "Percentage",
       fill = "Smoking State") +
  theme_minimal()+
  guides(fill = "none") +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 10))

# Plot over time

# calculate the distribution at the specified time ticks

time_ticks <- c(seq(1, last_tick, by = 10), last_tick)

smoking_by_tick <- 
  agent_dt[tick %in% time_ticks, .(
    "Current" = sum(smoking_status == "Current") / .N,
    "Former" = sum(smoking_status == "Former") / .N,
    "Never" = sum(smoking_status == "Never") / .N
  ), 
  by = tick]

# convert the data from wide to long format
smoking_long <- melt(smoking_by_tick,
                            id.vars = "tick",
                            variable.name = "smoking_status",
                            value.name = "proportion")


# create a time series plot

smoking_time_plot <-
  ggplot(smoking_long,
         aes(x = tick, y = proportion, color = smoking_status, group = smoking_status)) +
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
  
  geom_text(aes(x = max(tick)/2, y = targets_smoking[["CURRENT"]] - 0.01,
              label = sprintf("Target: %.3f", targets_smoking[["CURRENT"]])), color = "#377eb8", check_overlap = TRUE, size=5) +

  geom_text(aes(x = max(tick)/2, y = targets_smoking[["FORMER"]] + 0.01,
                label = sprintf("Target: %.3f", targets_smoking[["FORMER"]])), color = "#ff7f00", check_overlap = TRUE, size=5) +

  geom_text(aes(x = max(tick)/2, y = targets_smoking[["NEVER"]]  + 0.01,
                label = sprintf("Target: %.2f", targets_smoking[["NEVER"]])), 
                                color = "#4daf4a", check_overlap = TRUE, size=5) 

smoking_time_plot


