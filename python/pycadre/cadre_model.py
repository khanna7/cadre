from typing import Dict
import networkx as nx
from pycadre import cadre_person
import pycadre.load_params as load_params
from repast4py import logging, schedule
from repast4py import context as ctx
from mpi4py import MPI
import csv
from dataclasses import dataclass


@dataclass
class CountsLog:
    pop_size: int = 0
    n_incarcerated: int = 0
    n_current_smokers: int = 0
    n_AUD: int = 0
    n_alcohol_abstainers: int = 0

class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents, etc), 
    and the overall iterating behavior of the model.

    Args:
        comm: the mpi communicator over which the model is distributed.
        params: the simulation input parameters

    """   
    
    def __init__(self, comm: MPI.Intracomm, params: Dict, verbose=True):
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_repeating_event(1.1, 10, self.log_agents)
        self.runner.schedule_stop(params['STOP_AT'])
        self.runner.schedule_end_event(self.at_end)

        # create the context to hold the agents and manage cross process
        # synchronization
        self.context = ctx.SharedContext(comm)

        self.comm = comm
        self.my_persons = [] 
        self.graph = []
        tabular_logging_cols = ['tick', 'agent_id', 'agent_age', 'agent_race', 'agent_female', 'agent_alc_use_status', 
                                'agent_smoking_status', 'agent_last_incarceration_tick', 'agent_last_release_tick', 
                                'agent_current_incarceration_status']
        rank = comm.Get_rank()

        # initialize agents and attributes
        for i in range(load_params.params_list['N_AGENTS']):
            person = cadre_person.Person(name=i, rank=rank)  
            self.my_persons.append(person)
    
        self.graph = nx.erdos_renyi_graph(len(self.my_persons), 0.001)

        # initialize the logging
        self.agent_logger = logging.TabularLogger(comm, load_params.params_list['agent_log_file'], tabular_logging_cols)

        agent_count = len(self.my_persons)
        n_incarcerated = []
        current_smokers = []
        AUD = []
        abstainers = []

        self.counts = CountsLog(agent_count, len(n_incarcerated), len(current_smokers), len(AUD), len(abstainers))
        loggers = logging.create_loggers(self.counts, op=MPI.SUM, names={'pop_size':'pop_size', 'n_incarcerated':'n_incarcerated', 'n_current_smokers':'n_current_smokers', 'n_AUD':'n_AUD', 'n_alcohol_abstainers':'n_alcohol_abstainers'}, rank=rank)
        self.data_set = logging.ReducingDataSet(loggers, MPI.COMM_WORLD, 
                        load_params.params_list['counts_log_file'])
        #self.data_set.log(0)

    def log_agents(self):
        for person in self.my_persons:
            self.agent_logger.log_row(person.name, round(person.age), person.race, person.female, person.alc_use_status, 
                                        person.smoker, person.last_incarceration_tick, person.last_release_tick, 
                                        person.current_incarceration_status)
        self.agent_logger.write()

    def at_end(self):
        self.data_set.close()

    def step(self, verbose=True):
        tick = self.runner.schedule.tick   

        incaceration_states = []
        smokers = []
        alc_use_status = []
        self.log_agents()
        self.agent_logger.write()
        
        self.data_set.log(tick)

        for person in self.my_persons:
            person.aging() 
            person.transition_alc_use()
            person.simulate_incarceration(tick=tick, probability_daily_incarceration=load_params.params_list['PROBABILITY_DAILY_INCARCERATION'])
            if(person.current_incarceration_status == 1):
                person.incarceration_duration += 1
            #person.simulate_release(tick=tick)
            person.simulate_recidivism(tick=tick, probability_daily_recidivism_females=load_params.params_list['PROBABILITY_DAILY_RECIDIVISM']['FEMALES'], probability_daily_recidivism_males=load_params.params_list['PROBABILITY_DAILY_RECIDIVISM']['MALES'])

            incaceration_states.append(person.current_incarceration_status)
            smokers.append(person.smoker)
            alc_use_status.append(person.alc_use_status)

            if verbose == True:
                    print("Person ID: " + str(person.name))
                    print("Person age: ", round(person.age))
                    print("Person race: " + str(person.race))
                    print("Person Female: " + str(person.female))
                    print("Person alcohol use status: " + str(person.alc_use_status))
                    print("Person smoking status: " + str(person.smoker))
                    print("Person last incarceration tick: " + str(person.last_incarceration_tick))
                    print("Person last release tick: " + str(person.last_release_tick))
                    print("Person incarceration duration: ", (person.last_release_tick - person.last_incarceration_tick), "\n")

        n = len(self.my_persons)
        current_smokers = [i for i, x in enumerate(smokers) if x == "Current"]
        AUD_persons = [i for i, x in enumerate(alc_use_status) if x == 3]
        alc_abstainers = [i for i, x in enumerate(alc_use_status) if x == 0]

        self.counts.pop_size = len(self.my_persons)
        self.counts.n_incarcerated = sum(incaceration_states)
        self.counts.n_current_smokers = len(current_smokers)
        self.counts.n_AUD = len(AUD_persons)
        self.counts.n_alcohol_abstainers = len(alc_abstainers)
        
        if verbose == True:
            print("Number of agents is: ", len(self.my_persons))
            print("Network size is", len(list(self.graph.nodes())), "nodes")
            print("Network edgecount is", len(list(self.graph.edges())), "edges")

    def start(self, verbose=True):
        self.runner.execute()
                

    def run(self, params: Dict):
        global model
        model = Model(MPI.COMM_WORLD, params)
        model.start()
        for line in nx.generate_edgelist(self.graph):
            #print(line)
            pass


            

        



             



                        
    
                   



                    
         