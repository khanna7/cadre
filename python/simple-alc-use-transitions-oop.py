from numpy import random

class Person():
    def __init__(self, age=None, alc_use_status=None):
        if age == None:
            age = random.randint(18, 65)
        if alc_use_status == None:
            alc_use_status = random.randint(0, 3)
        self.age = age
        self.alc_use_status = alc_use_status

p1=Person()

        