from numpy import random
import statistics

class Person():
    def __init__(self, name=None, age=None, alc_use_status=None):
        if age == None:
            age = random.randint(18, 65)
        if alc_use_status == None:
            alc_use_status = random.randint(0, 4) # (0,3) gives a max of 2. QT is this expected behavior?

        self.name = name    
        self.age = age
        self.alc_use_status = alc_use_status

    def initialize_population(n:int=10):
        # QT: didn't use self here because then I couldn't override the default param val in main
        my_persons = {}
        age_sum = 0
        alc_use_status = {}
        alc_use_status_vals = {}
        
        # initialize agents and attributes
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

        # transition agents from alc use states
        # QT: Can this be its own method? If so, how do I get it to access the objects it needs from above methods? 
        # transition probabilities
        # level up
        trans_prob_0_1 = 0/100 
        trans_prob_1_2 = 1/100
        trans_prob_2_3 = 1/100
        # level down
        trans_prob_1_0 = 0.5/100
        trans_prob_2_1 = 0.5/100
        trans_prob_3_2 = 0.5/100

        changes = 0

        for i in range(len(my_persons)):
            prob = random.uniform(0, 1)

            if my_persons[i].alc_use_status == 0:
                if (prob <= trans_prob_0_1):
                    my_persons[i].alc_use_status += 1
                    changes+=1
                    print("change!")

            elif my_persons[i].alc_use_status == 1:
                if (prob <= trans_prob_1_2):
                    my_persons[i].alc_use_status += 1
                    changes+=1
                    print("change!")
                elif (prob > 1-trans_prob_1_0):
                    my_persons[i].alc_use_status -= 1
                    changes += 1
                    print("change!")
            
            elif my_persons[i].alc_use_status == 2:
                if (prob <= trans_prob_2_3):
                    my_persons[i].alc_use_status += 1
                    changes += 1
                    print("change!")
                elif (prob > 1-trans_prob_2_1):
                    my_persons[i].alc_use_status -= 1
                    changes += 1
                    print("change!")

            elif my_persons[i].alc_use_status == 3:
                if (prob > 1-trans_prob_3_2):
                    my_persons[i].alc_use_status -= 1
                    changes += 1
                    print("change!")

        print("Number of transitions is " + str(changes))

    # add alcohol transition function here
    def transition_alc_use():
        pass
    
def main():
    Person.initialize_population(10001) #QT: See above for overriding default params
    #Person.transition_alc_use()

    #QT: Where would a time loop go?
  
if __name__ == "__main__":
    main()
    
        
