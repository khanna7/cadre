print("This is the Model file")

from numpy import random
import numpy as np
import pandas as pd
from pycadre import cadre_person
from pycadre.load_params import params_list
from collections import Counter

PROBABILITY_DAILY_INCARCERATION = params_list['PROBABILITY_DAILY_INCARCERATION']
SENTENCE_DURATION = params_list['SENTENCE_DURATION']

class Model:

    #params_list = load_params.params_list

    RACE_CATS = params_list['RACE_CATS']
    RD = params_list['RACE_DISTRIBUTION']
    RACE_DISTRIBUTION = [
        RD['White'],
        RD['Black'],
        RD['Hispanic'], 
        RD['Asian']
    ]
    
    SMOKING_PREV = params_list['SMOKING_PREV']
    FEMALE_PROP = params_list['FEMALE_PROP']
   
    #print("daily inc prob: " + str(PROBABILITY_DAILY_INCARCERATION))
    
   
    #ALC_USE_PROPS = [8.3/100, 72.9/100, 13.2/100, 5.6/100] #see derivation in file:///Volumes/GoogleDrive/My%20Drive/code/cadre/r/explain-population-initialization.nb.html


    def __init__(self, n, verbose=True):
        self.my_persons = [] 
        
        name = []
        age_sum = 0
        race = []
        females = 0
        alc_use_status = [] 
        smokers = 0 
        n_current_incarcerated = 0
        last_incarceration_time = []
        incarceration_duration = []
        last_release_time = []

        
        
        # initialize agents and attributes
        for i in range(n):
            person = cadre_person.Person(name = i) 

            self.my_persons.append(person)
            name.append(person.name)
            age_sum = person.age + age_sum
            race.append(person.race) 
            females = person.female + females 
            alc_use_status.append(person.alc_use_status)
            smokers = person.smoker + smokers
            n_current_incarcerated = person.current_incarceration_status + n_current_incarcerated
            last_incarceration_time.append(last_incarceration_time)
            incarceration_duration.append(incarceration_duration)
            last_release_time.append(last_release_time)

            if verbose == True:
                print("Person name: " + str(person.name))
                print("Person age: " + str(person.age))
                print("Person alcohol use status: " + str(person.alc_use_status))
                print("Person last incarceration time: " + str(person.last_incarceration_time))
                print("Person last release time: " + str(person.last_release_time), "\n")

        if verbose == True:
            alc_use_status_dist = pd.value_counts(np.array(alc_use_status))/len(alc_use_status)*100
            print("Number of females is: " + 
                str(females))
    
    def run(self, MAXTIME=10):
            
            ages = [] 
            current_incarceration_statuses = []
            last_incarceration_times = []
            last_release_times = []
            current_alcohol_stage = []
        
            for time in range(MAXTIME):

            ## model run checks 
                print("Timestep = " + str(time))
                print("Number of incarcerated persons at time " + str(time) + " is " + 
                    str(sum(current_incarceration_statuses)) + " out of a total " + str(len(ages)))
                print("Last incarceration times are " + str(last_incarceration_times)) 
                print("Last release times are " + str(last_release_times), "\n") 
                print("alcohol usage is" + str(Counter(current_alcohol_stage)))

            # ensure that these vectors only hold the agent attributes at the current time 
            # (as opposed to appending) values from all times 
                ages = [] 
                current_incarceration_statuses = []
                last_incarceration_times = []
                last_release_times = []
                current_alcohol_stage = []

                for person in self.my_persons:
                    person.aging()
                    ages.append(person.age)
                    person.transition_alc_use()
                    person.simulate_incarceration(time=time, probability_daily_incarceration=PROBABILITY_DAILY_INCARCERATION)
                    person.simulate_release(time=time, sentence_duration=SENTENCE_DURATION)
                    current_alcohol_stage.append(person.alc_use_status)
                    current_incarceration_statuses.append(person.current_incarceration_status)
                    last_incarceration_times.append(person.last_incarceration_time)
                    last_release_times.append(person.last_release_time)
    
def main():
    model = Model(n=100, verbose=True)
    model.run(MAXTIME=50)
  
if __name__ == "__main__":
    main()
    
        
