from numpy import random
import statistics

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
    age_sum = 0
    alc_use_status = {}

    my_persons = {}
    for i in range(11):
        my_persons[i] = Person()
        my_persons[i].name = i
        age_sum = my_persons[i].age + age_sum
        alc_use_status[i] = my_persons[i].alc_use_status

        print(my_persons[i].name)
        print(my_persons[i].age)
        print(my_persons[i].alc_use_status, "\n")
    
    
    print((alc_use_status.values()), "\n")
    print("Total number of persons is: " + str(len(my_persons)))
    print("Their average age is: " + str(age_sum/len(my_persons)))
    print("Their median level of alcohol use is " + 
    str(statistics.median(alc_use_status.values())))

    




if __name__ == "__main__":
    main()
        