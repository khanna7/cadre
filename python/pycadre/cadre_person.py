from numpy import random
from pycadre.load_params import params_list

#PROBABILITY_DAILY_INCARCERATION = params_list['PROBABILITY_DAILY_INCARCERATION']
#SENTENCE_DURATION = params_list['SENTENCE_DURATION']

class Person():
    def __init__(self, 
    name=None, 
    age=None, 
    race=None, 
    female=None,
    smoker=None, 
    alc_use_status=None,
    current_incarceration_status = None,
    last_incarceration_time = None,
    incarceration_duration = None,
    last_release_time = None):

        self.name = name    
        self.age = age
        self.race = race
        self.female = female
        self.smoker = smoker
        self.alc_use_status = alc_use_status
        self.current_incarceration_status = current_incarceration_status
        self.last_incarceration_time = last_incarceration_time
        self.incarceration_duration = incarceration_duration
        self.last_release_time = last_release_time

    def aging(self):
        TICK_TO_YEAR_RATIO = params_list['TICK_TO_YEAR_RATIO']
        self.age += 1/TICK_TO_YEAR_RATIO

    def transition_alc_use(self):

        # level up
        ALC_USE_STATES = params_list['ALC_USE_STATES']
        TRANS_PROB_0_1 = ALC_USE_STATES['TRANS_PROB_0_1']
        TRANS_PROB_1_2 = ALC_USE_STATES['TRANS_PROB_1_2']
        TRANS_PROB_2_3 = ALC_USE_STATES['TRANS_PROB_2_3']
        # LEVEL DOWN
        TRANS_PROB_1_0 = ALC_USE_STATES['TRANS_PROB_1_0']
        TRANS_PROB_2_1 = ALC_USE_STATES['TRANS_PROB_2_1']
        TRANS_PROB_3_2 = ALC_USE_STATES['TRANS_PROB_3_2']

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



    def simulate_incarceration(self, time, probability_daily_incarceration, sentence_duration):
        
        prob = random.uniform(0, 1)
        #PROBABILITY_DAILY_INCARCERATION = params_list['PROBABILITY_DAILY_INCARCERATION']

        if self.current_incarceration_status == 0:
            if prob < probability_daily_incarceration:
                self.current_incarceration_status = 1 
                self.last_incarceration_time = time  
                self.incarceration_duration = 0   
                
        elif self.current_incarceration_status == 1:
            self.incarceration_duration += 1
        
        if (self.incarceration_duration > sentence_duration):
                self.current_incarceration_status = 0
                self.last_release_time = time
                self.incarceration_duration = 0


