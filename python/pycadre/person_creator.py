from pycadre import cadre_person

person_creator = None


def init_person_creator(rank):
    global person_creator
    if person_creator == None:
        person_creator = PersonCreator(rank)
    return person_creator


class PersonCreator:
    def __init__(self, rank: int):
        self.id = 0
        self.rank = rank

    def create_person(self, age=None, race=None, female=None, tick=None):
        person = cadre_person.Person(
            self.id,
            cadre_person.Person.TYPE,
            self.rank,
            age=age,
            race=race,
            female=female,
            tick=tick,
        )
        self.id += 1
        return person
