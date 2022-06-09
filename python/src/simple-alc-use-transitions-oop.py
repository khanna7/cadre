from pickle import FALSE, TRUE
from tabnanny import verbose
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

        self.name = name    
        self.age = age
        self.race = race
        self.female = female
        self.smoker = smoker
        self.alc_use_status = alc_use_status

    def aging(self):
        TICK_TO_YEAR_RATIO = 365 #xx ticks make a year
        self.age += 1/TICK_TO_YEAR_RATIO

    def simulate_incarceration(self):

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
    


class Model:
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


    def __init__(self, n, verbose=TRUE):
        self.my_persons = [] 
        
        age_sum = 0
        race = []
        females = 0
        alc_use_status = [] 
        smokers = 0 
        
        
        # initialize agents and attributes
        for i in range(n):
            person = Person(age=random.randint(18, 65), 
                            race=random.choice(Model.RACE_CATS, p=Model.RACE_DISTRIBUTION),
                            female=random.binomial(1, Model.FEMALE_PROP),
                            alc_use_status=random.choice(range(0, 4), p=Model.ALC_USE_PROPS),
                            smoker=random.binomial(1, Model.SMOKING_PREV)
                            ) 

            self.my_persons.append(person)
            age_sum = person.age + age_sum
            race.append(person.race) 
            females = person.female + females 
            alc_use_status.append(person.alc_use_status)
            smokers = person.smoker + smokers

            if verbose == TRUE:
                print(person.name)
                print(person.age)
                print(person.alc_use_status, "\n")

        if verbose == TRUE:
            race_dist = pd.value_counts(np.array(race))/len(race)*100
            alc_use_status_dist = pd.value_counts(np.array(alc_use_status))/len(alc_use_status)*100

            print("Number of agents is: " + 
                str(len(self.my_persons)))
            print("Mean agent age is: " + 
                str(('{:.2f}'.format(age_sum/len(self.my_persons)))))
            print("Distribution of race categories is ", "\n" + 
                str(race_dist.round(decimals=2)), "%")
            print("Number of females is: " + 
                str(females))
    
    def run(self, MAXTIME=10):
        
        ages = []

        for time in range(MAXTIME):
            if time % 100 == 0:
                print("Timestep = " + str(time))
                print("Mean age at time " + str(time) + " is " + str(('{:.4f}'.format(np.mean(ages)))))
        
            for person in self.my_persons:
                person.aging()
                ages.append(person.age)
                person.transition_alc_use()

      
                


                


    
def main():
    model = Model(n=10000, verbose=TRUE)
    model.run(MAXTIME=1000)

    


  
if __name__ == "__main__":
    main()
    
        
