from cmath import nan
from tkinter.messagebox import NO
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
        self.dur_cat = -1
        self.sentence_duration = -1

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

    def simulate_incarceration(self, time, probability_daily_incarceration):
        
        prob = random.uniform(0, 1)
        #PROBABILITY_DAILY_INCARCERATION = params_list['PROBABILITY_DAILY_INCARCERATION']

        if self.current_incarceration_status == 0:
            if prob < probability_daily_incarceration:
                self.current_incarceration_status = 1 
                self.last_incarceration_time = time  
                self.incarceration_duration = 0   

        elif self.current_incarceration_status == 1:
            self.incarceration_duration += 1

   
    def simulate_release(self, time):
                      
        if self.sentence_duration > 0:
            if self.incarceration_duration >= self.sentence_duration:
                    self.current_incarceration_status = 0
                    self.last_release_time = time
                    self.incarceration_duration = -1

    def assign_sentence_duration_cat(self):
            ALL_SDEMP = params_list['SENTENCE_DURATION_EMP']
            FEMALE_SDEMP =  ALL_SDEMP['females']
            MALE_SDEMP = ALL_SDEMP['males']
            FEMALE_SDEMP_DURATIONS = list(FEMALE_SDEMP.keys())
            FEMALE_SDEMP_PROPS = list(FEMALE_SDEMP.values())
            MALE_SDEMP_DURATIONS = list(MALE_SDEMP.keys())
            MALE_SDEMP_PROPS = list(MALE_SDEMP.values())

            if self.female == 1:
                if self.current_incarceration_status == 1: 
                    self.dur_cat = random.choice(FEMALE_SDEMP_DURATIONS, p=FEMALE_SDEMP_PROPS)

                print("First dur_cat" + " for agent " + str(self.name) + " is " + str(self.dur_cat)) 


            elif self.female == 0:
                if self.current_incarceration_status == 1: 
                    self.dur_cat = random.choice(MALE_SDEMP_DURATIONS, p=MALE_SDEMP_PROPS)   
                print("First dur_cat" + " for agent " + str(self.name) + " is " + str(self.dur_cat)) 
                
               

    def assign_sentence_duration(self):
            #print("Second dur_cat" + " for agent " + str(self.name) + " is " + str(self.dur_cat), "\n") 
            
            if self.dur_cat == 0:
                self.sentence_duration = random.randint(7, 29) #IN DAILY UNITS, CHANGE IF UNITS CHANGE
            elif self.dur_cat == 1:
                self.sentence_duration = random.randint(29, 183)
            elif self.dur_cat == 2:
                self.sentence_duration = random.randint(183, 366)
            elif self.dur_cat == 3:
                self.sentence_duration = random.randint(366, 1096)
            elif self.dur_cat == 4:
                self.sentence_duration = random.randint(1096, 2191)

            print("Second dur_cat" + " for agent " + str(self.name) + " is " + str(self.dur_cat))
            print("Sentence duration" + " for agent " + str(self.name) + " is " + str(self.sentence_duration), "\n")

        


