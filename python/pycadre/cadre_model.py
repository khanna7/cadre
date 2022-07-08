from numpy import random
import numpy as np
import pandas as pd
from pycadre import cadre_person
import pycadre.load_params as load_params

class Model:
    def __init__(self, n, verbose=True):
        self.my_persons = [] 
        
        # initialize agents and attributes
        for i in range(n):
            person = cadre_person.Person(name = i)    
            self.my_persons.append(person)
    
    def run(self, MAXTIME=10, verbose=True):

        
            for time in range(MAXTIME):

                for person in self.my_persons:
                    person.step(time)
                    
                    if verbose == True:
                        print("Person name: " + str(person.name))
                        print("Person age: ", round(person.age))
                        print("Person race: " + str(person.race))
                        print("Person Female: " + str(person.female))
                        print("Person alcohol use status: " + str(person.alc_use_status))
                        print("Person smoking status: " + str(person.smoker))
                        print("Person last incarceration time: " + str(person.last_incarceration_time))
                        print("Person last release time: " + str(person.last_release_time))
                        print("Person incarceration duration: ", (person.last_release_time - person.last_incarceration_time), "\n")
            
  
