from numpy import random
from pycadre.load_params import params_list

# read parameters

class Person():
    def __init__(self, name=None):

        MIN_AGE = params_list['MIN_AGE']
        MAX_AGE = params_list['MAX_AGE']+1
        RACE_CATS = params_list['RACE_CATS']
        FEMALE_PROP = params_list['FEMALE_PROP']
        RD = params_list['RACE_DISTRIBUTION']
        RACE_DISTRIBUTION = [
            RD['White'],
            RD['Black'],
            RD['Hispanic'], 
            RD['Asian']]
        AU_PROPS = params_list['ALC_USE_PROPS']
        ALC_USE_PROPS = [AU_PROPS['A'], AU_PROPS['O'], AU_PROPS['R'], AU_PROPS['D']]
        SMOKING_PREV = params_list['SMOKING_PREV']

        self.name = name    
        self.age = random.randint(MIN_AGE, MAX_AGE)
        self.race = random.choice(RACE_CATS, p=RACE_DISTRIBUTION)
        self.female = random.binomial(1, FEMALE_PROP)
        self.smoker = random.binomial(1, SMOKING_PREV)
        self.alc_use_status = random.choice(range(0, len(ALC_USE_PROPS)), p=ALC_USE_PROPS)
        self.current_incarceration_status = 0
        self.last_incarceration_time = -1
        self.incarceration_duration = -1
        self.last_release_time = -1

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


