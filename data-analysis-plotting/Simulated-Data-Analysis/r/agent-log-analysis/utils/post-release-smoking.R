# Compute change in current smoking rate over time since release ----------

calculate_proportions_smoking <- function(data) {
  proportions <- prop.table(table(data$smoking_status))
  df <- data.frame(Category = names(proportions),
                   Proportion = as.numeric(proportions))
  df$Category <- factor(df$Category,
                        levels = c("Never", "Former", "Current"),
                        labels = c("Never", "Former", "Current"))
  return(df)
}

summary_after_release <- function(time_period) {
  agents_within_time_period <- agent_dt[last_release_tick > 0 &
                                          tick - last_release_tick <= time_period]
  
  proportions <- calculate_proportions_smoking(agents_within_time_period)
  agent_count <- nrow(agents_within_time_period)
  return(list("proportions" = proportions, "agent_count" = agent_count))
}