# Analyze incarceration data

rm(list=ls())
  
#renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)
library(dplyr)


# Utility functions ------------

source("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/utils/post-release-alcohol.R")


# Read RDS file ------------

all_instances_data <- readRDS(here("agent-log-analysis", "multiple-runs", "rds-outs", "all_instances_data.RDS"))


# Single instance analysis ------------

# Load data 

agent_dt <- all_instances_data[[1]][["agent_dt"]]
input_params <- all_instances_data[[1]][["input_params"]]


# Ticks of interest 

selected_ticks <- seq(1, max(agent_dt$tick), by = 10)
last_tick <- max(agent_dt$tick)


# Population subsets by release status 
desired_tick=last_tick

all_agents <- agent_dt[tick==desired_tick,] #everyone at all times

never_released_agents <- agent_dt[tick==desired_tick & n_releases == 0] #never release

released_agents <- agent_dt[tick == desired_tick & n_releases >= 1] #released at least once


# Alcohol use state distributions in above subsets 

all_agents_summary <- calculate_proportions(all_agents)
never_released_agents_summary <- calculate_proportions(never_released_agents)
released_agents_summary <- calculate_proportions(released_agents)


# Summarize alcohol use rates in general population 


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


# Compare alcohol use rates in short time frame after release (1 year) 

fixed_time_after_release <- 365

# filter agents who were released at least once and within one year after release
within_fixed_time_after_release_agents <- agent_dt[last_release_tick > 0 & tick <= last_release_tick + fixed_time_after_release]

# calculate proportions for agents within one year after release
within_fixed_time_after_release_summary <- calculate_proportions(within_fixed_time_after_release_agents)

# display the summary
print("Summary for Agents Within One Year After Release")
print(within_fixed_time_after_release_summary)


# Sensitivity Analysis on parameter of time after release 

# time periods in ticks (days): 1 day, 1 week, 2 weeks, 1 month, 3 months, 6 months, 1 year
time_periods <- c(1, 7, 14, 30, 90, 180, 365)

# calculate summaries for each time period
summaries <- lapply(time_periods, function(x)
  summary_after_release(x, agent_dt = agent_dt))

# display summaries
names(summaries) <- paste(time_periods, "days after release")
summaries


# Plot heavy drinking/AUD after release 

labels <- c("1D", "1W", "2W", "1M", "3M", "6M", "1Y")
heavy_use_or_AUD_proportions <- sapply(summaries, function(x) sum(x[x$Category == "Cat III", "Proportion"]))
heavy_use_or_AUD_proportions

heavy_use_AUD_df <- data.frame(Time = time_periods,
                               Labels = labels,
                               Proportion = heavy_use_or_AUD_proportions
                               )


ggplot(heavy_use_AUD_df, aes(x = Time, y = Proportion, group = 1)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  scale_y_continuous(breaks = seq(0, 0.5, 0.1), limits = c(0, 0.5)) +
  labs(title = "",
       x = "Time After Release",
       y = "Proportion of Agents with AUD") +
  theme_minimal()+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))



# Compare Heavy Use/AUD in general population with the post-release group  

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


# Plotting both datasets
p <- 
  ggplot() +
  geom_line(data = heavy_use_AUD_df, aes(x = Time, y = Proportion, color = "Previously Incarcerated"), linewidth=1.5) +
  geom_line(data = general_population, aes(x = Time, y = Proportion, color = "Overall"), linewidth=1.5)+
  ylim(c(0,1))+
  scale_color_manual(values = c("Previously Incarcerated" = "blue", "Overall" = "red")) +
  theme_minimal() +
  labs(title = "",
       x = "Time After Release",
       y = "Proportion",
       color = "Population") +
  scale_x_continuous(breaks = heavy_use_AUD_df$Time, labels = heavy_use_AUD_df$Labels) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1),
        #text = element_text(size = 12, face = "bold"))
        text = element_text(size = 12))
        
p




# Multiple instance analysis ------------

# Initialize lists to store data for each instance
heavy_use_proportions_list <- list()
overall_proportions_list <- list()

# Loop through each instance
# Released population
for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  
  # Existing code for calculating heavy_use_or_AUD_proportions for this instance
  summaries <- lapply(time_periods, function(x) summary_after_release(x, agent_dt = agent_dt))
  heavy_use_or_AUD_proportions <- sapply(summaries, function(x) sum(x[x$Category == "Cat III", "Proportion"]))
  heavy_use_proportions_list[[i]] <- heavy_use_or_AUD_proportions

  }

#########
overall_proportions_list <- list()

