from numpy import random

class Person():
    def __init__(self, name=None, age=None, alc_use_status=None):
        if age == None:
            age = random.randint(18, 65)
        if alc_use_status == None:
            alc_use_status = random.randint(0, 3)

        self.name = name    
        self.age = age
        self.alc_use_status = alc_use_status

    def print_person_characteristics(self):
        print("This object's name is {}.".format(self.name))

def main():
    my_persons = {}
    for i in range(11):
        my_persons[i] = Person()
        my_persons[i].name = i

        print(my_persons[i].name)
        print(my_persons[i].age)
        print(my_persons[i].alc_use_status, "\n")
        print(len(my_persons))

    




if __name__ == "__main__":
    main()
        