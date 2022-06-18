import unittest
import numpy as np
import cadre_person
import cadre_model 

class TestSum(unittest.TestCase):

    def test_age_assignment(self):
        ages = []
        min_age = 18
        max_age = 65

        model = cadre_model.Model(n=100, verbose=True)
        model.run(MAXTIME=0)
        mean_age_target = (18+64)/2

            
        for person in model.my_persons:
                ages.append(person.age)
        
        print("Ages are: " + str(ages))
        self.assertTrue(all(ages) > min_age, "all ages are not above " + str(min_age))
        self.assertTrue(all(ages) <= max_age, "all ages are not below " + str(max_age))

if __name__ == '__main__':  
    unittest.main()
