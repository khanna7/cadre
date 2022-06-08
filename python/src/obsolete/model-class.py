class Model:
    RACE_DISTRIBUTION = [
        71.4/100, #white alone
        8.5/100, #black alone
        16.3/100, #hispanic alone
        3.8/100 #asian alone (increased by 0.1 to sum to 1)
        # REF: https://censusreporter.org/profiles/04000US44-rhode-island/
    ]

    RACE_CATS = ["white", "black", "hispanic", "other"]
    
    SMOKING_PREV = 0.13 #REF: https://www.cdc.gov/tobacco/data_statistics/fact_sheets/adult_data/cig_smoking/index.htm
    
    FEMALE_PROP = 51.3/100 # REF: https://www.census.gov/quickfacts/RI
    
    ALC_USE_PROPS = [8.3/100, 72.9/100, 13.2/100, 5.6/100] #see derivation in file:///Volumes/GoogleDrive/My%20Drive/code/cadre/r/explain-population-initialization.nb.html


    def __init__(self, n):
        self.my_persons = [] 
        
        age_sum = 0
        race = []
        females = 0
        alc_use_status = [] 
        smokers = 0
        
        
        # initialize agents and attributes
        for i in range(n):
            person = Person(age=random.randint(18, 65), 
                            race=random.choice(RACE_CATS, p=RACE_DISTRIBUTION),
                            female=random.binomial(1, FEMALE_PROP),
                            alc_use_status=random.choice(range(0, 4), p=ALC_USE_PROPS),
                            smoker=random.binomial(1, SMOKING_PREV)
                            ) 

            self.my_persons.append(person)
            age_sum = person.age + age_sum
            race.append(person.race) 
            females = person.female + females 
            alc_use_status.append(person.alc_use_status)
            smokers = person.smoker + smokers

            if verbose == TRUE:
                print(person.name)
                print(person.age)
                print(person.alc_use_status, "\n")

        if verbose == TRUE:
            race_dist = pd.value_counts(np.array(race))/len(race)*100
            alc_use_status_dist = pd.value_counts(np.array(alc_use_status))/len(alc_use_status)*100

            print("Number of agents is: " + 
                str(len(my_persons)))
            print("Mean agent age is: " + 
                str(('{:.2f}'.format(age_sum/len(my_persons)))))
            print("Distribution of race categories is ", "\n" + 
                str(race_dist.round(decimals=2)), "%")
            print("Number of females is: " + 
                str(females))
            print("Distribution of alcohol use categories is ", "\n" + 
                str(alc_use_status_dist.round(decimals=2)), "%")
            print("Max level of alcohol use is " + 
                str(max(alc_use_status)))
            print("Min level of alcohol use is " + 
                str(min(alc_use_status)))
            print("Median level of alcohol use is " + 
                str(np.median(alc_use_status)))
            print("Number of smokers is " + 
                str(smokers))