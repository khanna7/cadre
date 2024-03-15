import os
from statistics import mean as mean
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
from pycadre import cadre_model
from pycadre.person_creator import PersonCreator, init_person_creator
import pycadre.load_params
from mpi4py import MPI
from repast4py import context as ctx, schedule

class TestPerson(unittest.TestCase):
    def setUp(self):
        self.params_list = pycadre.load_params.load_params(
            "../../python/test_data/test_params.yaml", ""
        )

    def test_post_release_alc_use(self):
        states=[]
        
        person_creator = init_person_creator()
        n = 10000
        
        for i in range(n):
            p = person_creator.create_person()
            p.n_releases = 1
            p.update_alc_use_post_release()
            new_state = p.alc_use_status
            states.append(new_state)
            
        count_of_0 = states.count(0)
        count_of_1 = states.count(1)
        count_of_2 = states.count(2)
        count_of_3 = states.count(3)
        
        self.assertAlmostEqual(count_of_0/n, 0.31, delta=0.01) #allt are hardcoded right now - should be changed
        self.assertAlmostEqual(count_of_1/n, 0.51, delta=0.01) 
        self.assertAlmostEqual(count_of_2/n, 0.01, delta=0.01) 
        self.assertAlmostEqual(count_of_3/n, 0.17, delta=0.01) 
        
    def test_age_assignment(self):

        ages = []
        MIN_AGE = self.params_list["MIN_AGE"]
        MAX_AGE = self.params_list["MAX_AGE"]

        mean_age_target = (MIN_AGE + MAX_AGE) / 2

        person_creator = init_person_creator()
        for i in range(1000):
            p = person_creator.create_person()
            ages.append(p.age)

        for age in ages:
            self.assertTrue(age >= MIN_AGE)
            self.assertTrue(age <= MAX_AGE + 1)
            self.assertAlmostEqual(np.mean(ages), mean_age_target, delta=1)

    def test_person_creator(self):
        person_creator = PersonCreator()
        p1 = person_creator.create_person(tick=1, age=47, female=False, race="White")
        self.assertEqual(p1.entry_at_tick, 1)
        self.assertEqual(p1.age, 47)
        self.assertEqual(p1.female, False)
        self.assertEqual(p1.race, "White")

        p2 = person_creator.create_person(tick=1, age=0)
        self.assertEqual(p2.age, self.params_list["MIN_AGE"])

    def test_race_assignment(self):

        RD = self.params_list["RACE_DISTRIBUTION"]
        RACE_DISTRIBUTION = [RD["White"], RD["Black"], RD["Hispanic"], RD["Asian"]]
        races = []
        pc = init_person_creator()

        for p in [pc.create_person() for i in range(1000)]:
            races.append(p.race)

        # print("Races: "  + str(races))
        race_dist = pd.value_counts(np.array(races)) / len(races)
        # print("Races: " + str(race_dist))

        self.assertAlmostEqual(race_dist.White, RACE_DISTRIBUTION[0], delta=2)
        self.assertAlmostEqual(race_dist.Black, RACE_DISTRIBUTION[1], delta=2)
        self.assertAlmostEqual(race_dist.Hispanic, RACE_DISTRIBUTION[2], delta=2)
        self.assertAlmostEqual(race_dist.Asian, RACE_DISTRIBUTION[3], delta=2)

    ## test alcohol use assignment

    ## test alcohol status transition

    def test_aging(self):
        ages_init = []
        ages_final = []
        TICK_TO_YEAR_RATIO = self.params_list[
            "TICK_TO_YEAR_RATIO"
        ]  # xx ticks make a year

        #model = cadre_model.Model(comm=MPI.COMM_WORLD, params=self.params_list)

        for person in [init_person_creator().create_person() for i in range(1000)]:
            ages_init.append(person.age)
            person.aging()
            ages_final.append(person.age)

        diff_in_ages = np.subtract(np.array(ages_final), np.array(ages_init))

        self.assertAlmostEqual(np.mean(diff_in_ages), 1 / TICK_TO_YEAR_RATIO)

    """ def test_simulate_incarceration(self):
        nsteps = 1
        inc_states = []

        #model = cadre_model.Model(comm=MPI.COMM_WORLD, params=self.params_list)

        # test case where 0 < incarceration probability < 1
        probability_daily_incarceration = 0.5

        for person in [init_person_creator().create_person() for i in range(1000)]:
            self.assertTrue(
                person.current_incarceration_status == 0,
                "all persons are not initially un-incarcerated",
            )
            person.simulate_incarceration(
                tick=nsteps,
                probability_daily_incarceration=probability_daily_incarceration,
            )
            inc_states.append(person.current_incarceration_status)

        if self.params_list["N_AGENTS"] >= 1000:
            self.assertAlmostEqual(
                mean(inc_states), probability_daily_incarceration, delta=0.1
            )

        # test case where incarceration probability = 1

        probability_daily_incarceration = 1
        for person in [init_person_creator().create_person() for i in range(1000)]:
            person.simulate_incarceration(
                tick=nsteps, probability_daily_incarceration=1
            )
            inc_states.append(person.current_incarceration_status)
            self.assertTrue(
                person.current_incarceration_status == 1,
                "not incarcerated, even though probability of incarceration is 1",
            )
 """
    def test_simulate_release(self):
        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=self.params_list)
        nsteps = 1
        inc_states = []  # make incarceration status list empty

        for p in [init_person_creator().create_person() for i in range(1000)]:
            p.sentence_duration = 0  # assign
            p.simulate_release(model=model, tick=nsteps)
            inc_states.append(p.current_incarceration_status)
            self.assertTrue(
                p.current_incarceration_status == 0,
                "all not unincarcerated, even though max sentence duration is 0",
            )

    def test_assign_smoking_status(self):

        """
        Test smoking use status distributions:
         - simulate 25 steps of smoking transitions

        Compare if the proportion of current/former/never white male smokers
        is within 0.03 units of the target proportions (0-1 scale)
        Tests for other demographic groups to be added
        """

        SMOKING_CATS = self.params_list["SMOKING_CATS"]
        SMOKING_PREV = self.params_list["SMOKING_PREV"]

        SMOKING_PREV_WHITE_MALE = [
            SMOKING_PREV["WHITE_MALE_CURRENT"],
            SMOKING_PREV["WHITE_MALE_FORMER"],
            SMOKING_PREV["WHITE_MALE_NEVER"],
        ]
        SMOKING_PREV_WHITE_FEMALE = [
            SMOKING_PREV["WHITE_FEMALE_CURRENT"],
            SMOKING_PREV["WHITE_FEMALE_FORMER"],
            SMOKING_PREV["WHITE_FEMALE_NEVER"],
        ]
        SMOKING_PREV_BLACK_MALE = [
            SMOKING_PREV["BLACK_MALE_CURRENT"],
            SMOKING_PREV["BLACK_MALE_FORMER"],
            SMOKING_PREV["BLACK_MALE_NEVER"],
        ]
        SMOKING_PREV_BLACK_FEMALE = [
            SMOKING_PREV["BLACK_FEMALE_CURRENT"],
            SMOKING_PREV["BLACK_FEMALE_FORMER"],
            SMOKING_PREV["BLACK_FEMALE_NEVER"],
        ]
        SMOKING_PREV_HISPANIC_MALE = [
            SMOKING_PREV["HISPANIC_MALE_CURRENT"],
            SMOKING_PREV["HISPANIC_MALE_FORMER"],
            SMOKING_PREV["HISPANIC_MALE_NEVER"],
        ]
        SMOKING_PREV_HISPANIC_FEMALE = [
            SMOKING_PREV["HISPANIC_FEMALE_CURRENT"],
            SMOKING_PREV["HISPANIC_FEMALE_FORMER"],
            SMOKING_PREV["HISPANIC_FEMALE_NEVER"],
        ]
        SMOKING_PREV_ASIAN_MALE = [
            SMOKING_PREV["ASIAN_MALE_CURRENT"],
            SMOKING_PREV["ASIAN_MALE_FORMER"],
            SMOKING_PREV["ASIAN_MALE_NEVER"],
        ]
        SMOKING_PREV_ASIAN_FEMALE = [
            SMOKING_PREV["ASIAN_FEMALE_CURRENT"],
            SMOKING_PREV["ASIAN_FEMALE_FORMER"],
            SMOKING_PREV["ASIAN_FEMALE_NEVER"],
        ]

        smokers = []
        races = []
        sexes = []

        for person in [init_person_creator().create_person() for i in range(2000)]:
            for j in range(25):
                person.aging()
                person.transition_smoking_status(j)
            smokers.append(person.smoker)
            races.append(person.race)
            sexes.append(person.female)

        white_indices = [i for i, x in enumerate(races) if x == "White"]
        black_indices = [i for i, x in enumerate(races) if x == "Black"]
        hispanic_indices = [i for i, x in enumerate(races) if x == "Hispanic"]
        asian_indices = [i for i, x in enumerate(races) if x == "Asian"]

        male_indices = [i for i, x in enumerate(sexes) if x == 0]
        female_indices = [i for i, x in enumerate(sexes) if x == 1]

        current_smoker_indices = [i for i, x in enumerate(smokers) if x == "Current"]
        former_smoker_indices = [i for i, x in enumerate(smokers) if x == "Former"]
        never_smoker_indices = [i for i, x in enumerate(smokers) if x == "Never"]

        white_male_ids_collate = [white_indices, male_indices]
        white_male_ids_intersect = set.intersection(*map(set, white_male_ids_collate))

        white_male_current_smoker_ids_collate = [
            white_indices,
            male_indices,
            current_smoker_indices,
        ]
        white_male_current_smoker_ids_intersect = set.intersection(
            *map(set, white_male_current_smoker_ids_collate)
        )

        white_male_former_smoker_ids_collate = [
            white_indices,
            male_indices,
            former_smoker_indices,
        ]
        white_male_former_smoker_ids_intersect = set.intersection(
            *map(set, white_male_former_smoker_ids_collate)
        )

        white_male_never_smoker_ids_collate = [
            white_indices,
            male_indices,
            never_smoker_indices,
        ]
        white_male_never_smoker_ids_intersect = set.intersection(
            *map(set, white_male_never_smoker_ids_collate)
        )

        self.assertAlmostEqual(
            len(white_male_current_smoker_ids_intersect)
            / len(white_male_ids_intersect),
            SMOKING_PREV_WHITE_MALE[0],
            delta=0.1,
        )
        self.assertAlmostEqual(
            len(white_male_former_smoker_ids_intersect) / len(white_male_ids_intersect),
            SMOKING_PREV_WHITE_MALE[1],
            delta=0.1,
        )
        self.assertAlmostEqual(
            len(white_male_never_smoker_ids_intersect) / len(white_male_ids_intersect),
            SMOKING_PREV_WHITE_MALE[2],
            delta=0.1,
        )

    def test_alco_status(self):

        """
        Test alcohol use status distributions:
         - simulate 25 steps of alc use transitions

        Compare if the proportion of persons in each alcohol use state
        is within 0.01 units of the target proportion (0-1 scale)
        """

        NON_PROP = self.params_list["ALC_USE_PROPS"][0]
        CAT1_PROP = self.params_list["ALC_USE_PROPS"][1]
        CAT2_PROP = self.params_list["ALC_USE_PROPS"][2]
        CAT3_PROP = self.params_list["ALC_USE_PROPS"][3]

        all_alco = []

        for person in [init_person_creator().create_person() for i in range(10000)]:
            for i in range(25):
                person.aging()
                person.transition_alc_use()
            all_alco.append(person.alc_use_status)

        alco_dist = pd.value_counts(np.array(all_alco)) / len(all_alco)
        self.assertAlmostEqual(alco_dist[0], NON_PROP, delta=0.02)
        self.assertAlmostEqual(alco_dist[1], CAT1_PROP, delta=0.02)
        self.assertAlmostEqual(alco_dist[2], CAT2_PROP, delta=0.02)
        self.assertAlmostEqual(alco_dist[3], CAT3_PROP, delta=0.02)


    def test_transition_alc_use(self):
        person_creator = init_person_creator()
        person = person_creator.create_person()
        person.alc_use_status = 1  # Starting in state 1
        person.current_incarceration_status = 0  # Not incarcerated
        ALC_USE_STATES = self.params_list["ALC_USE_STATES"]

        for current_state in ALC_USE_STATES: 
            N = 100000
            sums = {}
            for i in range(N):
                person.alc_use_status = 1
                new_state = person.get_new_alc_use_state(current_state)
                if new_state in sums:
                    sums[new_state] += 1
                else:
                    sums[new_state] = 1

            tot = 0
            for state in ALC_USE_STATES:
                tot += ALC_USE_STATES[current_state][state]
            scaled_states = {}
            for state in ALC_USE_STATES:
                scaled_states[state] = ALC_USE_STATES[current_state][state] / tot
        
            for state in sums:
                expected = scaled_states[state]
                result = sums[state]/N
                self.assertAlmostEqual(expected, result, delta=0.006)
                print(expected, result, abs(expected - result))

    # def test_transition_alc_use_statistically(self):
    #     person_creator = init_person_creator()
    #     transitions = {0: 0, 1: 0, ...}  # Include all possible states here
    #     n = 10000  # Number of simulations

    #     for _ in range(n):
    #         person = person_creator.create_person()
    #         person.alc_use_status = 1  # Starting in state 1
    #         person.transition_alc_use()  # Execute the transition
    #         transitions[person.alc_use_status] += 1  # Record the outcome

    #     # Now transitions dict contains the count of transitions to each state
    #     observed = [transitions[state] for state in sorted(transitions)]
    #     expected = [n * probability for probability in expected_probabilities]  # Define your expected probabilities list

    #     # Perform the chi-squared test
    #     chi_square, p_value = stats.chisquare(observed, f_exp=expected)

    #     # Set your significance level
    #     alpha = 0.05
    #     self.assertLess(p_value, alpha, "The transition probabilities do not match the expected distribution.")


