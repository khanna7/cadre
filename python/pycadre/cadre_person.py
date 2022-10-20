from functools import partial
from unicodedata import name
from repast4py import core, schedule
from numpy import random
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

    def __init__(self, name: int, type: int, rank: int, **kwargs):

        super().__init__(id=name, type=Person.TYPE, rank=rank)

        MIN_AGE = load_params.params_list["MIN_AGE"]
        MAX_AGE = load_params.params_list["MAX_AGE"] + 1
        RACE_CATS = load_params.params_list["RACE_CATS"]
        FEMALE_PROP = load_params.params_list["FEMALE_PROP"]
        RD = load_params.params_list["RACE_DISTRIBUTION"]
        RACE_DISTRIBUTION = [RD["White"], RD["Black"], RD["Hispanic"], RD["Asian"]]
        AU_PROPS = load_params.params_list["ALC_USE_PROPS"]
        ALC_USE_PROPS = [AU_PROPS["A"], AU_PROPS["O"], AU_PROPS["R"], AU_PROPS["D"]]

        self.name = name
        self.age = random.uniform(MIN_AGE, MAX_AGE-1)
        self.race = random.choice(RACE_CATS, p=RACE_DISTRIBUTION)
        self.female = random.binomial(1, FEMALE_PROP)
        self.alc_use_status = random.choice(
            range(0, len(ALC_USE_PROPS)), p=ALC_USE_PROPS
        )
        self.current_incarceration_status = 0
        self.last_incarceration_tick = -1
        self.incarceration_duration = -1
        self.last_release_tick = -1
        self.dur_cat = -1
        self.sentence_duration = -1
        self.when_to_release = -1
        self.n_incarcerations = 0
        self.entry_at_tick = -1
        self.exit_at_tick = -1
        self.assign_smoker_status()  # note self.smoker = self.assign_smoker_status() was giving all smoking statuses as None. but this works

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

    def transition_alc_use(self):

        # level up
        ALC_USE_STATES = load_params.params_list["ALC_USE_STATES"]
        TRANS_PROB_0_1 = ALC_USE_STATES["TRANS_PROB_0_1"]
        TRANS_PROB_1_2 = ALC_USE_STATES["TRANS_PROB_1_2"]
        TRANS_PROB_2_3 = ALC_USE_STATES["TRANS_PROB_2_3"]
        # LEVEL DOWN
        TRANS_PROB_1_0 = ALC_USE_STATES["TRANS_PROB_1_0"]
        TRANS_PROB_2_1 = ALC_USE_STATES["TRANS_PROB_2_1"]
        TRANS_PROB_3_2 = ALC_USE_STATES["TRANS_PROB_3_2"]

        prob = random.uniform(0, 1)
        if self.alc_use_status == 0:
            if prob <= TRANS_PROB_0_1:
                self.alc_use_status += 1

        elif self.alc_use_status == 1:
            if prob <= TRANS_PROB_1_2:
                self.alc_use_status += 1

            elif prob > 1 - TRANS_PROB_1_0:
                self.alc_use_status -= 1

        elif self.alc_use_status == 2:
            if prob <= TRANS_PROB_2_3:
                self.alc_use_status += 1

            elif prob > 1 - TRANS_PROB_2_1:
                self.alc_use_status -= 1

        elif self.alc_use_status == 3:
            if prob > 1 - TRANS_PROB_3_2:
                self.alc_use_status -= 1

    def transition_smoking_status(self):
        SMOKING_TRANSITION_PROBS = load_params.params_list["SMOKING_TRANSITION_PROBS"]
        WHITE_MALES_CESSATION = SMOKING_TRANSITION_PROBS["WHITE_MALES"]["CESSATION"]
        WHITE_MALES_RELAPSE = SMOKING_TRANSITION_PROBS["WHITE_MALES"]["RELAPSE"]
        WHITE_FEMALES_CESSATION = SMOKING_TRANSITION_PROBS["WHITE_FEMALES"]["CESSATION"]
        WHITE_FEMALES_RELAPSE = SMOKING_TRANSITION_PROBS["WHITE_FEMALES"]["RELAPSE"]
        BLACK_MALES_CESSATION = SMOKING_TRANSITION_PROBS["BLACK_MALES"]["CESSATION"]
        BLACK_MALES_RELAPSE = SMOKING_TRANSITION_PROBS["BLACK_MALES"]["RELAPSE"]
        BLACK_FEMALES_CESSATION = SMOKING_TRANSITION_PROBS["BLACK_FEMALES"]["CESSATION"]
        BLACK_FEMALES_RELAPSE = SMOKING_TRANSITION_PROBS["BLACK_FEMALES"]["RELAPSE"]
        HISPANIC_MALES_CESSATION = SMOKING_TRANSITION_PROBS["HISPANIC_MALES"][
            "CESSATION"
        ]
        HISPANIC_MALES_RELAPSE = SMOKING_TRANSITION_PROBS["HISPANIC_MALES"]["RELAPSE"]
        HISPANIC_FEMALES_CESSATION = SMOKING_TRANSITION_PROBS["HISPANIC_FEMALES"][
            "CESSATION"
        ]
        HISPANIC_FEMALES_RELAPSE = SMOKING_TRANSITION_PROBS["HISPANIC_FEMALES"][
            "RELAPSE"
        ]
        ASIAN_MALES_CESSATION = SMOKING_TRANSITION_PROBS["ASIAN_MALES"]["CESSATION"]
        ASIAN_MALES_RELAPSE = SMOKING_TRANSITION_PROBS["ASIAN_MALES"]["RELAPSE"]
        ASIAN_FEMALES_CESSATION = SMOKING_TRANSITION_PROBS["ASIAN_FEMALES"]["CESSATION"]
        ASIAN_FEMALES_RELAPSE = SMOKING_TRANSITION_PROBS["ASIAN_FEMALES"]["RELAPSE"]

        prob = random.uniform(0, 1)

        # cessation for current smokers
        if self.smoker == "Current":
            if self.race == "White":
                if self.female == 1:
                    if prob <= WHITE_FEMALES_CESSATION:
                        self.smoker = "Former"

                elif self.female == 0:
                    if prob <= WHITE_MALES_CESSATION:
                        self.smoker = "Former"

            elif self.race == "Black":
                if self.female == 1:
                    if prob <= BLACK_FEMALES_CESSATION:
                        self.smoker = "Former"

                elif self.female == 0:
                    if prob <= BLACK_MALES_CESSATION:
                        self.smoker = "Former"

            elif self.race == "Hispanic":
                if self.female == 1:
                    if prob <= HISPANIC_FEMALES_CESSATION:
                        self.smoker = "Former"

                elif self.female == 0:
                    if prob <= HISPANIC_MALES_CESSATION:
                        self.smoker = "Former"

            elif self.race == "Asian":
                if self.female == 1:
                    if prob <= ASIAN_FEMALES_CESSATION:
                        self.smoker = "Former"

                elif self.female == 0:
                    if prob <= ASIAN_MALES_CESSATION:
                        self.smoker = "Former"

        # relapse for former smokers
        if self.smoker == "Former":
            if self.race == "White":
                if self.female == 1:
                    if prob <= WHITE_FEMALES_RELAPSE:
                        self.smoker = "Current"

                elif self.female == 0:
                    if prob <= WHITE_MALES_RELAPSE:
                        self.smoker = "Current"

            elif self.race == "Black":
                if self.female == 1:
                    if prob <= BLACK_FEMALES_RELAPSE:
                        self.smoker = "Current"

                elif self.female == 0:
                    if prob <= BLACK_MALES_RELAPSE:
                        self.smoker = "Current"

            elif self.race == "Hispanic":
                if self.female == 1:
                    if prob <= HISPANIC_FEMALES_RELAPSE:
                        self.smoker = "Current"

                elif self.female == 0:
                    if prob <= HISPANIC_MALES_RELAPSE:
                        self.smoker = "Current"

            elif self.race == "Asian":
                if self.female == 1:
                    if prob <= ASIAN_FEMALES_RELAPSE:
                        self.smoker = "Current"

                elif self.female == 0:
                    if prob <= ASIAN_MALES_RELAPSE:
                        self.smoker = "Former"

    def simulate_incarceration(self, tick, probability_daily_incarceration):

        prob = random.uniform(0, 1)

        if self.current_incarceration_status == 0:
            if self.n_incarcerations == 0:
                if prob < probability_daily_incarceration:
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
                self.dur_cat = random.choice(
                    FEMALE_SDEMP_DURATIONS, p=FEMALE_SDEMP_PROPS
                )

        elif self.female == 0:
            if self.current_incarceration_status == 1:
                self.dur_cat = random.choice(MALE_SDEMP_DURATIONS, p=MALE_SDEMP_PROPS)

    def assign_sentence_duration(self):

        if self.dur_cat == 0:
            self.sentence_duration = random.randint(
                7, 29
            )  # IN DAILY UNITS, CHANGE IF UNITS CHANGE
        elif self.dur_cat == 1:
            self.sentence_duration = random.randint(29, 183)
        elif self.dur_cat == 2:
            self.sentence_duration = random.randint(183, 366)
        elif self.dur_cat == 3:
            self.sentence_duration = random.randint(366, 1096)
        elif self.dur_cat == 4:
            self.sentence_duration = random.randint(1096, 2191)

    def simulate_release(self, tick):

        self.current_incarceration_status = 0
        self.last_release_tick = tick
        self.incarceration_duration = -1

    def simulate_recidivism(
        self,
        tick,
        probability_daily_recidivism_females,
        probability_daily_recidivism_males,
        probability_daily_incarceration,
    ):

        RECIDIVISM_UPDATED_PROB_LIMIT = load_params.params_list[
            "RECIDIVISM_UPDATED_PROB_LIMIT"
        ]
        prob = random.uniform(0, 1)
        time_since_release = tick - self.last_release_tick

        if self.current_incarceration_status == 0:

            if self.n_incarcerations > 0:
                if time_since_release <= RECIDIVISM_UPDATED_PROB_LIMIT:
                    # recidivism probability only applies for a certain num of days after release
                    if self.female == 1:
                        if prob < probability_daily_recidivism_females:
                            self.update_attributes_at_incarceration_tick(tick=tick)

                    elif self.female == 0:
                        if prob < probability_daily_recidivism_males:
                            self.update_attributes_at_incarceration_tick(tick=tick)

                elif time_since_release > RECIDIVISM_UPDATED_PROB_LIMIT:
                    # after recidivism limit period, inc prob is the same for both genders
                    if prob < probability_daily_incarceration:
                        self.update_attributes_at_incarceration_tick(tick=tick)

    def assign_smoker_status(self):

        SMOKING_CATS = load_params.params_list["SMOKING_CATS"]
        SMOKING_PREV = load_params.params_list["SMOKING_PREV"]

        SMOKING_PREV_WHITE_MALE = (
            SMOKING_PREV["WHITE_MALE_CURRENT"],
            SMOKING_PREV["WHITE_MALE_FORMER"],
            SMOKING_PREV["WHITE_MALE_NEVER"],
        )
        SMOKING_PREV_WHITE_FEMALE = (
            SMOKING_PREV["WHITE_FEMALE_CURRENT"],
            SMOKING_PREV["WHITE_FEMALE_FORMER"],
            SMOKING_PREV["WHITE_FEMALE_NEVER"],
        )
        SMOKING_PREV_BLACK_MALE = (
            SMOKING_PREV["BLACK_MALE_CURRENT"],
            SMOKING_PREV["BLACK_MALE_FORMER"],
            SMOKING_PREV["BLACK_MALE_NEVER"],
        )
        SMOKING_PREV_BLACK_FEMALE = (
            SMOKING_PREV["BLACK_FEMALE_CURRENT"],
            SMOKING_PREV["BLACK_FEMALE_FORMER"],
            SMOKING_PREV["BLACK_FEMALE_NEVER"],
        )
        SMOKING_PREV_HISPANIC_MALE = (
            SMOKING_PREV["HISPANIC_MALE_CURRENT"],
            SMOKING_PREV["HISPANIC_MALE_FORMER"],
            SMOKING_PREV["HISPANIC_MALE_NEVER"],
        )
        SMOKING_PREV_HISPANIC_FEMALE = (
            SMOKING_PREV["HISPANIC_FEMALE_CURRENT"],
            SMOKING_PREV["HISPANIC_FEMALE_FORMER"],
            SMOKING_PREV["HISPANIC_FEMALE_NEVER"],
        )
        SMOKING_PREV_ASIAN_MALE = (
            SMOKING_PREV["ASIAN_MALE_CURRENT"],
            SMOKING_PREV["ASIAN_MALE_FORMER"],
            SMOKING_PREV["ASIAN_MALE_NEVER"],
        )
        SMOKING_PREV_ASIAN_FEMALE = (
            SMOKING_PREV["ASIAN_FEMALE_CURRENT"],
            SMOKING_PREV["ASIAN_FEMALE_FORMER"],
            SMOKING_PREV["ASIAN_FEMALE_NEVER"],
        )

        if self.race == "White":
            if self.female == 0:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_WHITE_MALE)
            elif self.female == 1:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_WHITE_FEMALE)

        elif self.race == "Black":
            if self.female == 0:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_BLACK_MALE)
            elif self.female == 1:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_BLACK_FEMALE)

        elif self.race == "Hispanic":
            if self.female == 0:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_HISPANIC_MALE)
            elif self.female == 1:
                self.smoker = random.choice(
                    SMOKING_CATS, p=SMOKING_PREV_HISPANIC_FEMALE
                )

        elif self.race == "Asian":
            if self.female == 0:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_ASIAN_MALE)
            elif self.female == 1:
                self.smoker = random.choice(SMOKING_CATS, p=SMOKING_PREV_ASIAN_FEMALE)


def create_person(nid, agent_type, rank, **kwargs):
    return Person(nid, agent_type, rank)


def restore_person(agent_data):
    uid = agent_data[0]
    return Person(uid[0], uid[1], uid[2], agent_data[1])
