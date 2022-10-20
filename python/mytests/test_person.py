from statistics import mean as mean
import unittest
import numpy as np
import pandas as pd
from pycadre import cadre_model
import pycadre.load_params
from mpi4py import MPI
from repast4py import context as ctx


class TestPerson(unittest.TestCase):
    params_list = pycadre.load_params.load_params(
        "../../cadre/python/test_data/test_params.yaml", ""
    )

    def test_age_assignment(self):

        ages = []
        MIN_AGE = TestPerson.params_list["MIN_AGE"]
        MAX_AGE = TestPerson.params_list["MAX_AGE"]

        mean_age_target = (MIN_AGE + MAX_AGE) / 2

        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=TestPerson.params_list)

        for person in model.context.agents():
            ages.append(person.age)

        for age in ages:
            self.assertTrue(age >= MIN_AGE)
            self.assertTrue(age <= MAX_AGE)

            if TestPerson.params_list["N_AGENTS"] >= 1000:
                # only try this if n is sufficiently large, or test fails
                self.assertAlmostEqual(np.mean(ages), mean_age_target, delta=1)

    def test_race_assignment(self):

        RD = TestPerson.params_list["RACE_DISTRIBUTION"]
        RACE_DISTRIBUTION = [RD["White"], RD["Black"], RD["Hispanic"], RD["Asian"]]
        races = []
        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=TestPerson.params_list)
        model.start()

        for person in model.context.agents():
            races.append(person.race)

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
        TICK_TO_YEAR_RATIO = TestPerson.params_list[
            "TICK_TO_YEAR_RATIO"
        ]  # xx ticks make a year

        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=TestPerson.params_list)

        for person in model.context.agents():
            ages_init.append(person.age)
            person.aging()
            ages_final.append(person.age)

        diff_in_ages = np.subtract(np.array(ages_final), np.array(ages_init))

        self.assertAlmostEqual(np.mean(diff_in_ages), 1 / TICK_TO_YEAR_RATIO)

    def test_simulate_incarceration(self):
        nsteps = 1
        inc_states = []

        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=TestPerson.params_list)

        # test case where 0 < incarceration probability < 1
        probability_daily_incarceration = 0.5

        for person in model.context.agents():
            self.assertTrue(
                person.current_incarceration_status == 0,
                "all persons are not initially un-incarcerated",
            )
            person.simulate_incarceration(
                tick=nsteps,
                probability_daily_incarceration=probability_daily_incarceration,
            )
            inc_states.append(person.current_incarceration_status)

        if TestPerson.params_list["N_AGENTS"] >= 1000:
            self.assertAlmostEqual(
                mean(inc_states), probability_daily_incarceration, delta=0.1
            )

        # test case where incarceration probability = 1
        probability_daily_incarceration = 1
        for person in model.context.agents():
            person.simulate_incarceration(
                tick=nsteps, probability_daily_incarceration=1
            )
            inc_states.append(person.current_incarceration_status)
            self.assertTrue(
                person.current_incarceration_status == 1,
                "not incarcerated, even though probability of incarceration is 1",
            )

        return model

    def test_simulate_release(self):
        model = TestPerson.test_simulate_incarceration(self)
        nsteps = 1
        inc_states = []

        for p in model.context.agents():
            # print(p.current_incarceration_status)
            inc_states.append(p.current_incarceration_status)

        inc_states = []  # make incarceration status list empty

        for p in model.context.agents():
            p.sentence_duration = 0  # assign
            p.simulate_release(tick=nsteps)
            inc_states.append(p.current_incarceration_status)
            self.assertTrue(
                p.current_incarceration_status == 0,
                "all not unincarcerated, even though max sentence duration is 0",
            )

    def test_assign_smoking_status(self):

        """
        Test smoking use status distributions:
         - initialize model with 'STOP_AT' changed to 25
         - Now the model includes transitions between current and former smoking states
         - run the model

        Compare if the proportion of current/former/never white male smokers
        is within 0.03 units of the target proportions (0-1 scale)
        Tests for other demographic groups to be added
        """

        test_smoking_status_params_list = TestPerson.params_list.copy()
        test_smoking_status_params_list["STOP_AT"] = 25

        SMOKING_CATS = TestPerson.params_list["SMOKING_CATS"]
        SMOKING_PREV = TestPerson.params_list["SMOKING_PREV"]

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

        nsteps = 1
        smokers = []
        races = []
        sexes = []

        model = cadre_model.Model(
            comm=MPI.COMM_WORLD, params=test_smoking_status_params_list
        )
        model.start()

        for person in model.context.agents():
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
            delta=0.03,
        )
        self.assertAlmostEqual(
            len(white_male_former_smoker_ids_intersect) / len(white_male_ids_intersect),
            SMOKING_PREV_WHITE_MALE[1],
            delta=0.03,
        )
        self.assertAlmostEqual(
            len(white_male_never_smoker_ids_intersect) / len(white_male_ids_intersect),
            SMOKING_PREV_WHITE_MALE[2],
            delta=0.03,
        )

    def test_alco_status(self):

        """
        Test alcohol use status distributions:
         - initialize model with 'STOP_AT' changed to 25
         - run the model

        Compare if the proportion of persons in each alcohol use state
        is within 0.01 units of the target proportion (0-1 scale)
        """

        test_alco_status_params_list = TestPerson.params_list.copy()

        ABSTAINERS_PROP = test_alco_status_params_list["ALC_USE_PROPS"]["A"]
        OCCASIONAL_PROP = test_alco_status_params_list["ALC_USE_PROPS"]["O"]
        REGULAR_PROP = test_alco_status_params_list["ALC_USE_PROPS"]["R"]
        AUD_PROP = test_alco_status_params_list["ALC_USE_PROPS"]["D"]

        test_alco_status_params_list["STOP_AT"] = 25
        all_alco = []

        model = cadre_model.Model(
            comm=MPI.COMM_WORLD, params=test_alco_status_params_list
        )
        model.start()

        for person in model.context.agents():
            all_alco.append(person.alc_use_status)

        alco_dist = pd.value_counts(np.array(all_alco)) / len(all_alco)
        self.assertAlmostEqual(alco_dist[0], ABSTAINERS_PROP, delta=0.01)
        self.assertAlmostEqual(alco_dist[1], OCCASIONAL_PROP, delta=0.01)
        self.assertAlmostEqual(alco_dist[2], REGULAR_PROP, delta=0.01)
        self.assertAlmostEqual(alco_dist[3], AUD_PROP, delta=0.01)

    def test_sentence_duration_emp(self):

        DU_dis = TestPerson.params_list["SENTENCE_DURATION_EMP"]

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

        model = cadre_model.Model(comm=MPI.COMM_WORLD, params=TestPerson.params_list)
        model.start()

        for person in model.context.agents():
            if person.female == 1:
                f_du_collect.append(person.incarceration_duration)
            else:
                m_du_collect.append(person.incarceration_duration)

        f_du_collect_dist = pd.value_counts(np.array(f_du_collect)) / len(f_du_collect)
        m_du_collect_dist = pd.value_counts(np.array(m_du_collect)) / len(m_du_collect)

    def test_recidivism_model(self):

        """
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
        """

        test_recividism_params_list = TestPerson.params_list.copy()

        N_AGENTS = test_recividism_params_list["STOP_AT"]
        test_recividism_params_list["STOP_AT"] = 2
        test_recividism_params_list["STOP_AT"] = 2
        test_recividism_params_list["RECIDIVISM_UPDATED_PROB_LIMIT"] = 1
        test_recividism_params_list["PROBABILITY_DAILY_RECIDIVISM"]["FEMALES"] = 1
        test_recividism_params_list["PROBABILITY_DAILY_RECIDIVISM"]["MALES"] = 1

        model = cadre_model.Model(
            comm=MPI.COMM_WORLD, params=test_recividism_params_list
        )

        for person in model.context.agents():
            person.current_incarceration_status = 0
            person.last_incarceration_tick = -1
            person.last_release_tick = 0
            person.when_to_release = 0
            person.n_incarcerations = 1

        model.start()

        for person in model.context.agents():
            if person.name < N_AGENTS:
                # needed because agents enter at all times since age initialization was changed,
                # and newly entering agents don't become incarerated because their attributes are not reset
                self.assertEqual(person.current_incarceration_status, 1)
                self.assertEqual(person.n_incarcerations, 2)


if __name__ == "__main__":
    unittest.main()
