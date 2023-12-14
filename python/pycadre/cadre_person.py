from functools import partial
from unicodedata import name
from repast4py import core, schedule, random
import pycadre.load_params as load_params
import csv

# read parameters


class Person(core.Agent):
    """The Person Agent

    Args:
        name: a integer that uniquely identifies this Person on its
              starting rank
        rank: the starting MPI rank of this Person.
    """

    TYPE = 0

    def __init__(
        self,
        name: int,
        type: int,
        rank: int,
        alc_use_status,
        age: int,
        race,
        female,
        tick,
        graph
    ):
        super().__init__(id=name, type=Person.TYPE, rank=rank)

        self.name = name
        self.age = age
        self.race = race
        self.female = female
        self.graph = graph
        self.alc_use_status = alc_use_status
        self.current_incarceration_status = 0
        self.last_incarceration_tick = -1
        self.incarceration_duration = -1
        self.last_release_tick = -1
        self.dur_cat = -1
        self.sentence_duration = -1
        self.when_to_release = -1
        self.n_incarcerations = 0
        self.n_releases = 0
        self.entry_at_tick = tick if tick is not None else -1
        self.exit_at_tick = -1
        self.assign_smoker_status()  # note self.smoker = self.assign_smoker_status() was giving all smoking statuses as None. but this works
        self.n_smkg_stat_trans = 0
        self.n_alc_use_stat_trans = 0
        #self.previous_smoking_status = None #to model transition in smoking status

    def __str__(self):
        return (
            super().__str__()
            + f" (age = {self.age}, race = {self.race}, female = {self.female} entry_at_tick = {self.entry_at_tick})"
        )

    def save(self):
        """Saves the state of this agent as tuple.

        A non-ghost agent will save its state using this
        method, and any ghost agents of this agent will
        be updated with that data (self.current_incarceration_status).

        Returns:
            The agent's state
        """
        return (self.uid, self.current_incarceration_status)

    def aging(self):
        TICK_TO_YEAR_RATIO = load_params.params_list["TICK_TO_YEAR_RATIO"]
        self.age += 1 / TICK_TO_YEAR_RATIO

    def exit_of_age(self, tick):
        MAX_AGE = load_params.params_list["MAX_AGE"]
        if self.age > MAX_AGE:
            self.exit_at_tick = tick
            return self

    def get_regular_to_heavy_alc_use_transition_network_influence(self):
        per_neighbor_factor = load_params.params_list["ALCOHOL_NETWORK_EFFECTS"]["ONSET"]["FIRST_DEGREE"]
        max_n_neighbors = load_params.params_list["MAX_N_NEIGHBORS_EFFECT"]["ALCOHOL"]
        increase = 1
        if self.graph is not None:
            nheavy = 0
            for n in self.graph.neighbors(self):
                if n.alc_use_status == 3:
                    nheavy += 1
            nincreases = min(nheavy, max_n_neighbors)
            increase *= pow(per_neighbor_factor, nincreases)
        return increase
    
    def transition_alc_use(self):

        # level up
        ALC_USE_STATES = load_params.params_list["ALC_USE_STATES"]

        if self.n_incarcerations > 0:
            # post-release proportions of alcohol are skewed towards more abuse,
            # so the transition rates need to change to reflect that
            ALC_USE_STATES = load_params.params_list["POST_RELEASE_ALC_USE_TRANSITION_RATES"]

        TRANS_PROB_1_2 = ALC_USE_STATES["TRANS_PROB_1_2"]
        TRANS_PROB_2_3 = ALC_USE_STATES["TRANS_PROB_2_3"]
        # LEVEL DOWN
        TRANS_PROB_2_1 = ALC_USE_STATES["TRANS_PROB_2_1"]
        TRANS_PROB_3_2 = ALC_USE_STATES["TRANS_PROB_3_2"]

        prob = random.default_rng.uniform(0, 1)
        #print("Generated prob in transition_alc_use:", prob)

        if self.current_incarceration_status == 0:
            if self.alc_use_status == 0:
                pass

            elif self.alc_use_status == 1:
                if prob <= TRANS_PROB_1_2:
                    self.alc_use_status += 1
                    self.n_alc_use_stat_trans += 1

            elif self.alc_use_status == 2:
                increase = self.get_regular_to_heavy_alc_use_transition_network_influence()
                if prob <= increase * TRANS_PROB_2_3:
                    self.alc_use_status += 1
                    self.n_alc_use_stat_trans += 1

                elif prob > 1 - TRANS_PROB_2_1:
                    self.alc_use_status -= 1
                    self.n_alc_use_stat_trans += 1

            elif self.alc_use_status == 3:
                if prob > 1 - TRANS_PROB_3_2:
                    self.alc_use_status -= 1
                    self.n_alc_use_stat_trans += 1
                    
        else: 
            pass

    def get_smoking_network_influence_factor(self):
        increase = 1
        if self.graph is not None:
            for n in self.graph.neighbors(self):
                if n.smoker == "Current":
                    increase = 1.61 
                    break
        return increase

    def get_former_to_current_smoking_transition_network_influence(self):
        per_neighbor_factor = load_params.params_list["SMOKING_NETWORK_EFFECTS"]["ONSET"]["FIRST_DEGREE"]
        max_n_neighbors = load_params.params_list["MAX_N_NEIGHBORS_EFFECT"]["ALCOHOL"]
        increase = 1
        if self.graph is not None:
            nsmokers = 0
            for n in self.graph.neighbors(self):
                if n.smoker == "Current":
                    nsmokers += 1
            nincreases = min(nsmokers, max_n_neighbors)
            increase *= pow(per_neighbor_factor, nincreases)
        return increase
    
    def transition_smoking_status(self, tick):
        SMOKING_TRANSITION_PROBS = load_params.params_list["SMOKING_TRANSITION_PROBS"]
     
        prob = random.default_rng.uniform(0, 1)

        def probs_key():
            return self.race.upper() + "_" + ("FEMALES" if self.female else "MALES")

        if self.current_incarceration_status == 0:
            # cessation for current smokers
            if self.smoker == "Current":
                key = probs_key()
                if prob <= SMOKING_TRANSITION_PROBS[key]["CESSATION"]:
                    self.smoker = "Former"
                    self.n_smkg_stat_trans += 1
                    self.last_smkg_trans_tick = tick
        
            # relapse for former smokers
            elif self.smoker == "Former":
                key = probs_key()
                increase = self.get_former_to_current_smoking_transition_network_influence()

                relapse_rate = SMOKING_TRANSITION_PROBS[key]["RELAPSE"]

                # if history of incarceration --> expose to elevated relapse rate
                if self.n_incarcerations > 0:
                    relapse_rate = load_params.params_list["POST_RELEASE_SMOKING_RELAPSE"]

                if prob <= increase * relapse_rate:
                    self.smoker = "Current"
                    self.n_smkg_stat_trans += 1
                    self.last_smkg_trans_tick = tick
    
        else:
            pass

    def simulate_incarceration(self, tick, probability_daily_incarceration, 
                               race_sex_pop_props, pct_smoking, pct_aud):
        prob = random.default_rng.uniform(0, 1)

        INC_RACE_SEX_PROP = load_params.params_list["INC_RACE_SEX_PROP"]        
        INC_CURRENT_SMOKING = load_params.params_list["INCARCERATION_SMOKING_ASSOC"]
        INC_CURRENT_AUD = load_params.params_list["INCARCERATION_AUD_ASSOC"]


        inc_current_smoking_rate = (INC_CURRENT_SMOKING["MIN"] + INC_CURRENT_SMOKING["MAX"])/2
        inc_current_aud_rate = (INC_CURRENT_AUD["MALES"] + INC_CURRENT_AUD["FEMALES"])/2
       
        time_since_release = tick - self.last_release_tick
        past_recidivism_limit = time_since_release > load_params.params_list["RECIDIVISM_UPDATED_PROB_LIMIT"]


        converted_race_sex_smoking_alc_inc_probs = {}
        
        for key in race_sex_pop_props:
            if race_sex_pop_props[key] == 0: 
                converted_race_sex_smoking_alc_inc_probs[key] = 0
            elif self.smoker == "Current" and self.alc_use_status == 3:
                converted_race_sex_smoking_alc_inc_probs[key] = (
                    probability_daily_incarceration * 
                    (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                    (inc_current_smoking_rate / pct_smoking) * 
                    (inc_current_aud_rate / pct_aud)
                ) 
            elif self.smoker == "Current" and self.alc_use_status != 3:
                converted_race_sex_smoking_alc_inc_probs[key] = (
                    probability_daily_incarceration * 
                    (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                    (inc_current_smoking_rate / pct_smoking) * 
                    (1 - inc_current_aud_rate / 1-pct_aud) 
                ) 
            elif self.smoker != "Current" and self.alc_use_status == 3: 
                converted_race_sex_smoking_alc_inc_probs[key] = (
                    probability_daily_incarceration * 
                    (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                    (1-inc_current_smoking_rate) / (1- pct_smoking) *
                    (inc_current_aud_rate / pct_aud)                   
                )
            elif self.smoker != "Current" and self.alc_use_status != 3: 
                converted_race_sex_smoking_alc_inc_probs[key] = (
                    probability_daily_incarceration * 
                    (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                    (1-inc_current_smoking_rate) / (1- pct_smoking) *
                    (1-inc_current_aud_rate / 1-pct_aud)                   
                )
 
                
        if self.current_incarceration_status == 0:
            if (self.n_incarcerations == 0) or (self.n_incarcerations > 0 and past_recidivism_limit):
                # include people pass the recidivism limit, so the enhanced probability does not apply to them 
                sex = "FEMALE" if self.female == 1 else "MALE"
                race_sex_key = f"{self.race.upper()}_{sex.upper()}"

                if race_sex_key in converted_race_sex_smoking_alc_inc_probs:
                    specific_prob = converted_race_sex_smoking_alc_inc_probs[race_sex_key]

                    if prob < specific_prob:
                        self.update_attributes_at_incarceration_tick(tick)
                            
    def update_attributes_at_incarceration_tick(self, tick):
        self.current_incarceration_status = 1
        self.last_incarceration_tick = tick
        self.incarceration_duration = 0
        self.n_incarcerations += 1
        self.assign_sentence_duration_cat()
        self.assign_sentence_duration()
        self.when_to_release = tick + self.sentence_duration
        runner = schedule.runner()
        runner.schedule_event(
            self.when_to_release,
            partial(self.simulate_release, tick=self.when_to_release),
        )

    def assign_sentence_duration_cat(self):
        ALL_SDEMP = load_params.params_list["SENTENCE_DURATION_EMP"]
        FEMALE_SDEMP = ALL_SDEMP["females"]
        MALE_SDEMP = ALL_SDEMP["males"]
        FEMALE_SDEMP_DURATIONS = list(FEMALE_SDEMP.keys())
        FEMALE_SDEMP_PROPS = list(FEMALE_SDEMP.values())
        MALE_SDEMP_DURATIONS = list(MALE_SDEMP.keys())
        MALE_SDEMP_PROPS = list(MALE_SDEMP.values())

        if self.female == 1:
            if self.current_incarceration_status == 1:
                self.dur_cat = random.default_rng.choice(
                    FEMALE_SDEMP_DURATIONS, p=FEMALE_SDEMP_PROPS
                )

        elif self.female == 0:
            if self.current_incarceration_status == 1:
                self.dur_cat = random.default_rng.choice(MALE_SDEMP_DURATIONS, p=MALE_SDEMP_PROPS)

    def assign_sentence_duration(self):

        if self.dur_cat == 0:
            self.sentence_duration = random.default_rng.integers(
                7, 29
            )  # IN DAILY UNITS, CHANGE IF UNITS CHANGE
        elif self.dur_cat == 1:
            self.sentence_duration = random.default_rng.integers(29, 183)
        elif self.dur_cat == 2:
            self.sentence_duration = random.default_rng.integers(183, 366)
        elif self.dur_cat == 3:
            self.sentence_duration = random.default_rng.integers(366, 1096)
        elif self.dur_cat == 4:
            self.sentence_duration = random.default_rng.integers(1096, 2191)

    def simulate_release(self, tick):
        # Check if the agent is still in the graph
        
        if self.graph is not None and self.graph.has_node(self):
            # reset incarceration status
            self.current_incarceration_status = 0
            self.last_release_tick = tick
            self.incarceration_duration = -1
            self.n_releases += 1
            #self.previous_smoking_status = self.smoker
            #self.assign_smoker_status() 
            #self.update_alc_use_post_release()

    def simulate_recidivism(
        self,
        tick,
        probability_daily_recidivism_females,
        probability_daily_recidivism_males,
        race_sex_pop_props,
        pct_smoking,
        pct_aud
    ):
    
        prob = random.default_rng.uniform(0, 1)
        
        RECIDIVISM_UPDATED_PROB_LIMIT = load_params.params_list["RECIDIVISM_UPDATED_PROB_LIMIT"]
        INC_RACE_SEX_PROP = load_params.params_list["INC_RACE_SEX_PROP"] #use same values as INC_RACE_SEX_PROP
        INC_CURRENT_SMOKING = load_params.params_list["INCARCERATION_SMOKING_ASSOC"]
        INC_CURRENT_AUD = load_params.params_list["INCARCERATION_AUD_ASSOC"]

        inc_current_smoking_rate = (
            (INC_CURRENT_SMOKING["MIN"] + 
            INC_CURRENT_SMOKING["MAX"])/2
            )
        inc_current_aud_rate = (INC_CURRENT_AUD["MALES"] + INC_CURRENT_AUD["FEMALES"])/2


        converted_race_sex_smoking_alc_recidivism_probs = {}
        base_prob = {}        
        
        time_since_release = tick - self.last_release_tick
        
        for key in race_sex_pop_props:
            
            if race_sex_pop_props[key] == 0: 
                base_prob[key] = 0
            
            else:
                base_prob[key] = probability_daily_recidivism_females if "FEMALE" in key else probability_daily_recidivism_males
            
                if self.smoker == "Current" and self.alc_use_status == 3:
                    converted_race_sex_smoking_alc_recidivism_probs[key] = (
                        base_prob[key] * 
                        (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                        (inc_current_smoking_rate / pct_smoking)*
                        (inc_current_aud_rate / pct_aud)
                    ) 
                elif self.smoker == "Current" and self.alc_use_status != 3:
                    converted_race_sex_smoking_alc_recidivism_probs[key] = (
                        base_prob[key] * 
                        (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                        (inc_current_smoking_rate / pct_smoking) * 
                        (1 - inc_current_aud_rate / 1-pct_aud) 
                ) 
                elif self.smoker != "Current" and self.alc_use_status == 3:
                    converted_race_sex_smoking_alc_recidivism_probs[key] = (
                        base_prob[key] * 
                        (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                        (1-inc_current_smoking_rate / 1-pct_smoking) * 
                        (inc_current_aud_rate / pct_aud) 
                ) 
                elif self.smoker != "Current" and self.alc_use_status != 3:
                    converted_race_sex_smoking_alc_recidivism_probs[key] = (
                        base_prob[key] * 
                        (INC_RACE_SEX_PROP[key] / race_sex_pop_props[key]) *
                        (1-inc_current_smoking_rate / 1-pct_smoking) * 
                        (1-inc_current_aud_rate / 1-pct_aud) 
                ) 
                    
        if self.current_incarceration_status == 0 and self.n_incarcerations > 0:
            if time_since_release <= RECIDIVISM_UPDATED_PROB_LIMIT:
                # Adjusting recidivism probability based on race and sex
                sex = "FEMALE" if self.female == 1 else "MALE"
                race_sex_key = f"{self.race.upper()}_{sex.upper()}"
                specific_prob = converted_race_sex_smoking_alc_recidivism_probs.get(race_sex_key, 0)
                                    
                if prob < specific_prob:
                    self.update_attributes_at_incarceration_tick(tick=tick)
                    print("Agent experiences recidivism")
    
    def assign_smoker_status(self):
        SMOKING_CATS = load_params.params_list["SMOKING_CATS"]
        SMOKING_PREV = load_params.params_list["SMOKING_PREV"]
        RACE_CATS = load_params.params_list["RACE_CATS"]

        #print("SMOKING_CATS", SMOKING_CATS)
        #print("SMOKING_PREV", SMOKING_PREV)

        SMOKING_PREV_BY_RACE_AND_GENDER = {
            "White": {
                0: (
                    SMOKING_PREV["WHITE_MALE_CURRENT"],
                    SMOKING_PREV["WHITE_MALE_FORMER"],
                    SMOKING_PREV["WHITE_MALE_NEVER"]
                ),
                1: (
                    SMOKING_PREV["WHITE_FEMALE_CURRENT"],
                    SMOKING_PREV["WHITE_FEMALE_FORMER"],
                        SMOKING_PREV["WHITE_FEMALE_NEVER"]
                )
            },
            "Black": {
                0: (
                    SMOKING_PREV["BLACK_MALE_CURRENT"],
                    SMOKING_PREV["BLACK_MALE_FORMER"],
                    SMOKING_PREV["BLACK_MALE_NEVER"]
                ),
                1: (
                    SMOKING_PREV["BLACK_FEMALE_CURRENT"],
                    SMOKING_PREV["BLACK_FEMALE_FORMER"],
                    SMOKING_PREV["BLACK_FEMALE_NEVER"]
                )
            },
            "Hispanic": {
                0: (
                    SMOKING_PREV["HISPANIC_MALE_CURRENT"],
                    SMOKING_PREV["HISPANIC_MALE_FORMER"],
                    SMOKING_PREV["HISPANIC_MALE_NEVER"]
                ),
                1: (
                    SMOKING_PREV["HISPANIC_FEMALE_CURRENT"],
                    SMOKING_PREV["HISPANIC_FEMALE_FORMER"],
                    SMOKING_PREV["HISPANIC_FEMALE_NEVER"]
                )
            },
            "Asian": {
                0: (
                    SMOKING_PREV["ASIAN_MALE_CURRENT"],
                    SMOKING_PREV["ASIAN_MALE_FORMER"],
                    SMOKING_PREV["ASIAN_MALE_NEVER"]
                ),
                1: (
                    SMOKING_PREV["ASIAN_FEMALE_CURRENT"],
                    SMOKING_PREV["ASIAN_FEMALE_FORMER"],
                    SMOKING_PREV["ASIAN_FEMALE_NEVER"]
                )
            }
        }

        # smoking_increase_factor = [load_params.parameters.params['RELEASE_SMOKING_INCREASE']['MALES'], load_params.parameters.params['RELEASE_SMOKING_INCREASE']['FEMALES']]
        # num_smoking_increases = load_params.parameters.params['NUM_RELEASE_SMOKING_INCREASES']
        # if self.n_releases > 0:
        #     n = max(self.n_releases, num_smoking_increases)
        #     for race in RACE_CATS:
        #         for sex in [0, 1]:
        #             current = pow(smoking_increase_factor[sex], n) * SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][0]
        #             SMOKING_PREV_BY_RACE_AND_GENDER[race][sex] = (current,
        #                                                     1 - (current + SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][2]),
        #                                                     SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][2]) 

        network_increase = self.get_smoking_network_influence_factor()
        if network_increase != 1:
            for race in RACE_CATS:
                for sex in [0, 1]:
                    current = network_increase * SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][0]
                    SMOKING_PREV_BY_RACE_AND_GENDER[race][sex] = (current,
                        1 - (current + SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][2]),
                        SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][2])

        smoking_prev = SMOKING_PREV_BY_RACE_AND_GENDER[self.race][self.female]
        if not hasattr(self, "smoker"):
            self.smoker = random.default_rng.choice(SMOKING_CATS, p=smoking_prev)
        elif self.smoker != "Never":
            prob_current = smoking_prev[0] / (smoking_prev[0] + smoking_prev[1])
            self.smoker =  "Current" if (prob_current > random.default_rng.random()) else "Former"

    # def update_alc_use_post_release(self):
    #     if self.alc_use_status == 0: return

    #     AU_PROPS = load_params.params_list["ALC_USE_PROPS"]
    #     ALC_USE_PROPS_INIT = [AU_PROPS["A"], AU_PROPS["O"], AU_PROPS["R"], AU_PROPS["D"]]
    #     ALC_USE_PROPS_POSTRELEASE = list(ALC_USE_PROPS_INIT)
    #     ALC_USE_PROPS_POSTRELEASE[3] = 0.17
    #     ALC_USE_PROPS_POSTRELEASE[2] = ALC_USE_PROPS_INIT[2] - abs(ALC_USE_PROPS_POSTRELEASE[3] - ALC_USE_PROPS_INIT[3])/2
    #     ALC_USE_PROPS_POSTRELEASE[1] = ALC_USE_PROPS_INIT[1] - abs(ALC_USE_PROPS_POSTRELEASE[3] - ALC_USE_PROPS_INIT[3])/2

    #     if (self.n_releases > 0):
    #         alc_use_status_postrelease = random.default_rng.choice(
    #             range(1, len(ALC_USE_PROPS_POSTRELEASE)), p=[x/sum(ALC_USE_PROPS_POSTRELEASE[1:]) for x in ALC_USE_PROPS_POSTRELEASE[1:]]
    #         )
    #         self.alc_use_status = alc_use_status_postrelease

def create_person(nid, agent_type, rank, **kwargs):
    return Person(nid, agent_type, rank)

def restore_person(agent_data):
    uid = agent_data[0]
    return Person(uid[0], uid[1], uid[2], agent_data[1])
