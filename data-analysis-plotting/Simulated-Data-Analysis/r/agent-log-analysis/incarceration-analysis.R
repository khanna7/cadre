# Analyze incarceration data (This is from the agent log, there is a separate incarceartion log)
rm(list=ls())


# Load R environment ---------

renv::activate()


# Load packages ---------

library(here)
library(data.table)
library(yaml)
library(ggplot2)


# Read RDS file ------------

#agent_log_env <- readRDS(here("agent-analysis", "rds-outs", "agent_log_env.RDS"))
agent_log_env <- readRDS("/users/akhann16/code/cadre/data-analysis-plotting/Simulated-Data-Analysis/r/agent-log-analysis/rds-outs/agent_log_env.RDS")


# Load data ------------

agent_dt <- agent_log_env[["agent_dt"]]
input_params <- agent_log_env[["input_params"]]


# Summary ------------

last_tick <- max(agent_dt$tick)
selected_ticks <- c(seq(1, last_tick, by = 10), last_tick)

# mean incarceration rate over time
incarceration_summary <- agent_dt[tick %in% selected_ticks, 
                                  .(n_incarcerated = sum(current_incarceration_status == 1),
                                    n_agents = .N), 
                                  by = tick]

incarceration_summary[, rate_per_100k := n_incarcerated / n_agents * 100000]

ggplot(incarceration_summary, aes(x = tick, y = rate_per_100k)) +
  geom_line() +
  theme_minimal() +
  labs(title = "",
       x = "Time (Days)",
       y = "Incarceration Rate (per 100,000 persons)")+
  theme(text = element_text(size = 20, face = "bold"))+
  ylim(c(0,500))


# number incarcerated
ggplot(incarceration_summary, aes(x = tick, y = n_incarcerated)) +
  geom_line() +
  theme_minimal() +
  labs(title = "",
       x = "Time (Days)",
       y = "Number Incarcerated")


# Last tick analysis ----------

# number and proportion of incarcerated persons at last tick:
incarceration_summary <- agent_dt[tick %in% selected_ticks, 
                                  .(n_incarcerated = sum(current_incarceration_status == 1),
                                    n_agents = .N), 
                                  by = tick]
tail(incarceration_summary)

# race distribution
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("race")][,"prop":=round(N/sum(N)*100, 0)][]

# sex distribution
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("female")][,"prop":=round(N/sum(N)*100, 0)][]


# race-sex distribution
agent_dt[tick==last_tick & current_incarceration_status == 1, 
         .N, 
         by=c("race", "female")][,"prop":=round(N/sum(N)*100, 0)][]





# Ever incarcerated ----------

# how many?

# To answer this question, we can group the last incarceration times by agent ID.
# If last incarceration time is -1, the person has never been incarcerated. 
# If last incarceration time is > -1, the person has been incarcerated at least once. 

last_incarceration_time <- agent_dt[, 
                                    .(last_incarceration_time = max(last_incarceration_tick)), 
                                    by = id]

n_ever_incarcerated <- sum(last_incarceration_time$last_incarceration_time != -1)

prop_ever_incarcerated <- n_ever_incarcerated / nrow(last_incarceration_time)


# agent-level analysis of those ever incarcerated 

ever_incarcerated_times <- last_incarceration_time[last_incarceration_time > 1]
dim(ever_incarcerated_times)

## demographics

### generate dataset
ever_incarcerated_ids <-
  unique(agent_dt[id %in% ever_incarcerated_times$id, id])
ever_incarcerated_info <- agent_dt[id %in% ever_incarcerated_ids,
                                   .SD[.N, list(
                                     id,
                                     age = last(age),
                                     race = last(race),
                                     female = last(female)
                                   )],
                                   by = id]


### create distributions

ever_incarcerated_info[,#age 
                       .(
  mean_age = mean(age),
  min_age = min(age),
  max_age = max(age)
)]

sex_incarcerated_proportion <- 
  ever_incarcerated_info[, .(
    Count = .N,
    Proportion = round(.N / nrow(ever_incarcerated_info), 2)
  ), 
  by = .(Sex = ifelse(female==1, "Female", "Male"))
  ]

race_incarcerated_proportion <- 
  ever_incarcerated_info[, .(
  Count = .N,
  Proportion = round(.N / nrow(ever_incarcerated_info), 2)
  ), 
  by = .(Race=race)]

race_sex_incarcerated_proportion <- 
  ever_incarcerated_info[, .N, by = c("race", "female")][
    #race, sex
    ,
    .(Race = race,
      Sex = ifelse(female == 1, "Female", "Male"),
      Count = N,
      Proportion = round(N / sum(N), 2)
    )[order(c(female, race))]
  ]


# Race/Sex distribution in full population ----------

## defined as  % group representation in incarcerated population
## relative to to representation in general population

unique_agents <- unique(agent_dt, by = "id")
dim(unique_agents)
str(unique_agents)

race_population_proportion <- 
  unique_agents[, .(
                Count = .N,
                Proportion = round(.N/nrow(unique_agents), 2)
                ),
              by = .(Race = race)
              ]

sex_population_proportion <-
  unique_agents[, .(
  Count = .N,
  Proportion = round(.N/nrow(unique_agents), 2)
  ),
  by = .(Sex = ifelse(female==1, "Female", "Male"))
  ]

race_sex_population_proportion <- 
  unique_agents[, .N, by = c("race", "female")][
    #race, sex
    ,
    .(Race = race,
      Sex = ifelse(female == 1, "Female", "Male"),
      Count = N,
      Proportion = round(N / sum(N), 2)
    )[order(c(female, race))]
  ]



# Disparity analysis ---------

