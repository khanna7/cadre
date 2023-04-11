rm(list=ls())

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


# Calculate the percentages to be added to the text
percentage_alcohol_only <- n_alcohol_only
percentage_tobacco_only <- n_tobacco_only
percentage_both <- n_both


# Create the Euler diagram
euler_plot <- euler(data_vector) %>%
  plot(
    labels = c("Alcohol", "Tobacco"),
    fills = c("red", "blue"),
    main = "",
    legend = FALSE
  ) 

# Render the Euler diagram
plot(euler_plot)

# # Add percentages as text to the Venn diagram
# text(x = euler_plot$diagram$coords[1, 1], y = euler_plot$diagram$coords[1, 2], labels = paste0(round(percentage_alcohol_only, 1), "%"), col = "black")
# text(x = euler_plot$diagram$coords[2, 1], y = euler_plot$diagram$coords[2, 2], labels = paste0(round(percentage_tobacco_only, 1), "%"), col = "black")
# text(x = mean(euler_plot$diagram$coords[, 1]), y = mean(euler_plot$diagram$coords[, 2]), labels = paste0(round(percentage_both, 1), "%"), col = "white")
# 
# # Calculate the percentage for neither alcohol nor tobacco
# percentage_neither <- n_neither
# 
# # Add the "neither" percentage as text to the Venn diagram
# # Find an appropriate position for the "neither" label outside the circles
# neither_x <- max(euler_plot$diagram$coords[, 1]) + 0.25
# neither_y <- max(euler_plot$diagram$coords[, 2]) + 0.25
# text(x = neither_x, y = neither_y, labels = paste0("Neither: ", round(percentage_neither, 1), "%"), col = "black")
