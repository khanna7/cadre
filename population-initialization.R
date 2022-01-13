# set up structure for incarceration and smoking

rm(list=ls())


# Libraries ----------

library(ergm)
library(network)


# Initialize Population --------------


n <- 5000
net <- network.initialize(n, directed = FALSE)


# Demographic Initialization --------------

# age (https://censusreporter.org/profiles/04000US44-rhode-island/)
 # lets use age = 18-64
 # 63% of RI population is in this range
 # uniform may not be an unreasonable assumption
age.min <- 18
age.max <- 64
age <- runif(n, age.min, age.max)
net %v% "age" <- age
hist(net %v% "age")

# race (see https://www.census.gov/quickfacts/RI)
white_alone <- 71.4/100 #not hispanic or latino
black_alone <- 8.5/100
hispanic_alone <- 16.3/100
asian_alone <- 3.7/100
other <- 1- sum(c(white_alone, black_alone, asian_alone, hispanic_alone))

race_cats <- c("White", "Black", "Hispanic", "Asian", "Other")

race <- 
  sample(x=race_cats, 
       prob = c(white_alone, black_alone, hispanic_alone, asian_alone, other),
       replace = TRUE,
       size = n
       )
net %v% "race" <- race
table(net %v% "race")


# sex (https://www.census.gov/quickfacts/RI)
female.prop <- 51.3/100
female <- rbinom(n, 1, prob=female.prop)

net %v% "female" <- female
table(net %v% "female")


# Add Smoking Profiles --------------

smoking.prev <- 0.15 
net %v% "smoking.prob" <- smoking.prev
smoking.prob <- net %v% "smoking.prob"
 # assign smoker status after factoring in incareration x race



# Add Alcohol Use Profile --------------
  # parameterize as ordinal variables:
  # "abstainers", "occassional", "regular", "high-risk" (See Apostolopoulos 2017)
  # should alcohol use disorder (AUD) be one of the categories?
  # initial value parameters???


# Initialize incarceration --------------

# 2-week risk #macmadu 2021 (table 1)
incarceration.2week.prob <- 1.7/100
  # we'll break down the above by age and race

# attributes:
  # current location (Correctional Setting vs Home)
  locations <- c("CS", "H")

  curr_loc <- 
    sample(x=locations, 
           prob = c(incarceration.2week.prob, 1-incarceration.2week.prob),
           replace = TRUE,
           size = n
    )
  
   net %v% "curr_loc" <- curr_loc
   table(net %v% "curr_loc")
   
  # ever incarcerated
  ever_inc <- ifelse(curr_loc=="CS", 1, 0) 
  xtabs(~curr_loc + ever_inc)
  net%v% "ever_inc" <- ever_inc
    
  # number of times incarcerated
  num_incs <- ifelse(ever_inc == 1, 1, 0)
  xtabs(~num_incs + ever_inc)
  net %v% "num_incs" <- num_incs
  
  # other predictors of incarceration?
  
  # other parameters:
  #- sentence duration: see macmadu 2021 (Table 1) for male/female distribution
  # recidivism probability: as above

# Initialize housing
  #stably housed persons (https://www.census.gov/quickfacts/RI)
  stably.housed.prop <- 87.4/100
  stably.housed <- rbinom(n, 1, stably.housed.prop)
  table(stably.housed)
  net %v% "stably.housed" <- stably.housed
  
  # correlation between unstable housing and current incarceration
  xtabs(~net %v% "stably.housed" + 
          net %v% "curr_loc")
  
  # correlation between unstable housing and smoking?
  xtabs(~net %v% "stably.housed" + 
          net %v% "smoker")

  
    
# Individual Feedback between incarceration and smoking --------------
  
  # Black men with incarceration history 1.77x as likely to smoke as those w/o inc history
  # Black women with incarceration history 1.61x as likely 
  # (reference: Bailey 2015, AJPH)
  xtabs(~net %v% "race" + net %v%"smoker" +
          net %v% "female")

  mult.black.inc.male.smk <- 1.77 #see above
  mult.black.inc.female.smk <- 1.61 #see above
  
  black.male.idx <- intersect(which(net %v% "race" == "Black"), 
                                   which(net %v% "female" == 0)) 
  black.male.inc.idx <- intersect(black.male.idx, 
                                 (which(net %v% "ever_inc" == 1))) 
  
  black.female.idx <- intersect(which(net %v% "race" == "Black"), 
                             which(net %v% "female" == 1)) 
  black.female.inc.idx <- intersect(black.female.idx, 
                                 (which(net %v% "ever_inc" == 1))) 
  
  smoking.prob[black.male.inc.idx] <- smoking.prev * mult.black.inc.male.smk
  smoking.prob[black.female.inc.idx] <- smoking.prev * mult.black.inc.female.smk
  table(smoking.prob)
  net %v% "smoking.prob" <- smoking.prob
  
  # assign smoker status
  smoker <- rbinom(n, 1, smoking.prob)
  net %v% "smoker" <- smoker
  table(net %v% "smoker") #1= current smoker, 0=former/never smoker
  
# Individual Feedback between incarceration and alcohol use --------------
  # see Tsai 2019 and Fazel 2017

# Smoking-alcohol use association --------------
  

# Initialize Network --------------
  
# persons per househould (https://www.census.gov/quickfacts/RI)
persons.per.household <- 2.47

# structure of networks over which incarceration-related effects will be 
# realized? (within household, between households, unstably housed persons?)


# Smoking Effects in Networks --------------

# parameters:
  # five years of smoking correlated with 1.23x greater odds of smoking 
    #(Howell 2015, Addictive Behaviors)

