import unittest
import numpy as np
import pandas as pd
import sys
import os 

from pycadre import cadre_model
from pycadre.load_params import params_list

class TestPerson(unittest.TestCase):

    def test_age_assignment(self):
        ages = []
        MIN_AGE = params_list['MIN_AGE']
        MAX_AGE = params_list['MAX_AGE']
        mean_age_target = (MIN_AGE+MAX_AGE)/2

        model = cadre_model.Model(n=1000, verbose=False)    
        model.run(MAXTIME=0)
                   
        for person in model.my_persons:
                ages.append(person.age)

        for age in ages: 
            self.assertTrue(age >= MIN_AGE)
            self.assertTrue(age <= MAX_AGE)
            self.assertAlmostEqual(np.mean(ages), mean_age_target, delta=1)

    def test_race_assignment(self):

        RD = params_list['RACE_DISTRIBUTION']
        RACE_DISTRIBUTION = [
            RD['White'],
            RD['Black'],
            RD['Hispanic'], 
            RD['Asian']
        ]
        races = []
        model = cadre_model.Model(n=1000, verbose=False)
        model.run(MAXTIME=0)
                   
        for person in model.my_persons:
                races.append(person.race)

        #print("Races: "  + str(races))
        race_dist = pd.value_counts(np.array(races))/len(races)
        #print("Races: " + str(race_dist))

        self.assertAlmostEqual(race_dist.White, RACE_DISTRIBUTION[0], delta=2)
        self.assertAlmostEqual(race_dist.Black, RACE_DISTRIBUTION[1], delta=2)
        self.assertAlmostEqual(race_dist.Hispanic, RACE_DISTRIBUTION[2], delta=2)
        self.assertAlmostEqual(race_dist.Other, RACE_DISTRIBUTION[3], delta=2)

    ## test alcohol use assignment

    ## test alcohol status transition

    def test_aging(self):
        ages_init = []
        ages_final = []
        TICK_TO_YEAR_RATIO = params_list['TICK_TO_YEAR_RATIO'] #xx ticks make a year
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
            p.simulate_incarceration(time=nsteps, probability_daily_incarceration=1, sentence_duration=1)
            inc_states.append(p.current_incarceration_status)
            self.assertTrue(p.current_incarceration_status == 1, "not incarcerated, even though probability of incarceration is 1")

    def test_alco_status(self):
        nsteps = 250
        all_alco = []

        model = cadre_model.Model(n=10000, verbose = False)
        model.run(MAXTIME=nsteps)

        for person in model.my_persons:
            all_alco.append(person.alc_use_status)

        alco_dist = pd.value_counts(np.array(all_alco))/len(all_alco)
        print(alco_dist)
        self.assertAlmostEqual(alco_dist[0], 0.083, delta=4)


if __name__ == '__main__':  
    unittest.main()
