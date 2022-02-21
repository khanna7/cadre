# Simulate incarceration 

rm(list=ls())


# Load libraries ---------------------------

library(ergm)
library(tergm)
library(networkDynamic)
library(dplyr)


# Load data ---------------------------

load(file="intialized-network.RData")


# Set up network ---------------------------

sim2_last_TS <- network.collapse(sim2, at=time.slices)
list.vertex.attributes(sim2_last_TS)
table(sim2_last_TS %v% "incarcerated")


n_not_incarcerated <- length(which(sim2_last_TS %v% "incarcerated" == 0))
n_incarcerated <- length(which(sim2_last_TS %v% "incarcerated" == 1))

# Compute probability of incarceration ---------------------------

daily_incarceration_prob <- 1-(0.7)^(1/14) #based on scaling 2-week prob by factor of 100
sentence_duration <- 100 #hypothetical value - replace by Macmadu 2021
daily_release_prob <- 1/sentence_duration

incarceration_coin_flips <- runif(n_not_incarcerated, 0, 1)
release_coin_flips <- runif(n_incarcerated, 0, 1)

prob_location_change <- 1/mig_step
coin_flips <- runif(num_migrant_males, 0, 1)
move <- which(coin_flips <= prob_mig)

# for not incarcerated people, when rand.draw < daily_incarceration_prob,
   # change "incarceration" attribute to 1

# for incarcerated people, when rand.draw < daily_release_prob,
   # change "incarceration" attribute to 0


# for peopl with incarceration history, update smoking probability

# for people in networks of incarceration history, update smoking probability



# Simulate incarceration

