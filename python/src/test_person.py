import unittest
import numpy as np
import cadre_person
import cadre_model 

class TestPerson(unittest.TestCase):

    def test_age_assignment(self):
        ages = []
        min_age = 18
        max_age = 64
        mean_age_target = (min_age+max_age)/2

        model = cadre_model.Model(n=10000, verbose=False)
        model.run(MAXTIME=0)
                   
        for person in model.my_persons:
                ages.append(person.age)

        for age in ages: 
            self.assertTrue(age >= min_age)
            self.assertTrue(age <= max_age)
            self.assertEqual(round(np.mean(ages)), mean_age_target)
        
if __name__ == '__main__':  
    unittest.main()
