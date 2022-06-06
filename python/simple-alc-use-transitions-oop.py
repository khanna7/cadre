from pickle import FALSE, TRUE
from numpy import random
import numpy as np
import pandas as pd

class Person():
    def __init__(self, 
    name=None, 
    age=None, 
    race=None, 
    female=None,
    smoker=None, 
    alc_use_status=None):


        RACE_DISTRIBUTION = [
            71.4/100, #white alone
            8.5/100, #black alone
            16.3/100, #hispanic alone
            3.8/100 #asian alone (increased by 0.1 to sum to 1)
            # REF: https://censusreporter.org/profiles/04000US44-rhode-island/
        ]
        RACE_CATS = ["white", "black", "hispanic", "other"]
        SMOKING_PREV = 0.13 #REF: https://www.cdc.gov/tobacco/data_statistics/fact_sheets/adult_data/cig_smoking/index.htm
        FEMALE_PROP = 51.3/100 # REF: https://www.census.gov/quickfacts/RI
        ALC_USE_PROPS = [8.3/100, 72.9/100, 13.2/100, 5.6/100] #see derivation in file:///Volumes/GoogleDrive/My%20Drive/code/cadre/r/explain-population-initialization.nb.html


        if age == None:
            age = random.randint(18, 65)

        if race == None:
            race = random.choice(RACE_CATS, p=RACE_DISTRIBUTION)

        if female == None:
            female = random.binomial(1, FEMALE_PROP)

        if alc_use_status == None:
            alc_use_status = random.choice(range(0, 4), p=ALC_USE_PROPS) 
        
        if smoker == None:
            smoker = random.binomial(1, SMOKING_PREV)
    
        self.name = name    
        self.age = age
        self.race = race
        self.female = female
        self.smoker = smoker
        self.alc_use_status = alc_use_status

    def transition_alc_use(self):

        # level up
        TRANS_PROB_0_1 = 0/100 
        TRANS_PROB_1_2 = 1/100
        TRANS_PROB_2_3 = 1/100
        # LEVEL DOWN
        TRANS_PROB_1_0 = 0.5/100
        TRANS_PROB_2_1 = 0.5/100
        TRANS_PROB_3_2 = 0.5/100

        changes = 0
        prob = random.uniform(0, 1)
        if self.alc_use_status == 0:
            if (prob <= TRANS_PROB_0_1):
                self.alc_use_status += 1
                changes+=1
                #print("change!")

        elif self.alc_use_status == 1:
            if (prob <= TRANS_PROB_1_2):
                self.alc_use_status += 1
                changes+=1
                #print("change!")
            elif (prob > 1-TRANS_PROB_1_0):
                self.alc_use_status -= 1
                changes += 1
                #print("change!")
        
        elif self.alc_use_status == 2:
            if (prob <= TRANS_PROB_2_3):
                self.alc_use_status += 1
                changes += 1
                #print("change!")
            elif (prob > 1-TRANS_PROB_2_1):
                self.alc_use_status -= 1
                changes += 1
                #print("change!")

        elif self.alc_use_status == 3:
            if (prob > 1-TRANS_PROB_3_2):
                self.alc_use_status -= 1
                changes += 1
                #print("change!")

def initialize_population(n, verbose=TRUE):
    my_persons = [] 
    age_sum = 0
    race = []
    females = 0
    alc_use_status = [] 
    smokers = 0 

   
    
    # initialize agents and attributes
    for i in range(n):
        my_persons.append(Person(i))
        age_sum = my_persons[i].age + age_sum
        race.append(my_persons[i].race) 
        females = my_persons[i].female + females 
        alc_use_status.append(my_persons[i].alc_use_status)
        smokers = my_persons[i].smoker + smokers
       
        
        if verbose == TRUE:
            print(my_persons[i].name)
            print(my_persons[i].age)
            print(my_persons[i].alc_use_status, "\n")

    if verbose == TRUE:
        race_dist = pd.value_counts(np.array(race))/len(race)*100
        alc_use_status_dist = pd.value_counts(np.array(alc_use_status))/len(alc_use_status)*100

        print("Number of agents is: " + 
            str(len(my_persons)))
        print("Mean agent age is: " + 
            str(('{:.2f}'.format(age_sum/len(my_persons)))))
        print("Distribution of race categories is ", "\n" + 
            str(race_dist.round(decimals=2)), "%")
        print("Number of females is: " + 
            str(females))
        print("Distribution of alcohol use categories is ", "\n" + 
            str(alc_use_status_dist.round(decimals=2)), "%")
        print("Max level of alcohol use is " + 
            str(max(alc_use_status)))
        print("Min level of alcohol use is " + 
            str(min(alc_use_status)))
        print("Median level of alcohol use is " + 
            str(np.median(alc_use_status)))
        print("Number of smokers is " + 
            str(smokers))
      

    return my_persons

    
def main():
    persons = initialize_population(n=10001, verbose=TRUE) 

    MAXTIME=100
    
    for time in range(MAXTIME):
        if time % 10 == 0:
            print("Timestep = " + str(time))
        
        for person in persons:
            person.transition_alc_use()


  
if __name__ == "__main__":
    main()
    
        
