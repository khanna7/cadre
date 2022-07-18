from numpy import random
import numpy as np
import pandas as pd
import networkx as nx
from pycadre import cadre_person
import pycadre.load_params as load_params
from repast4py import logging
import csv

class Model:
    def __init__(self, n, comm, verbose=True):
        self.comm=comm
        self.my_persons = [] 
        self.graph = []
        tabular_logging_cols = ['tick', 'agent_id', 'agent_age', 'agent_race', 'agent_female', 'agent_alc_use_status', 
                                'agent_smoking_status', 'agent_last_incarceration_time', 'agent_last_release_time', 
                                'agent_current_incarceration_status']
        
        # initialize agents and attributes
        for i in range(n):
            person = cadre_person.Person(name = i)    
            self.my_persons.append(person)
    
        self.graph = nx.erdos_renyi_graph(len(self.my_persons), 0.001)
        self.agent_logger = logging.TabularLogger(comm, load_params.params_list['agent_log_file'], tabular_logging_cols)


    def log_agents(self, time):
        
        for person in self.my_persons:
            self.agent_logger.log_row(time, person.name, round(person.age), person.race, person.female, person.alc_use_status, 
                                        person.smoker, person.last_incarceration_time, person.last_release_time, 
                                        person.current_incarceration_status)

    def run(self, MAXTIME=10, verbose=True, params=None):

        with open('counts_data.csv', 'w', newline='') as cd_file:
            
            for time in range(MAXTIME):
                self.log_agents(time)
                self.agent_logger.write()
                incaceration_states = []
                smokers = []
                alc_use_status = []

                for person in self.my_persons:
                    person.step(time) 
                    incaceration_states.append(person.current_incarceration_status)
                    smokers.append(person.smoker)
                    alc_use_status.append(person.alc_use_status)

                    if verbose == True:
                            print("Person name: " + str(person.name))
                            print("Person age: ", round(person.age))
                            print("Person race: " + str(person.race))
                            print("Person Female: " + str(person.female))
                            print("Person alcohol use status: " + str(person.alc_use_status))
                            print("Person smoking status: " + str(person.smoker))
                            print("Person last incarceration time: " + str(person.last_incarceration_time))
                            print("Person last release time: " + str(person.last_release_time))
                            print("Person incarceration duration: ", (person.last_release_time - person.last_incarceration_time), "\n")

                    
                n = len(self.my_persons)
                current_smokers = [i for i, x in enumerate(smokers) if x == "Current"]
                AUD_persons = [i for i, x in enumerate(alc_use_status) if x == 3]
                alc_abstainers = [i for i, x in enumerate(alc_use_status) if x == 0]

                writer = csv.writer(cd_file)
                writer.writerow([time, n, sum(incaceration_states), len(current_smokers), len(alc_abstainers), len(AUD_persons)])

                print("Number of agents is: ", len(self.my_persons))
                print("Network size is", len(list(self.graph.nodes())), "nodes")
                print("Network edgecound is", len(list(self.graph.edges())), "edges")

                for line in nx.generate_edgelist(self.graph):
                    print(line)



                        
    
                   



                    
         