from functools import partial
from unicodedata import name
from repast4py import core, schedule, random

import copy
import pycadre.load_params as load_params
from pycadre import cadre_logging

# from pycadre.Model import Model

import csv

# read parameters

def normalize_transitions(states):
    tot = 0
    for state in states:
        tot += states[state]
    scaled_states = {}
    for state in states:
        scaled_states[state] = states[state] / tot
    return scaled_states

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
        graph,
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
        # self.previous_smoking_status = None #to model transition in smoking status

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
        per_neighbor_factor = load_params.params_list[
            "ALCOHOL_NETWORK_EFFECTS"
        ]["ONSET"]["FIRST_DEGREE"]
        max_n_neighbors = load_params.params_list["MAX_N_NEIGHBORS_EFFECT"][
            "ALCOHOL"
        ]
        increase = 1
        if self.graph is not None:
            nheavy = 0
            for n in self.graph.neighbors(self):
                if n.alc_use_status == 3:
                    nheavy += 1
            nincreases = min(nheavy, max_n_neighbors)
            increase *= pow(per_neighbor_factor, nincreases)
        return increase

    def get_new_alc_use_state(self, current_state):
        trans_probs = []
        # Load all transition probabilities
        ALC_USE_STATES = load_params.params_list["ALC_USE_STATES"]
        states = copy.deepcopy(ALC_USE_STATES[current_state])

        if current_state == 2:
            increase = (
                self.get_regular_to_heavy_alc_use_transition_network_influence()
            )
            states[3] = states[3] * increase
        scaled_states = normalize_transitions(states)
        # print("Scaled states: ", scaled_states)

        for state in scaled_states:
            # Append a tuple with the cumulative probability and the target state
            if trans_probs:
                trans_probs.append(
                    (trans_probs[-1][0] + scaled_states[state], state)
                )
            else:
                # First entry is the probability itself since there is no previous cumulative probability
                trans_probs.append((scaled_states[state], state))

        prob = random.default_rng.uniform(0, 1)
        # print("Trans probs", trans_probs)
        for cum_prob, state in trans_probs:
            # print("Trans probs: ", trans_probs)
            if prob <= cum_prob:
                new_state = state
                if new_state != current_state:
                    self.n_alc_use_stat_trans += 1
                break  # Exit loop after transition occurs
        return new_state

    def transition_alc_use(self):
        # Check if the agent is not incarcerated
        if self.current_incarceration_status == 0:
            # print("Person alc use status:", self.alc_use_status)

            self.alc_use_status = self.get_new_alc_use_state(
                self.alc_use_status
            )

        # print("Alcohol use state:", self.alc_use_status)

    def get_smoking_network_influence_factor(self):
        increase = 1
        if self.graph is not None:
            for n in self.graph.neighbors(self):
                if n.smoker == "Current":
                    increase = 1.61
                    break
        return increase

    def get_former_to_current_smoking_transition_network_influence(self):
        per_neighbor_factor = load_params.params_list[
            "SMOKING_NETWORK_EFFECTS"
        ]["ONSET"]["FIRST_DEGREE"]
        max_n_neighbors = load_params.params_list["MAX_N_NEIGHBORS_EFFECT"][
            "ALCOHOL"
        ]
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
        SMOKING_TRANSITION_PROBS = load_params.params_list[
            "SMOKING_TRANSITION_PROBS"
        ]

        prob = random.default_rng.uniform(0, 1)

        def probs_key():
            return (
                self.race.upper()
                + "_"
                + ("FEMALES" if self.female else "MALES")
            )

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
                increase = (
                    self.get_former_to_current_smoking_transition_network_influence()
                )
                if (
                    prob
                    <= increase * SMOKING_TRANSITION_PROBS[key]["RELAPSE"]
                ):
                    self.smoker = "Current"
                    self.n_smkg_stat_trans += 1
                    self.last_smkg_trans_tick = tick

        else:
            pass

    def get_race_sex_smoking_alc_inc_prob(self, base_prob, race_sex_pop_prop,
        inc_race_sex_prop, pct_smoking, pct_aud):
        converted_race_sex_smoking_alc_inc_prob = 0

        INC_CURRENT_SMOKING = load_params.params_list[
            "INCARCERATION_SMOKING_ASSOC"
        ]
        INC_CURRENT_AUD = load_params.params_list["INCARCERATION_AUD_ASSOC"]

        inc_current_smoking_rate = (
            INC_CURRENT_SMOKING["MIN"] + INC_CURRENT_SMOKING["MAX"]
        ) / 2
        inc_current_aud_rate = (
            INC_CURRENT_AUD["MALES"] + INC_CURRENT_AUD["FEMALES"]
        ) / 2

        if self.smoker == "Current" and self.alc_use_status == 3:
            converted_race_sex_smoking_alc_inc_prob = (
                base_prob
                * (inc_race_sex_prop / race_sex_pop_prop)
                * (inc_current_smoking_rate / pct_smoking)
                * (inc_current_aud_rate / pct_aud)
            )
        elif self.smoker == "Current" and self.alc_use_status != 3:
            converted_race_sex_smoking_alc_inc_prob = (
                base_prob
                * (inc_race_sex_prop / race_sex_pop_prop)
                * (inc_current_smoking_rate / pct_smoking)
                * ((1 - inc_current_aud_rate) / (1 - pct_aud))
            )
        elif self.smoker != "Current" and self.alc_use_status == 3:
            converted_race_sex_smoking_alc_inc_prob = (
                base_prob
                * (inc_race_sex_prop / race_sex_pop_prop)
                * ((1 - inc_current_smoking_rate) / (1 - pct_smoking))
                * (inc_current_aud_rate / pct_aud)
            )
        elif self.smoker != "Current" and self.alc_use_status != 3:
            converted_race_sex_smoking_alc_inc_prob = (
                base_prob
                * (inc_race_sex_prop / race_sex_pop_prop)
                * ((1 - inc_current_smoking_rate) / (1 - pct_smoking))
                * ((1 - inc_current_aud_rate) / (1 - pct_aud))
            )
        return converted_race_sex_smoking_alc_inc_prob

    def simulate_incarceration(
        self,
        tick,
        model,
        probability_daily_incarceration,
        probability_daily_recidivism_females,
        probability_daily_recidivism_males,
        race_sex_pop_props,
        pct_smoking,
        pct_aud,
    ):

        if self.current_incarceration_status == 1:
            return
        

        sex = "FEMALE" if self.female == 1 else "MALE"
        race_sex_key = f"{self.race.upper()}_{sex.upper()}"
        race_sex_pop_prop = race_sex_pop_props[race_sex_key]
        INC_RACE_SEX_PROP = load_params.params_list["INC_RACE_SEX_PROP"]
        inc_race_sex_prop = INC_RACE_SEX_PROP[race_sex_key]

        base_prob = probability_daily_incarceration
        if self.n_incarcerations > 0:
            time_since_release = tick - self.last_release_tick
            past_recidivism_limit = load_params.params_list["RECIDIVISM_UPDATED_PROB_LIMIT"]

            if time_since_release <= past_recidivism_limit:
                if self.female:
                    base_prob = probability_daily_recidivism_females
                else:
                    base_prob = probability_daily_recidivism_females

        specific_prob = self.get_race_sex_smoking_alc_inc_prob(base_prob, race_sex_pop_prop, inc_race_sex_prop, pct_smoking, pct_aud)
        prob = random.default_rng.uniform(0, 1)
        if prob < specific_prob:
            self.update_attributes_at_incarceration_tick(
                tick, model
            )
            cadre_logging.log_incarceration(
                self, tick, event_type="Incarceration"
                )

    def update_attributes_at_incarceration_tick(self, tick, model):
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
            partial(
                self.simulate_release, tick=self.when_to_release, model=model
            ),
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
                self.dur_cat = random.default_rng.choice(
                    MALE_SDEMP_DURATIONS, p=MALE_SDEMP_PROPS
                )

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

    def simulate_release(self, tick, model):
        # Check if the agent is still in the graph

        if self.graph is not None and self.graph.has_node(self):
            # reset incarceration status
            self.current_incarceration_status = 0
            self.last_release_tick = tick
            self.incarceration_duration = -1
            self.n_releases += 1

            cadre_logging.log_incarceration(self, tick, event_type="Release")

            # self.previous_smoking_status = self.smoker
            # self.assign_smoker_status()
            # self.update_alc_use_post_release()

    def assign_smoker_status(self):
        SMOKING_CATS = load_params.params_list["SMOKING_CATS"]
        SMOKING_PREV = load_params.params_list["SMOKING_PREV"]
        RACE_CATS = load_params.params_list["RACE_CATS"]

        # print("SMOKING_CATS", SMOKING_CATS)
        # print("SMOKING_PREV", SMOKING_PREV)

        SMOKING_PREV_BY_RACE_AND_GENDER = {
            "White": {
                0: (
                    SMOKING_PREV["WHITE_MALE_CURRENT"],
                    SMOKING_PREV["WHITE_MALE_FORMER"],
                    SMOKING_PREV["WHITE_MALE_NEVER"],
                ),
                1: (
                    SMOKING_PREV["WHITE_FEMALE_CURRENT"],
                    SMOKING_PREV["WHITE_FEMALE_FORMER"],
                    SMOKING_PREV["WHITE_FEMALE_NEVER"],
                ),
            },
            "Black": {
                0: (
                    SMOKING_PREV["BLACK_MALE_CURRENT"],
                    SMOKING_PREV["BLACK_MALE_FORMER"],
                    SMOKING_PREV["BLACK_MALE_NEVER"],
                ),
                1: (
                    SMOKING_PREV["BLACK_FEMALE_CURRENT"],
                    SMOKING_PREV["BLACK_FEMALE_FORMER"],
                    SMOKING_PREV["BLACK_FEMALE_NEVER"],
                ),
            },
            "Hispanic": {
                0: (
                    SMOKING_PREV["HISPANIC_MALE_CURRENT"],
                    SMOKING_PREV["HISPANIC_MALE_FORMER"],
                    SMOKING_PREV["HISPANIC_MALE_NEVER"],
                ),
                1: (
                    SMOKING_PREV["HISPANIC_FEMALE_CURRENT"],
                    SMOKING_PREV["HISPANIC_FEMALE_FORMER"],
                    SMOKING_PREV["HISPANIC_FEMALE_NEVER"],
                ),
            },
            "Asian": {
                0: (
                    SMOKING_PREV["ASIAN_MALE_CURRENT"],
                    SMOKING_PREV["ASIAN_MALE_FORMER"],
                    SMOKING_PREV["ASIAN_MALE_NEVER"],
                ),
                1: (
                    SMOKING_PREV["ASIAN_FEMALE_CURRENT"],
                    SMOKING_PREV["ASIAN_FEMALE_FORMER"],
                    SMOKING_PREV["ASIAN_FEMALE_NEVER"],
                ),
            },
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
                    current = (
                        network_increase
                        * SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][0]
                    )
                    SMOKING_PREV_BY_RACE_AND_GENDER[race][sex] = (
                        current,
                        1
                        - (
                            current
                            + SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][2]
                        ),
                        SMOKING_PREV_BY_RACE_AND_GENDER[race][sex][2],
                    )

        smoking_prev = SMOKING_PREV_BY_RACE_AND_GENDER[self.race][self.female]
        if not hasattr(self, "smoker"):
            self.smoker = random.default_rng.choice(
                SMOKING_CATS, p=smoking_prev
            )
        elif self.smoker != "Never":
            prob_current = smoking_prev[0] / (
                smoking_prev[0] + smoking_prev[1]
            )
            self.smoker = (
                "Current"
                if (prob_current > random.default_rng.random())
                else "Former"
            )

    def update_alc_use_post_release(self):
        # if self.alc_use_status == 0: return

        AU_PROPS = load_params.params_list["ALC_USE_PROPS"]
        ALC_USE_PROPS_INIT = [
            AU_PROPS[0],
            AU_PROPS[1],
            AU_PROPS[2],
            AU_PROPS[3],
        ]
        # print("Alc use props init: ",  ALC_USE_PROPS_INIT)
        ALC_USE_PROPS_POSTRELEASE = list(ALC_USE_PROPS_INIT)
        ALC_USE_PROPS_POSTRELEASE[3] = 0.17
        ALC_USE_PROPS_POSTRELEASE[2] = (
            ALC_USE_PROPS_INIT[2]
            - abs(ALC_USE_PROPS_POSTRELEASE[3] - ALC_USE_PROPS_INIT[3]) / 3
        )
        ALC_USE_PROPS_POSTRELEASE[1] = (
            ALC_USE_PROPS_INIT[1]
            - abs(ALC_USE_PROPS_POSTRELEASE[3] - ALC_USE_PROPS_INIT[3]) / 3
        )
        ALC_USE_PROPS_POSTRELEASE[0] = (
            ALC_USE_PROPS_INIT[0]
            - abs(ALC_USE_PROPS_POSTRELEASE[3] - ALC_USE_PROPS_INIT[3]) / 3
        )

        # print("Alcohol states init", ALC_USE_PROPS_INIT)
        # print("Alcohol states PR", ALC_USE_PROPS_POSTRELEASE)
        # print("Sum PR", sum(ALC_USE_PROPS_POSTRELEASE))

        if self.n_releases > 0:
            alc_use_status_postrelease = random.default_rng.choice(
                range(0, len(ALC_USE_PROPS_POSTRELEASE)),
                p=[
                    x / sum(ALC_USE_PROPS_POSTRELEASE)
                    for x in ALC_USE_PROPS_POSTRELEASE
                ],
            )
            # print("Post-release status selected = ", alc_use_status_postrelease)
            self.alc_use_status = alc_use_status_postrelease


def create_person(nid, agent_type, rank, **kwargs):
    return Person(nid, agent_type, rank)


def restore_person(agent_data):
    uid = agent_data[0]
    return Person(uid[0], uid[1], uid[2], agent_data[1])
