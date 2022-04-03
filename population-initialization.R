#INITIALIZE POPULATION
# set up structure for incarceration and smoking

rm(list=ls())


# Libraries ----------

library(ergm)
library(network)
library(dplyr)


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
  # "abstainers", "occassional", "regular", "high-risk/AUD" (See Apostolopoulos 2017)
  # initial value parameters???
  # See National Comorbidity Survey Replication, Kalaydjian 2009 et al: 
  # (https://www.dropbox.com/s/cod0ojty84xa00y/Kalaydijan2009-alcoholuse-state-transitions.pdf?dl=0)
    # (A) 91.7% (SE=0.9) reported >1 sip of alcohol at some time in their life, 
    # (B) 72.9% (1.3) reported using alcohol regularly at some time in their life
    # (C) 13.2% (0.6) met criteria for alcohol abuse at some time in their life, and 
    # (D) 5.4% (0.3) met criteria for alcohol dependence at some time in their life.
 # so, we derive 1-A = 8.3% as abstainers
 # For simplicity, let us assume Occasional = B, Regular = C, 
 # & High-Risk/AUD = 1-(A+B+C) = 5.6 (which is almost the same as D)

alcohol_abstainers <- 8.3/100
alcohol_occasional_users <- 72.9/100
alcohol_regular_users <- 13.2/100
alcohol_dep <- 1 - (alcohol_abstainers+alcohol_occasional_users+alcohol_regular_users)

alcohol_cats <- c("abstainer", "occasional_user", 
                  "regular_user", "dependence/AUD")

alcohol_props <- c(alcohol_abstainers, alcohol_occasional_users,
                    alcohol_regular_users, alcohol_dep)

alcohol_use_state <- sample(alcohol_cats, alcohol_props, replace = TRUE, size=n)

table(alcohol_use_state, exclude = NULL)

net %v% "alcohol_use_state" <- alcohol_use_state

table(net %v% "alcohol_use_state")

## For now, assume that transitions between use states do not occur.


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
  
  incarcerated <- recode(curr_loc, "H" = "0", "CS" = "1")
  incarcerated <- as.numeric(incarcerated)
  table(incarcerated)
  
  net %v% "curr_loc" <- curr_loc
  table(net %v% "curr_loc")
  
  net %v% "incarcerated" <- incarcerated
  table(net %v% "incarcerated")
  
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
  # see meta analysis Fazel 2017: https://www.dropbox.com/s/tpe2hb49csizrpr/Fazel2017.pdf?dl=0
  # (and Tsai 2019)

# Smoking-alcohol use association --------------
  # From, Tsai 2019, 
  # p1 = % of persons with AUD w no incarceration history = 7550/8183
  # p2 = % of persons with AUD w incarceration history = 2388/2670
  # OR for AUD with incarceration to no incarceration = (p2/1-p2)/(p1/1-p1) = 0.71
  # (paper gives this ratio as 0.75)
  
  # Taking p1 = 5.6% (from National Comorbidity Survey Replication, 
    # Kalaydjian 2009) we solve for p2.
  
  # Solving the above equation, with RHS = 0.75 (as in the paper), 
    # and setting p1=5.6%, give p2=21/493 = 0.0423.
    # ie., % of persons with AUD who have incarceration history is 4.3%.

  # What about % of persons with incarceration history who have AUD?
    # See Chamberlain et al https://ascpjournal.biomedcentral.com/articles/10.1186/s13722-019-0136-6
    # See support for reduced post-release (relative to pre-incarceration) alcohol use: 
      # Tangney 2016 https://www.dropbox.com/s/8qggviinrt4lzoi/Tangney2016.pdf?dl=0   
  
  # simulate feedback between AUD and incarceration

  
  
# Initialize Network --------------
  
# persons per househould (https://www.census.gov/quickfacts/RI)
persons.per.household <- 2.47

# structure of networks over which incarceration-related effects will be 
# realized? (within household, between households, unstably housed persons?)


# Smoking Effects in Networks --------------

## See following paper:
   # Schaefer DR, Adams J, Haas SA. Social networks and smoking
      # Health Educ Behav. 2013 Oct;40(1 Suppl):24S-32S. PMID: 24084397; and
   # Adams J, Schaefer DR. How Initial Prevalence Moderates Network-based Smoking Change
      # J Health Soc Behav. 2016 Mar;57(1):22-38. PMID: 26957133; AND
  # Haynie DL, Whichard C, Kreager DA, Schaefer DR, Wakefield S. Social Networks and Health in a Prison Unit. 
      #J Health Soc Behav. 2018 Sep;59(3):318-334. Epub 2018 Aug 2. PMID: 30070603.
  
# parameters:
  # five years of smoking correlated with 1.23x greater odds of smoking 
    #(Howell 2015, Addictive Behaviors)

# Save Object --------------
save.image(file="init-population.RData")