""" 
    def test_sentence_duration_emp(self):
        # TODO: I think this test doesn't have any assertions (i.e. it cannot fail).
        # Write some assertions.
        DU_dis = self.params_list["SENTENCE_DURATION_EMP"]

        f_du_dis = [
            DU_dis["females"][0],
            DU_dis["females"][1],
            DU_dis["females"][2],
            DU_dis["females"][3],
            DU_dis["females"][4],
        ]
        m_du_dis = [
            DU_dis["males"][0],
            DU_dis["males"][1],
            DU_dis["males"][2],
            DU_dis["males"][3],
            DU_dis["males"][4],
        ]

        nsteps = 25
        f_du_collect = []
        m_du_collect = []
        schedule.init_schedule_runner(MPI.COMM_WORLD)
        
        pct_smoking = 0.99
        race_sex_pop_props
        
        for person in [init_person_creator().create_person() for i in range(5000)]:
            for tick in range(nsteps):
                person.aging()
                person.simulate_incarceration(
                    tick=tick,
                    probability_daily_incarceration=self.params_list[
                        "PROBABILITY_DAILY_INCARCERATION"
                    ],
                )
                if person.current_incarceration_status == 1:
                    person.incarceration_duration += 1

            if person.female == 1:
                f_du_collect.append(person.incarceration_duration)
            else:
                m_du_collect.append(person.incarceration_duration)

        f_du_collect_dist = pd.value_counts(np.array(f_du_collect)) / len(f_du_collect)
        m_du_collect_dist = pd.value_counts(np.array(m_du_collect)) / len(m_du_collect)
 """
