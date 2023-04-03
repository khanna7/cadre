# Load the eulerr package
library(eulerr)
library(magrittr)

# Define the data: Falk 2006 (NESARC)

# non-derived (table 1)
n_neither <- 28.6  
n_both <- 21.7
n_any_alcohol <- 65.4
n_any_tobacco <- 27.7

# derived  
n_alcohol_only <- n_any_alcohol - n_both
n_tobacco_only <- n_any_tobacco - n_both


# Calculate counts for Alcohol, Tobacco, and Both
total_population <- 1000 # Assuming a population of 1000 for integer values
count_alcohol_only <- round(total_population * n_alcohol_only / 100)
count_tobacco_only <- round(total_population * n_tobacco_only / 100)
count_both <- round(total_population * n_both / 100)

# Create a named vector with the data
data_vector <- c(
  "Alcohol" = count_alcohol_only,
  "Tobacco" = count_tobacco_only,
  "Alcohol&Tobacco" = count_both
)

# Create the Euler diagram
euler_plot <- euler(data_vector) %>%
  plot(
    labels = c("Alcohol", "Tobacco"),
    fills = c("red", "blue"),
    main = "",
    legend = FALSE
  )

# Display the Euler diagram
euler_plot
