rm(list=ls())

# Load the eulerr package
library(eulerr)
library(magrittr)
library(grid)

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
    labels = c("", ""),
    fills = c("red", "blue"),
    main = "",
    legend = FALSE
  ) 

# Render the Euler diagram
plot(euler_plot)

# Add the percentage text to the Euler diagram (manually adjust the x and y coordinates)
grid.text(paste0("Alcohol: ", percentage_alcohol_only, "%"), x = 0.38, y = 0.5, 
          default.units = "npc", gp = gpar(col = "white", fontsize = 10))
grid.text(paste0("Tob:", percentage_tobacco_only, "%"), x = 0.76, y = 0.5,
          default.units = "npc", gp = gpar(col = "white", fontsize = 10))
grid.text(paste0("Both: ", percentage_both, "%"), x = 0.6, y = 0.5, 
          default.units = "npc", gp = gpar(col = "white", fontsize = 10))

# Add the percentage text for Neither
grid.text(paste0("Neither: ", n_neither, "%"), x = 0.72, y = 0.8, 
          default.units = "npc", gp = gpar(col = "black", fontsize = 10))