## race-sex combined
disparity_analysis <- merge(
  race_sex_incarcerated_proportion,
  race_sex_population_proportion,
  by = c("Race", "Sex"),
  suffixes = c("_Incarcerated", "_Population")
)


disparity_analysis[, Disparity_Ratio := round(Proportion_Incarcerated / Proportion_Population, 2)]
disparity_analysis <- disparity_analysis[order(-Disparity_Ratio)]
disparity_analysis


## race only
disparity_analysis_race <- merge(
  race_incarcerated_proportion,
  race_population_proportion,
  by = c("Race"),
  suffixes = c("_Incarcerated", "_Population")
)


disparity_analysis_race[, Disparity_Ratio := round(Proportion_Incarcerated / Proportion_Population, 2)]
disparity_analysis_race[order(-Disparity_Ratio)]


## sex only
disparity_analysis_sex <- merge(
  sex_incarcerated_proportion,
  sex_population_proportion,
  by = c("Sex"),
  suffixes = c("_Incarcerated", "_Population")
)


disparity_analysis_sex[, Disparity_Ratio := round(Proportion_Population / Proportion_Incarcerated, 2)]
disparity_analysis_sex[order(-Disparity_Ratio)]


# Visualizing incarceration disparity by sex and race -----------

# sex
sex_data <- data.frame(
  Sex = rep(c("Female", "Male"), each = 2),
  Count = c(43, 8080, 527, 7622),
  Proportion = c(0.08, 0.51, 0.92, 0.49),
  PopulationType = rep(c("Incarcerated", "General"), 2)
)

ggplot(sex_data, aes(x = Sex, y = Proportion, fill = PopulationType)) +
  geom_bar(stat = "identity", position = position_dodge()) +
  scale_fill_manual(values = c("General" = "blue", "Incarcerated" = "red")) +
  scale_y_continuous(breaks = seq(0, 1, 0.25), limits = c(0, 1))+
  labs(title = "",
       x = "Sex",
       y = "Proportion",
       fill = "Population Type") +
  theme_minimal()+
  theme(text=element_text(face = "bold", size = 20))


# race 
race_data <- data.frame(
  Race = rep(c("Black", "Hispanic", "White", "Asian"), each = 2),
  Count = c(188, 1310, 123, 2580, 254, 11214, 5, 598),
  Proportion = c(0.33, 0.08, 0.22, 0.16, 0.45, 0.71, 0.01, 0.04),
  PopulationType = rep(c("Incarcerated", "General"), 4)
)

ggplot(race_data, aes(x = Race, y = Proportion, fill = PopulationType)) +
  geom_bar(stat = "identity", position = position_dodge()) +
  scale_fill_manual(values = c("General" = "blue", "Incarcerated" = "red")) +
  scale_y_continuous(breaks = seq(0, 1, 0.25), limits = c(0, 1))+
  labs(title = "",
       x = "Race",
       y = "Proportion",
       fill = "Population Type") +
  theme_minimal()+
  theme(text=element_text(face="bold", size=20))

# current smoking

race_data <- data.frame(
  Race = rep(c("Black", "Hispanic", "White", "Asian"), each = 2),
  Count = c(188, 1310, 123, 2580, 254, 11214, 5, 598),
  Proportion = c(0.33, 0.08, 0.22, 0.16, 0.45, 0.71, 0.01, 0.04),
  PopulationType = rep(c("Incarcerated", "General"), 4)
)


# Visualize incarceration disparity by smoking  -----------

incarcerated <- 
  agent_dt[tick %in% selected_ticks & current_incarceration_status==1, 
           .N, 
           by=c("smoking_status")][,"prop":=round(N/sum(N), 3)][order(smoking_status)]

incarcerated$group <- "Incarcerated"

general_pop <- 
  agent_dt[tick %in% selected_ticks, 
           .N, 
           by=c("smoking_status")][,"prop":=round(N/sum(N), 3)][order(smoking_status)]
general_pop$group <- "General"

combined_data <- rbind(incarcerated, general_pop)
combined_data$smoking_status <- factor(combined_data$smoking_status, 
                                       levels = c("Current", "Former", "Never"))


ggplot(combined_data, aes(x = smoking_status, y = prop, fill = group)) +
  geom_bar(stat = "identity", position = position_dodge()) +
  scale_fill_manual(values = c("General" = "blue", "Incarcerated" = "red")) +
  labs(title = "",
       x = "Smoking Status",
       y = "Proportion (%)",
       fill = "Population Type")+
  ylim(c(0,1))+
  theme_minimal() +
  theme(text = element_text(size = 20, face = "bold"))


# Visualize incarceration disparity by alcohol status -----------

incarcerated2 <- 
  agent_dt[tick %in% selected_ticks & current_incarceration_status == 1, 
         .N, 
         by=c("alc_use_status")][,"prop":=round(N/sum(N), 3)][order(alc_use_status)]

incarcerated2$group <- "Incarcerated"

general_pop2 <- 
  agent_dt[tick %in% selected_ticks, 
           .N, 
           by=c("alc_use_status")][,"prop":=round(N/sum(N), 3)][order(alc_use_status)]
general_pop2$group <- "General"

combined_data2 <- rbind(incarcerated2, general_pop2)


ggplot(combined_data2, aes(x = alc_use_status, y = prop, fill = group)) +
  geom_bar(stat = "identity", position = position_dodge()) +
  scale_fill_manual(values = c("General" = "blue", "Incarcerated" = "red")) +
  labs(title = "",
       x = "Alcohol Use",
       y = "Proportion (%)",
       fill = "Population Type")+
  ylim(c(0,1)) +
  theme_minimal() +
  theme(text = element_text(size = 20, face = "bold"))
 