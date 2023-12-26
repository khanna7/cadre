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


alc_use_last_tick <- 
  agent_dt[tick == last_tick, .N, by = c("alc_use_status")][, 
                                                            "%" := round(N /sum(N), 3)][
                                                              order(alc_use_status)][
                                                              ]

# targets
alc_use_props <- input_params$ALC_USE_PROPS
alc_use_targets <- c(alc_use_props$`0`, alc_use_props$`1`, alc_use_props$`2`, alc_use_props$`3`)

cbind(alc_use_last_tick[["%"]], alc_use_targets)

# Calculate the percentages for alcohol use status
alc_use_dt <- agent_dt[tick == last_tick, .N, by = alc_use_status][, `:=` (percentage = round(N/sum(N)*100, 2))]

# Order the data table by alcohol use status
setorder(alc_use_dt, alc_use_status)

# Rename the alcohol use status codes to descriptive labels
alc_use_dt[, alc_use_status := factor(alc_use_status, levels = c(0, 1, 2, 3), 
                                      labels = c("Non-Drinking", 
                                                 "Category I", 
                                                 "Category II", 
                                                 "Category III"))]


ggplot(alc_use_dt, aes(x = alc_use_status, y = percentage, fill = alc_use_status)) +
  geom_bar(stat = "identity", color = "black") +
  labs(title = "Agent Alcohol Use Status Distribution",
       x = "Use Frequency",
       y = "Percentage",
       fill = "Alcohol Use Status") +
  theme_minimal() +
  guides(fill = "none") +
  geom_text(aes(label = paste0(as.numeric(input_params$ALC_USE_PROPS)*100, "%")), 
            position = position_stack(vjust = 1.02))+
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 10))

# Plot over time

# calculate the distribution of alcohol states at the specified time ticks

time_ticks <- c(seq(1, last_tick, by = 10), last_tick)

alc_use_by_tick <- 
  agent_dt[tick %in% time_ticks, .(
  "Non Drinking" = sum(alc_use_status == 0) / .N,
  "Category I" = sum(alc_use_status == 1) / .N,
  "Category II" = sum(alc_use_status == 2) / .N,
  "Category III" = sum(alc_use_status== 3) / .N
  ), 
  by = tick]

# convert the data from wide to long format
alc_use_status_long <- melt(alc_use_by_tick, 
                              id.vars = "tick", 
                              variable.name = "alc_use_status", 
                              value.name = "proportion")


# create a time series plot of race proportions

alc_use_time_plot <-
  ggplot(race_proportions_long, 
         aes(x = tick, y = proportion, color = alc_use_status, group = alc_use_status)) +
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
  
  geom_text(aes(x = max(tick)/2, y = alc_use_targets[1] + 0.03,
                label = sprintf("Target: %.2f", alc_use_targets[1])), color = "#377eb8", check_overlap = TRUE, size=5) +
  
  geom_text(aes(x = max(tick)/2, y = alc_use_targets[2] + 0.03,
                 label = sprintf("Target: %.2f", alc_use_targets[2])), color = "#ff7f00", check_overlap = TRUE, size=5) +
   
  geom_text(aes(x = max(tick)/2, y = alc_use_targets[3] + 0.03, 
                 label = sprintf("Target: %.2f", alc_use_targets[3])), color = "#4daf4a", check_overlap = TRUE, size=5) +
  
  geom_text(aes(x = max(tick)/2, y = alc_use_targets[4] - 0.03,
               label = sprintf("Target: %.2f", alc_use_targets[4])), color = "#e41a1c", check_overlap = TRUE, size=5)

alc_use_time_plot

