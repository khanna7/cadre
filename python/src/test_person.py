import unittest
import numpy as np
import cadre_person
import cadre_model 

class TestSum(unittest.TestCase):

    person = cadre_person.Person()

    def test_sum(self):
         self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
         self.assertTrue(sum([1, 2, 3]) == 6, "Should be 6")

    # def test_age_assignment(self):
    #     ages = []
    #     min_age = 40
    #     max_age = 34

    #     model = cadre_model.Model(n=10, verbose=True)
    #     model.run(MAXTIME=0)
    #     mean_age_target = (18+64)/2

            
    #     for person in model.my_persons:
    #             ages.append(person.age)
        
    #     print(ages)
    #     assert(all(ages) > min_age, "all ages are not above " + str(min_age))
    #     #assert(person.age <= max_age, "all ages are not above " + str(min_age))
        
       

        


if __name__ == '__main__':  
    unittest.main()
