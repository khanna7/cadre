import unittest
import numpy as np
import pandas as pd
import sys
import os 

from pycadre import cadre_model
#from pycadre import cadre_person 


class TestPerson(unittest.TestCase):

    def test_age_assignment(self):
        ages = []
        min_age = 18
        max_age = 64
        mean_age_target = (min_age+max_age)/2

        model = cadre_model.Model(n=1000, verbose=False)    
        model.run(MAXTIME=0)
                   
        for person in model.my_persons:
                ages.append(person.age)

        for age in ages: 
            self.assertTrue(age >= min_age)
            self.assertTrue(age <= max_age)
            self.assertAlmostEqual(np.mean(ages), mean_age_target, delta=1)

    def test_race_assignment(self):
        RACE_DISTRIBUTION = [
        71.4, #white alone
        8.5, #black alone
        16.3, #hispanic alone
        3.8 #asian alone (increased by 0.1 to sum to 1)
        # REF: https://censusreporter.org/profiles/04000US44-rhode-island/
    ]
        races = []
        model = cadre_model.Model(n=1000, verbose=False)
        model.run(MAXTIME=0)
                   
        for person in model.my_persons:
                races.append(person.race)

        #print("Races: "  + str(races))
        race_dist = pd.value_counts(np.array(races))/len(races)*100
        #print("Races: " + str(race_dist))

        self.assertAlmostEqual(race_dist.white, RACE_DISTRIBUTION[0], delta=2)
        self.assertAlmostEqual(race_dist.black, RACE_DISTRIBUTION[1], delta=2)
        self.assertAlmostEqual(race_dist.hispanic, RACE_DISTRIBUTION[2], delta=2)
        self.assertAlmostEqual(race_dist.other, RACE_DISTRIBUTION[3], delta=2)

    ## test alcohol use assignment

    ## test alcohol status transition

    def test_aging(self):
        ages_init = []
        ages_final = []
        TICK_TO_YEAR_RATIO = 365 #xx ticks make a year
        nsteps = 100


        model = cadre_model.Model(n=1000, verbose=False)
        model.run(MAXTIME=0)                   
        for person in model.my_persons:
                ages_init.append(person.age)

        model.run(MAXTIME=nsteps)
        for person in model.my_persons:
                ages_final.append(person.age)

        diff_in_ages = np.subtract(np.array(ages_final), np.array(ages_init))

        self.assertAlmostEqual(np.mean(diff_in_ages), 1/TICK_TO_YEAR_RATIO*nsteps)

    
    def test_simulate_incarceration(self):
        nsteps = 1
        inc_states = []

        model = cadre_model.Model(n=10, verbose=False) 

        for p in model.my_persons:
            self.assertTrue(p.current_incarceration_status == 0, "all persons are not initially un-incarcerated")   
            p.simulate_incarceration(time=nsteps, PROBABILITY_DAILY_INCARCERATION=1)
            inc_states.append(p.current_incarceration_status)
            self.assertTrue(p.current_incarceration_status == 1, "not incarcerated, even though probability of incarceration is 1")     

if __name__ == '__main__':  
    unittest.main()
