from typing import Dict
import networkx as nx
from pycadre import cadre_person
import pycadre.load_params as load_params
from repast4py import logging, schedule, network
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
    n_exits: int=0

class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents, etc), 
    and the overall iterating behavior of the model.

    Args:
        comm: the mpi communicator over which the model is distributed.
        params: the simulation input parameters

    """   
    
    def __init__(self, comm: MPI.Intracomm, params: Dict):
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_repeating_event(1, 10, self.log_agents)
        self.runner.schedule_repeating_event(1, 10, self.print_progress)
        self.runner.schedule_stop(params['STOP_AT'])
        self.runner.schedule_end_event(self.log_network)
        self.runner.schedule_end_event(self.at_end)

        # create the context to hold the agents and manage cross process
        # synchronization
        self.context = ctx.SharedContext(comm)
        self.comm = comm
        rank = comm.Get_rank()
        #self.rank = self.comm.Get_rank()

        self.my_persons = [] 
        self.graph = []
        n_agents = load_params.params_list['N_AGENTS']
        
        # initialize agents and attributes
        for i in range(n_agents):
            person = cadre_person.Person(name=i, rank=rank)  
            self.my_persons.append(person)
            self.context.add(person)

        # initialize network and add projection to context
        #self.graph = nx.erdos_renyi_graph(n_agents, 0.001)
        network_init = nx.erdos_renyi_graph(n_agents, 0.001)
        self.network = network.UndirectedSharedNetwork(network_init, comm)
        self.context.add_projection(self.network)

        #print("Network type", type(self.network))
   

        # initialize the agent logging
        tabular_logging_cols = ['tick', 'agent_id', 'agent_age', 'agent_race', 'agent_female', 'agent_alc_use_status', 
                        'agent_smoking_status', 'agent_last_incarceration_tick', 'agent_last_release_tick', 
                        'agent_current_incarceration_status']
        self.agent_logger = logging.TabularLogger(comm, load_params.params_list['agent_log_file'], tabular_logging_cols)

        agent_count = len(self.my_persons)
        n_incarcerated = []
        current_smokers = []
        AUD = []
        abstainers = []
        
        # initialize the network logging
        network_tabular_logging_cols = ['tick', 'p1', 'p2']
        self.network_logger = logging.TabularLogger(comm, load_params.params_list['network_log_file'], network_tabular_logging_cols)

        # initialize the counts logging
        self.counts = CountsLog(agent_count, len(n_incarcerated), len(current_smokers), len(AUD), len(abstainers))
        loggers = logging.create_loggers(self.counts, op=MPI.SUM, names={'pop_size':'pop_size', 'n_incarcerated':'n_incarcerated', 'n_current_smokers':'n_current_smokers', 
                                        'n_AUD':'n_AUD', 'n_alcohol_abstainers':'n_alcohol_abstainers', 
                                        'n_exits':'n_exits'},
                                        rank=rank)
        self.data_set = logging.ReducingDataSet(loggers, MPI.COMM_WORLD, 
                        load_params.params_list['counts_log_file'])

    def log_agents(self):
        tick = self.runner.schedule.tick   
        for person in self.context.agents():
            self.agent_logger.log_row(tick, person.name, round(person.age), person.race, person.female, person.alc_use_status, 
                                        person.smoker, person.last_incarceration_tick, person.last_release_tick, 
                                        person.current_incarceration_status)
        self.agent_logger.write()

    def log_network(self):
        tick = self.runner.schedule.tick   
        # for line in nx.generate_edgelist(self.network):
        #          self.network_logger.log_row(tick, line)
        # self.network_logger.write()
        pass

    def at_end(self):
        self.data_set.close()

    def print_progress(self):
        tick = self.runner.schedule.tick   
        print("---------- Completing tick", tick, "----------")

    def step(self):
        tick = self.runner.schedule.tick   

        incaceration_states = []
        smokers = []
        alc_use_status = []
        
        self.data_set.log(tick)

        for person in self.context.agents():
            person.aging() 
            
            person.transition_alc_use()
            person.simulate_incarceration(tick=tick, probability_daily_incarceration=load_params.params_list['PROBABILITY_DAILY_INCARCERATION'])
            if(person.current_incarceration_status == 1):
                person.incarceration_duration += 1
            person.simulate_recidivism(tick=tick, probability_daily_recidivism_females=load_params.params_list['PROBABILITY_DAILY_RECIDIVISM']['FEMALES'], probability_daily_recidivism_males=load_params.params_list['PROBABILITY_DAILY_RECIDIVISM']['MALES'])

            incaceration_states.append(person.current_incarceration_status)
            smokers.append(person.smoker)
            alc_use_status.append(person.alc_use_status)

        n = list(self.context.size().values())[0]
        current_smokers = [i for i, x in enumerate(smokers) if x == "Current"]
        AUD_persons = [i for i, x in enumerate(alc_use_status) if x == 3]
        alc_abstainers = [i for i, x in enumerate(alc_use_status) if x == 0]

        exits = []
    
        for p in self.context.agents():
            exit = p.exit_of_age()
            if exit:
                exits.append(exit)

        print("Number of exits is", len(exits))

        for p in exits: 
            self.remove_agent(p)

        self.counts.pop_size = list(self.context.size().values())[0]
        self.counts.n_incarcerated = sum(incaceration_states)
        self.counts.n_current_smokers = len(current_smokers)
        self.counts.n_AUD = len(AUD_persons)
        self.counts.n_alcohol_abstainers = len(alc_abstainers)
        self.counts.n_exits = len(exits)
  
    def remove_agent(self, agent):
        self.context.remove(agent)

    def start(self):
        self.runner.execute()
                


            

        



             



                        
    
                   



                    
         