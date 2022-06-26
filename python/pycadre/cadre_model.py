print("This is the Model file")

## model release processes

from numpy import random
import numpy as np
import pandas as pd
from pycadre import cadre_person
from pycadre.load_params import params_list

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
   
    ALC_USE_PROPS = [8.3/100, 72.9/100, 13.2/100, 5.6/100] #see derivation in file:///Volumes/GoogleDrive/My%20Drive/code/cadre/r/explain-population-initialization.nb.html


    def __init__(self, n, verbose=True):
        self.my_persons = [] 
        
        age_sum = 0
        race = []
        females = 0
        alc_use_status = [] 
        smokers = 0 
        n_current_incarcerated = 0
        last_incarceration_time = []
        
        
        # initialize agents and attributes
        for i in range(n):
            person = cadre_person.Person(age=random.randint(18, 65), 
                            race=random.choice(Model.RACE_CATS, p=Model.RACE_DISTRIBUTION),
                            female=random.binomial(1, Model.FEMALE_PROP),
                            alc_use_status=random.choice(range(0, 4), p=Model.ALC_USE_PROPS),
                            smoker=random.binomial(1, Model.SMOKING_PREV),
                            current_incarceration_status=0,
                            last_incarceration_time = -1
                            ) 

            self.my_persons.append(person)
            age_sum = person.age + age_sum
            race.append(person.race) 
            females = person.female + females 
            alc_use_status.append(person.alc_use_status)
            smokers = person.smoker + smokers
            n_current_incarcerated = person.current_incarceration_status + n_current_incarcerated
            last_incarceration_time.append(last_incarceration_time)

            if verbose == True:
                print(person.name)
                print(person.age)
                print(person.alc_use_status, "\n")

        if verbose == True:
            alc_use_status_dist = pd.value_counts(np.array(alc_use_status))/len(alc_use_status)*100
            print("Number of females is: " + 
                str(females))
    
    def run(self, MAXTIME=10):
        
        ages = []
        current_incarceration_statuses = []
        last_incarceration_times = []

        for time in range(MAXTIME):
            
            #if time % 1 == 0:
            print("Timestep = " + str(time))
            print("Number of incarcerated persons at time " + str(time) + " is " + 
                str(sum(current_incarceration_statuses)) + " out of a total " + str(len(ages)))
            print("Last incarceration times are " + str(last_incarceration_times)) 
        
            # ensure that these vectors only hold the agent attributes at the current time 
            # (as opposed to appending) values from all times 
            ages = [] 
            current_incarceration_statuses = []
            last_incarceration_times = []
            
            for person in self.my_persons:
                person.aging()
                ages.append(person.age)
                person.transition_alc_use()
                person.simulate_incarceration(time=time)
                current_incarceration_statuses.append(person.current_incarceration_status)
                last_incarceration_times.append(person.last_incarceration_time)
    
def main():
    model = Model(n=100, verbose=True)
    model.run(MAXTIME=50)
  
if __name__ == "__main__":
    main()
    
        
