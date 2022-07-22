from numpy import random
import numpy as np
import pandas as pd
import networkx as nx
from pycadre import cadre_person
import pycadre.load_params as load_params
from repast4py import logging
from mpi4py import MPI
import csv
from dataclasses import dataclass, fields


@dataclass
class CountsLog:
    pop_size: int = 0
    n_incarcerated: int = 0
    n_current_smokers: int = 0


class Model:
    def __init__(self, n, comm, verbose=True):
        self.comm = comm
        self.my_persons = [] 
        self.graph = []
        tabular_logging_cols = ['tick', 'agent_id', 'agent_age', 'agent_race', 'agent_female', 'agent_alc_use_status', 
                                'agent_smoking_status', 'agent_last_incarceration_time', 'agent_last_release_time', 
                                'agent_current_incarceration_status']
        rank = comm.Get_rank()

        # initialize agents and attributes
        for i in range(n):
            person = cadre_person.Person(name=i)  
            self.my_persons.append(person)
    
        self.graph = nx.erdos_renyi_graph(len(self.my_persons), 0.001)

        # initialize the logging
        self.agent_logger = logging.TabularLogger(comm, load_params.params_list['agent_log_file'], tabular_logging_cols)

        agent_count = len(self.my_persons)
        n_incarcerated = []
        current_smokers = []

        self.counts = CountsLog(agent_count, len(n_incarcerated), len(current_smokers))
        loggers = logging.create_loggers(self.counts, op=MPI.SUM, rank=rank)
        self.data_set = logging.ReducingDataSet(loggers, MPI.COMM_WORLD, 
                        load_params.params_list['counts_log_file'])
        #self.data_set.log(0)

    def log_agents(self, time):
        for person in self.my_persons:
            self.agent_logger.log_row(time, person.name, round(person.age), person.race, person.female, person.alc_use_status, 
                                        person.smoker, person.last_incarceration_time, person.last_release_time, 
                                        person.current_incarceration_status)
        self.agent_logger.write()

    def run(self, MAXTIME=10, verbose=True, params=None):

        with open('counts_data.csv', 'w', newline='') as cd_file:
            
            for time in range(MAXTIME):
                
                incaceration_states = []
                smokers = []
                alc_use_status = []

                self.log_agents(time)
                self.agent_logger.write()
                self.data_set.log(tick=time)

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

                print("Current smokers:", current_smokers, "\n")
                print("Number of current smokders:", len(current_smokers), "\n")

                writer = csv.writer(cd_file)
                writer.writerow([time, n, sum(incaceration_states), len(current_smokers), len(alc_abstainers), len(AUD_persons)])

                self.counts.pop_size = len(self.my_persons)
                self.counts.n_incarcerated = sum(incaceration_states)
                self.n_current_smokers = len(current_smokers)
                
                self.data_set.close()

                print("Number of agents is: ", len(self.my_persons))
                print("Network size is", len(list(self.graph.nodes())), "nodes")
                print("Network edgecount is", len(list(self.graph.edges())), "edges")

                for line in nx.generate_edgelist(self.graph):
                    #print(line)
                    pass



                        
    
                   



                    
         