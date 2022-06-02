from numpy import random
import statistics

class Person():
    def __init__(self, name=None, age=None, race=None, alc_use_status=None):

        if age == None:
            age = random.randint(18, 65)

        if alc_use_status == None:
            alc_use_status = random.randint(0, 4) # (0,3) gives a max of 2. QT is this expected behavior?

        if age == None:
            age = random.randint(18, 65)
        
   
        race_distribution = [
            71.4/100, #white alone
            8.5/100, #black alone
            16.3/100, #hispanic alone
            3.7/100 #asian alone
        ]

        race_cats = ["white", "black", "hispanic", "other"]
        
        self.name = name    
        self.age = age
        self.race = random.choice(race_cats)
        self.alc_use_status = alc_use_status

    def transition_alc_use(self):

        # level up
        trans_prob_0_1 = 0/100 
        trans_prob_1_2 = 1/100
        trans_prob_2_3 = 1/100
        # level down
        trans_prob_1_0 = 0.5/100
        trans_prob_2_1 = 0.5/100
        trans_prob_3_2 = 0.5/100

        changes = 0
        prob = random.uniform(0, 1)
        if self.alc_use_status == 0:
            if (prob <= trans_prob_0_1):
                self.alc_use_status += 1
                changes+=1
                #print("change!")

        elif self.alc_use_status == 1:
            if (prob <= trans_prob_1_2):
                self.alc_use_status += 1
                changes+=1
                #print("change!")
            elif (prob > 1-trans_prob_1_0):
                self.alc_use_status -= 1
                changes += 1
                #print("change!")
        
        elif self.alc_use_status == 2:
            if (prob <= trans_prob_2_3):
                self.alc_use_status += 1
                changes += 1
                #print("change!")
            elif (prob > 1-trans_prob_2_1):
                self.alc_use_status -= 1
                changes += 1
                #print("change!")

        elif self.alc_use_status == 3:
            if (prob > 1-trans_prob_3_2):
                self.alc_use_status -= 1
                changes += 1
                #print("change!")

def initialize_population(n):
    # QT: didn't use self here because then I couldn't override the default param val in main
    my_persons = [] #use array instead
    age_sum = 0
    alc_use_status = []
    alc_use_status_vals = []
    
    # initialize agents and attributes
    for i in range(n):
        my_persons.append(Person(i))
        age_sum = my_persons[i].age + age_sum
        alc_use_status.append(my_persons[i].alc_use_status)  

        print(my_persons[i].name)
        print(my_persons[i].age)
        print(my_persons[i].alc_use_status, "\n")

    print("Number of agents is: " + 
        str(len(my_persons)))
    print("Mean agent age is: " + 
        str(age_sum/len(my_persons)))
    print("Max level of alcohol use is " + 
        str(max(alc_use_status)))
    print("Min level of alcohol use is " + 
        str(min(alc_use_status)))

    return my_persons

    
def main():
    persons = initialize_population(10001) 

    MAXTIME=100
    
    for time in range(MAXTIME):
        print("Timestep = " + str(time))
        
        for person in persons:
            person.transition_alc_use()
  
if __name__ == "__main__":
    main()
    
        
