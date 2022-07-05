from statistics import mean as mean
import unittest
import numpy as np
import pandas as pd
import sys
import os 


from pycadre import cadre_model
import pycadre.load_params

 
class TestPerson(unittest.TestCase):
    params_list = pycadre.load_params.load_params()
    Test_N = 100


    def test_age_assignment(self):
        
        ages = []
        MIN_AGE = TestPerson.params_list['MIN_AGE']
        MAX_AGE = TestPerson.params_list['MAX_AGE']

        mean_age_target = (MIN_AGE+MAX_AGE)/2

        #print("Min age:", TestPerson.MIN_AGE)

        model = cadre_model.Model(n=TestPerson.Test_N, verbose=False)    
        model.run(MAXTIME=0)
                   
        for person in model.my_persons:
                ages.append(person.age)

        for age in ages: 
            self.assertTrue(age >= MIN_AGE)
            self.assertTrue(age <= MAX_AGE)

            if TestPerson.Test_N >= 1000:
                # only try this if n is sufficiently large, or test fails
                self.assertAlmostEqual(np.mean(ages), mean_age_target, delta=1)

    def test_race_assignment(self):

        RD = TestPerson.params_list['RACE_DISTRIBUTION']
        RACE_DISTRIBUTION = [
            RD['White'],
            RD['Black'],
            RD['Hispanic'], 
            RD['Asian']
        ]
        races = []
        model = cadre_model.Model(n=TestPerson.Test_N, verbose=False)
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
        TICK_TO_YEAR_RATIO = TestPerson.params_list['TICK_TO_YEAR_RATIO'] #xx ticks make a year
        nsteps = 100

        model = cadre_model.Model(n=TestPerson.Test_N, verbose=False)
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

        model = cadre_model.Model(n=TestPerson.Test_N, verbose=False) 

        #test case where 0 < incarceration probability < 1
        probability_daily_incarceration=0.5 
        for p in model.my_persons:     
            self.assertTrue(p.current_incarceration_status == 0, "all persons are not initially un-incarcerated")   
            p.simulate_incarceration(time=nsteps, probability_daily_incarceration=probability_daily_incarceration)
            inc_states.append(p.current_incarceration_status)
        
        if TestPerson.Test_N >= 1000:
            print("Mean incarcerated: " + str(mean(inc_states)))
            self.assertAlmostEqual(mean(inc_states), probability_daily_incarceration, delta=0.1)

        #test case where incarceration probability = 1   
        probability_daily_incarceration=1 
        for p in model.my_persons:
            p.simulate_incarceration(time=nsteps, probability_daily_incarceration=1)
            inc_states.append(p.current_incarceration_status)
            self.assertTrue(p.current_incarceration_status == 1, "not incarcerated, even though probability of incarceration is 1")

        #print("Incarceration states: " + str(inc_states), )  
        return model

    def test_simulate_release(self):
            model = TestPerson.test_simulate_incarceration(self)
            nsteps = 1
            inc_states = []
            
            for p in model.my_persons:
                #print(p.current_incarceration_status)
                inc_states.append(p.current_incarceration_status)
            print("Initial Incarceration states: " + str(inc_states))

            inc_states = [] #make incarceration status list empty 
            for p in model.my_persons:
                p.sentence_duration = 0 #assign 
                p.simulate_release(time=nsteps)
                inc_states.append(p.current_incarceration_status)
                self.assertTrue(p.current_incarceration_status == 0, "all not unincarcerated, even though max sentence duration is 0")
            
            print("Final Incarceration states: " + str(inc_states)) 

if __name__ == '__main__':  
    unittest.main()
