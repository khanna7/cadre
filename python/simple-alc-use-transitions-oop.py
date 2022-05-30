from numpy import random

class Person():
    def __init__(self, age=None, alc_use_status=None):
        if age == None:
            age = random.randint(18, 65)
        if alc_use_status == None:
            alc_use_status = random.randint(0, 3)
        self.age = age
        self.alc_use_status = alc_use_status

def main():
    p1=Person()
    p2=Person()

    print(p1.age, p1.alc_use_status)
    print(p2.age, p2.alc_use_status)

if __name__ == "__main__":
    main()
        