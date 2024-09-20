# Analyze incarceration data

rm(list=ls())
  
renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)
library(dplyr)


# Utility functions ------------

#source(here("agent-analysis", "utils", "post-release-alcohol.R"))
#print(here("agent-analysis", "utils", "post-release-alcohol.R")) 
source("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/utils/post-release-alcohol.R")


# Read RDS file ------------


#agent_log_env <- readRDS(here("agent-analysis", "rds-outs", "agent_log_env.RDS"))
print(here("agent-analysis", "rds-outs", "agent_log_env.RDS"))

agent_log_env <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")



# Load data ------------

agent_dt <- agent_log_env[["agent_dt"]]
input_params <- agent_log_env[["input_params"]]


# Ticks of interest ----------

selected_ticks <- seq(1, max(agent_dt$tick), by = 10)
last_tick <- max(agent_dt$tick)


# Population subsets by release status --------
desired_tick=last_tick

all_agents <- agent_dt[tick==desired_tick,] #everyone at all times

never_released_agents <- agent_dt[tick==desired_tick & n_releases == 0] #never release

released_agents <- agent_dt[tick == desired_tick & n_releases >= 1] #released at least once


# Alcohol use state distributions in above subsets --------

all_agents_summary <- calculate_proportions(all_agents)
never_released_agents_summary <- calculate_proportions(never_released_agents)
released_agents_summary <- calculate_proportions(released_agents)


# Summarize alcohol use rates in general population --------


alcohol_summaries <- 
  lapply(selected_ticks, function(x) {
    agents_at_tick <- agent_dt[tick == x]
    proportions <- calculate_proportions(agents_at_tick)
    return(list("proportions" = proportions, "tick" = x))
  })

alcohol_proportions_df <- 
  do.call(rbind, lapply(alcohol_summaries, function(x) {
    df <- x$proportions
    df$Tick <- x$tick
    return(df)
  }
  )
  )

head(alcohol_summaries)
head(alcohol_proportions_df)

tail(alcohol_summaries)
tail(alcohol_proportions_df)


# Compare alcohol use rates in short time frame after release (1 year) --------

fixed_time_after_release <- 365

# filter agents who were released at least once and within one year after release
within_fixed_time_after_release_agents <- agent_dt[last_release_tick > 0 & tick <= last_release_tick + fixed_time_after_release]

# calculate proportions for agents within one year after release
within_fixed_time_after_release_summary <- calculate_proportions(within_fixed_time_after_release_agents)

# display the summary
print("Summary for Agents Within One Year After Release")
print(within_fixed_time_after_release_summary)


# Sensitivity Analysis on parameter of time after release ---------

# time periods in ticks (days): 1 day, 1 week, 2 weeks, 1 month, 3 months, 6 months, 1 year
time_periods <- c(1, 7, 14, 30, 90, 180, 365)

# calculate summaries for each time period
summaries <- lapply(time_periods, function(x)
  summary_after_release(x, agent_dt = agent_dt))

# display summaries
names(summaries) <- paste(time_periods, "days after release")
summaries


# Plot heavy drinking/AUD after release ---------

labels <- c("1D", "1W", "2W", "1M", "3M", "6M", "1Y")
heavy_use_or_AUD_proportions <- sapply(summaries, function(x) sum(x[x$Category == "Cat III", "Proportion"]))
heavy_use_or_AUD_proportions

heavy_use_AUD_df <- data.frame(Time = time_periods,
                               Labels = labels,
                               Proportion = heavy_use_or_AUD_proportions
                               )


# Create a common theme object
common_theme <- theme_minimal() +
  theme(legend.title = element_blank(),
        axis.text.x = element_text(size = 14, face = "bold"),  
        axis.text.y = element_text(size = 14, face = "bold"),  
        legend.text = element_text(size = 14),
        axis.title.x = element_text(size = 16, face = "bold"),
        axis.title.y = element_text(size = 16, face = "bold"),
        plot.margin = margin(10, 10, 10, 10),
        panel.grid.major = element_line(color = "black", linewidth=0.1),  # Set major grid lines to black
        panel.grid.minor = element_line(color = "black", linewidth=0.05)
        ) 

ggplot(heavy_use_AUD_df, aes(x = Time, y = Proportion, group = 1)) +
  geom_line(linewidth=1.5) +
  geom_point() +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  scale_y_continuous(breaks = seq(0, 0.5, 0.1), limits = c(0, 0.5)) +
  labs(title = "",
       x = "Time After Release",
       y = "Proportion of Agents with AUD") +
  common_theme +  # Apply the common theme
  theme(axis.text.x = element_text(angle = 90, hjust = 1))



# Compare Heavy Use/AUD in general population with the post-release group  ---------

# extract rows for heavy use/AUD only
general_heavy_AUD_df <-
  alcohol_proportions_df[alcohol_proportions_df$Category == 'Cat III', ]


# aggregate the heavy/AUD data
combined_proportions <- aggregate(Proportion ~ Tick, data = general_heavy_AUD_df, sum)
head(combined_proportions)

# map the 'Tick' column to the same scale as the original 'heavy_use_AUD_df' dataframe


# compute average of AUD rates for the last 10 ticks
last_combined_rate <- mean(combined_proportions$Proportion[(nrow(combined_proportions) - 9):nrow(combined_proportions)])

# Create a new dataframe with these rates for the time points
last_combined_rate_df <- data.frame(Time = max(heavy_use_AUD_df$Time):365,
                          Proportion = rep(last_combined_rate, 365 - max(heavy_use_AUD_df$Time) + 1))


general_population <- data.frame(
  Time = heavy_use_AUD_df$Time,
  Proportion = last_combined_rate_df$Proportion)




# Plotting both datasets with common theme applied
p <- 
  ggplot() +
  geom_line(data = heavy_use_AUD_df, aes(x = Time, y = Proportion, color = "Previously Incarcerated"), linewidth=1.5) +
  geom_line(data = general_population, aes(x = Time, y = Proportion, color = "Overall"), linewidth=1.5) +
  ylim(c(0, 1)) +
  scale_color_manual(values = c("Previously Incarcerated" = "blue", "Overall" = "red")) +
  common_theme +  # Apply the common theme
  labs(title = "",
       x = "Time After Release",
       y = "Proportion",
       color = "Population") +
  scale_x_continuous(breaks = heavy_use_AUD_df$Time, labels = heavy_use_AUD_df$Labels) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

# Print the plot
p

# Save the plot with 400 DPI
ggsave(filename = here("agent-log-analysis", "multiple-runs", "plots", "post-release-heavy-alcohol.png"), 
       plot = p, 
       width = 10, height = 8, units = "in", dpi = 400)


