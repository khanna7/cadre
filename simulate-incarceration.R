# Simulate incarceration 

rm(list=ls())


# Load libraries ---------------------------

library(ergm)
library(tergm)
library(networkDynamic)
library(dplyr)


# Load data ---------------------------

load(file="intialized-network.RData")

# Common Functions ---------------------------
source("common-functions.R")

# Set up network ---------------------------

pop_net <- network.collapse(sim2, at=time.slices)
list.vertex.attributes(pop_net)
table(pop_net %v% "incarcerated")


n_not_incarcerated <- length(which(pop_net %v% "incarcerated" == 0))
n_incarcerated <- length(which(pop_net %v% "incarcerated" == 1))

# Simulate incarceration and release ---------------------------

## incarceration parameters
daily_incarceration_prob <- 1-(0.7)^(1/14) #based on scaling 2-week prob by factor of 100
sentence_duration <- 10 #hypothetical value - replace by Macmadu 2021
incarceration_coin_flips <- runif(n_not_incarcerated, 0, 1)

## release parameters
daily_release_prob <- 1/sentence_duration
release_coin_flips <- runif(n_incarcerated, 0, 1)

## for not incarcerated people, when incarceration_coin_flips < daily_incarceration_prob,
   # update "incarceration" attribute to 1
   # if ever_inc == 0, update "ever_inc" to 1
   # increment num_incs by 1
incarcerate <- which(incarceration_coin_flips < daily_incarceration_prob)
   
   # identify newly incarcerated individuals
newly_incarcerated_ids <- intersect(which(pop_net %v% "ever_inc" == 0), incarcerate)

table(ever_inc, exclude=NULL) #measure: pre
ever_inc[newly_incarcerated_ids] = 1
table(ever_inc, exclude=NULL) #measure: post

num_incs[newly_incarcerated_ids] = num_incs[newly_incarcerated_ids]+1

set.vertex.attribute(pop_net, "incarcerated", v=incarcerate, value = 1)
set.vertex.attribute(pop_net, "ever_inc", v=newly_incarcerated_ids, value = 1)
set.vertex.attribute(pop_net, "num_incs", v=newly_incarcerated_ids, value = num_incs)

## for incarcerated people, when rand.draw < daily_release_prob,
   # update "incarceration" attribute to 0
newly_released_ids <- which(release_coin_flips < daily_release_prob)
set.vertex.attribute(pop_net, "incarceration", v=newly_released_ids, value = 0)

## test values
xtabs(~ factor(pop_net %v% "incarceration", exclude=NULL)+
        factor(pop_net %v% "num_incs", exclude=NULL))
xtabs(~ factor(pop_net %v% "incarceration", exclude=NULL)+
        factor(pop_net %v% "ever_inc", exclude=NULL))
xtabs(~ factor(pop_net %v% "num_incs", exclude=NULL)+
        factor(pop_net %v% "ever_inc", exclude=NULL))

# Update smoking probability for newly released Black men and women ---------------------------
# (reference: Bailey 2015, AJPH)

summary((pop_net%v%"smoking.prob")[newly_incarcerated_ids])

newly_rel_black_male <- 
   intersect_all(which(pop_net %v% "race" == "Black"), 
                 which(pop_net %v% "female" == 0),
                 newly_released_ids
   )

newly_rel_black_female <- 
   intersect_all(which(pop_net %v% "race" == "Black"), 
                 which(pop_net %v% "female" == 1),
                 newly_released_ids
   )

smoking.prob[newly_rel_black_male] <- smoking.prev * mult.black.inc.male.smk
smoking.prob[newly_rel_black_female] <- smoking.prev * mult.black.inc.female.smk

# Update smoking probability for newly released non-Black men and women ---------------------------
  # see Ahalt 2019: https://www.dropbox.com/s/xjcx45h293nobgl/Ahalt2019.pdf?dl=0

# for people in networks of incarceration history, update smoking probability



# Simulate incarceration

