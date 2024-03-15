from pycadre import cadre_person
import pycadre.load_params as load_params
from repast4py import random

person_creator = None


def init_person_creator():
    global person_creator
    if person_creator is None:
        person_creator = PersonCreator()
    return person_creator


class PersonCreator:
    def __init__(self):
        self.id = 0

    def create_person(
        self, age=None, race=None, female=None, tick=None, graph=None
    ):
        MIN_AGE = load_params.params_list["MIN_AGE"]
        MAX_AGE = load_params.params_list["MAX_AGE"]
        RACE_CATS = load_params.params_list["RACE_CATS"]
        FEMALE_PROP = load_params.params_list["FEMALE_PROP"]
        RD = load_params.params_list["RACE_DISTRIBUTION"]
        RACE_DISTRIBUTION = [
            RD["White"],
            RD["Black"],
            RD["Hispanic"],
            RD["Asian"],
        ]
        AU_PROPS = load_params.params_list["ALC_USE_PROPS"]
        ALC_USE_PROPS = [AU_PROPS[0], AU_PROPS[1], AU_PROPS[2], AU_PROPS[3]]

        my_age = (
            max(MIN_AGE, age)
            if age is not None
            else random.default_rng.uniform(MIN_AGE, MAX_AGE)
        )
        race = (
            race
            if race is not None
            else random.default_rng.choice(RACE_CATS, p=RACE_DISTRIBUTION)
        )
        female = (
            female
            if female is not None
            else random.default_rng.binomial(1, FEMALE_PROP)
        )
        alc_use_status = random.default_rng.choice(
            range(0, len(ALC_USE_PROPS)), p=ALC_USE_PROPS
        )
        # print("New agent's alcohol use status is", alc_use_status)
        person = cadre_person.Person(
            self.id,
            cadre_person.Person.TYPE,
            0,
            alc_use_status,
            age=my_age,
            race=race,
            female=female,
            tick=tick,
            graph=graph,
        )
        self.id += 1
        return person
