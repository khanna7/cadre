from numpy import random
import statistics

class Person():
    def __init__(self, name=None, age=None, alc_use_status=None):
        if age == None:
            age = random.randint(18, 65)
        if alc_use_status == None:
            alc_use_status = random.randint(0, 4) # (0,3) gives a max of 2 

        self.name = name    
        self.age = age
        self.alc_use_status = alc_use_status

    def initialize_population(n:int=10):
        my_persons = {}
        age_sum = 0
        alc_use_status = {}
        alc_use_status_vals = {}
        
        for i in range(n):
            my_persons[i] = Person()
            my_persons[i].name = i
            age_sum = my_persons[i].age + age_sum
            alc_use_status[i] = my_persons[i].alc_use_status

            print(my_persons[i].name)
            print(my_persons[i].age)
            print(my_persons[i].alc_use_status, "\n")
        
        alc_use_status_vals = alc_use_status.values()

        print("Number of agents is: " + 
            str(len(my_persons)))
        print("Mean agent age is: " + 
            str(age_sum/len(my_persons)))
        print("Median level of alcohol use is " + 
            str(statistics.median(alc_use_status_vals)))
        print("Max level of alcohol use is " + 
            str(max(alc_use_status_vals)))
        print("Min level of alcohol use is " + 
            str(min(alc_use_status_vals)))


    # add alcohol transition function here
    def transition_alc_use():
        pass
    
def main():
    Person.initialize_population(10001)
    Person.transition_alc_use()
  
if __name__ == "__main__":
    main()
    
        