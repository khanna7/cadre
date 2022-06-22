from numpy import random

class Person():
    def __init__(self, 
    name=None, 
    age=None, 
    race=None, 
    female=None,
    smoker=None, 
    alc_use_status=None,
    current_incarceration_status = None,
    last_incarceration_time = None):

        self.name = name    
        self.age = age
        self.race = race
        self.female = female
        self.smoker = smoker
        self.alc_use_status = alc_use_status
        self.current_incarceration_status = current_incarceration_status
        self.last_incarceration_time = last_incarceration_time

    def aging(self):
        TICK_TO_YEAR_RATIO = 365 #xx ticks make a year
        self.age += 1/TICK_TO_YEAR_RATIO


    def transition_alc_use(self):

        # level up
        TRANS_PROB_0_1 = 0/100 
        TRANS_PROB_1_2 = 1/100
        TRANS_PROB_2_3 = 1/100
        # LEVEL DOWN
        TRANS_PROB_1_0 = 0.5/100
        TRANS_PROB_2_1 = 0.5/100
        TRANS_PROB_3_2 = 0.5/100

        prob = random.uniform(0, 1)
        if self.alc_use_status == 0:
            if (prob <= TRANS_PROB_0_1):
                self.alc_use_status += 1


        elif self.alc_use_status == 1:
            if (prob <= TRANS_PROB_1_2):
                self.alc_use_status += 1

            elif (prob > 1-TRANS_PROB_1_0):
                self.alc_use_status -= 1

        
        elif self.alc_use_status == 2:
            if (prob <= TRANS_PROB_2_3):
                self.alc_use_status += 1

            elif (prob > 1-TRANS_PROB_2_1):
                self.alc_use_status -= 1

        elif self.alc_use_status == 3:
            if (prob > 1-TRANS_PROB_3_2):
                self.alc_use_status -= 1



    def simulate_incarceration(self, time):

        PROBABILITY_DAILY_INCARCERATION = 1/100
        prob = random.uniform(0, 1)

        if self.current_incarceration_status == 0:
            if prob < PROBABILITY_DAILY_INCARCERATION:
                self.current_incarceration_status = 1 
                self.last_incarceration_time = time   

