# Function to calculate proportions
calculate_proportions <- function(data) {
  proportions <- prop.table(table(data$alc_use_status))
  df <- data.frame(Category = names(proportions),
                   Proportion = as.numeric(proportions))
  df$Category <- factor(df$Category,
                        levels = c(0, 1, 2, 3),
                        labels = c("Lifetime Abstention", "Low-Risk Use", "Heavy Use", "AUD"))
  return(df)
}

# Function to filter agents and calculate proportions for the given time period after release
summary_after_release <- function(time_period) {
  agents_within_time_period <- agent_dt[last_release_tick > 0 & tick <= last_release_tick + time_period]
  proportions <- calculate_proportions(agents_within_time_period)
  return(proportions)
}

# Time periods in ticks (days): 1 day, 1 week, 2 weeks, 1 month, 3 months, 6 months, 1 year
time_periods <- c(1, 7, 14, 30, 90, 180, 365)

# Calculate summaries for each time period
summaries <- lapply(time_periods, function(x) summary_after_release(x))

# Display summaries
names(summaries) <- paste(time_periods, "days after release")
summaries