# Loop through each instance
for (i in 1:length(all_instances_data)) {
  agent_dt <- all_instances_data[[i]]$agent_dt
  
  # Initialize a vector to store the proportions for this instance
  cat_III_proportions_for_instance <- numeric(length(time_periods))
  
  # Calculate proportions for each time period
  for (j in 1:length(time_periods)) {
    x <- time_periods[j]
    agents_at_tick <- agent_dt[agent_dt$tick == x, ]
    proportion_data <- calculate_proportions(agents_at_tick)
    
    if ("Cat III" %in% proportion_data$Category) {
      cat_III_proportion <- proportion_data[proportion_data$Category == "Cat III", "Proportion"]
    } else {
      cat_III_proportion <- 0  # Default value if "Cat III" is not present
    }
    
    cat_III_proportions_for_instance[j] <- cat_III_proportion
  }
  
  # Add the vector to the list
  overall_proportions_list[[i]] <- cat_III_proportions_for_instance
}


# Extract "Cat III" proportions for the first time period across all instances
cat_III_first_period_proportions <- sapply(overall_proportions_list, `[[`, 1)

# Compute mean and SD for the first time period
cat_III_mean <- mean(cat_III_first_period_proportions, na.rm = TRUE)
cat_III_sd <- sd(cat_III_first_period_proportions, na.rm = TRUE)

# Prepare data frame for plotting
# Note: Only one time period, so Mean and SD are constant across the period
overall_AUD_df <- data.frame(Time = time_periods, Mean = rep(cat_III_mean, length(time_periods)), SD = rep(cat_III_sd, length(time_periods)))



#########

# Aggregate data across instances
heavy_use_aggregated <- do.call(rbind, heavy_use_proportions_list)
heavy_use_mean <- colMeans(heavy_use_aggregated)
heavy_use_sd <- apply(heavy_use_aggregated, 2, sd)


# Plot multiple instance ----------

# Prepare data for ggplot
heavy_use_AUD_df <- data.frame(Time = time_periods,
                               Labels = labels,
                               Mean = heavy_use_mean,
                               SD = heavy_use_sd)

# Plotting with error bars for previously incarcerated
p_prev_inc <- 
  ggplot(heavy_use_AUD_df, aes(x = Time, y = Mean, group = 1)) +
  geom_line(color = "blue") +
  geom_ribbon(aes(ymin = Mean - SD, ymax = Mean + SD), fill = "blue", alpha=0.3) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1))+
  scale_x_continuous(breaks = time_periods, labels = labels) +
  theme_minimal()

p_prev_inc

p_base <- 
  p_prev_inc + 
  geom_hline(yintercept = cat_III_mean, color = "red", linetype = "dashed")+
  geom_ribbon(aes(ymin = cat_III_mean - cat_III_sd, ymax = cat_III_mean + cat_III_sd), fill = "red", alpha=0.3)

p_base


p_legend <- 
  ggplot(heavy_use_AUD_df, aes(x = Time, y = Mean)) +
  geom_line(aes(color = "Previously Incarcerated")) +
  geom_ribbon(aes(ymin = Mean - SD, ymax = Mean + SD, fill = "Previously Incarcerated"), alpha=0.3) +
  geom_hline(aes(yintercept = cat_III_mean, color = "Overall"), linewidth = 1) +
  geom_ribbon(aes(ymin = cat_III_mean - cat_III_sd, ymax = cat_III_mean + cat_III_sd, fill = "Overall"), alpha=0.3) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) +
  scale_x_continuous(breaks = time_periods, labels = labels) +
  scale_color_manual(values = c("Previously Incarcerated" = "blue", "Overall" = "red")) +
  scale_fill_manual(values = c("Previously Incarcerated" = "blue", "Overall" = "red")) +
  theme_minimal() +
  guides(color = guide_legend(title = "Groups"), fill = guide_legend(title = "Groups"))

p_legend

p <- p_legend +  
  labs(title = "",
       x = "Time After Release",
       y = "Proportion of Agents in Category III Alcohol Use",
       color = "Population") +
  theme(
    plot.title = element_text(size = 20, face = "bold"),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    axis.text.x = element_text(size = 10, face = "bold", angle = 90, hjust = 1),
    axis.text.y = element_text(size = 10, face = "bold"),
    legend.title = element_text(size = 16, face = "bold"),
    legend.text = element_text(size = 14),
    axis.ticks.length = unit(0.5, "cm"),
    axis.ticks = element_line(linewidth = 1),
    axis.line = element_line(linewidth = 1.5),
  )
p

ggsave(filename = here("agent-log-analysis", "multiple-runs", "plots", "postrelease_alcohol.png"), 
       plot = p, 
       width = 10, height = 8, units = "in")