"""     def test_recidivism_model(self):

        \"""
        Test recidivism model by creating a copy of the params dictionary & setting:
         stop_at parameter = 2

        and initialize model with all agents:
         current incarceration status to 0
         last incarceration tick set to -1
         daily recidivism probability set to 1
         number prior incarcerations set to 1

        When the model completes running, all agents should be:
          currently incarcerated
          n_incarcerations should be zero
        \"""

        test_recividism_params_list = self.params_list.copy()

        N_AGENTS = 1
        test_recividism_params_list["STOP_AT"] = 2
        test_recividism_params_list["RECIDIVISM_UPDATED_PROB_LIMIT"] = 1
        test_recividism_params_list["PROBABILITY_DAILY_RECIDIVISM"]["FEMALES"] = 1
        test_recividism_params_list["PROBABILITY_DAILY_RECIDIVISM"]["MALES"] = 1

        schedule.init_schedule_runner(MPI.COMM_WORLD)

        people = []
        for person in [init_person_creator().create_person() for i in range(5000)]:
            people.append(person)
            person.current_incarceration_status = 0
            person.last_incarceration_tick = -1
            person.last_release_tick = 0
            person.when_to_release = 0
            person.n_incarcerations = 1
            for tick in range(2):
                person.simulate_recidivism(
                    tick=tick,
                    probability_daily_recidivism_females=test_recividism_params_list[
                        "PROBABILITY_DAILY_RECIDIVISM"
                    ]["FEMALES"],
                    probability_daily_recidivism_males=test_recividism_params_list[
                        "PROBABILITY_DAILY_RECIDIVISM"
                    ]["MALES"],
                    probability_daily_incarceration=test_recividism_params_list[
                        "PROBABILITY_DAILY_INCARCERATION"
                    ],
                )

        for person in people:
            if person.name < N_AGENTS:
                # needed because agents enter at all times since age initialization was changed,
                # and newly entering agents don't become incarerated because their attributes are not reset
                self.assertEqual(person.current_incarceration_status, 1)
                self.assertEqual(person.n_incarcerations, 2) """

if __name__ == "__main__":
    unittest.main()
