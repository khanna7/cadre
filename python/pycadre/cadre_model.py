from typing import Dict
import yaml
from repast4py.util import find_free_filename

import pycadre.load_params as load_params
from pycadre.cadre_network import ErdosReyniNetwork
from pycadre.person_creator import init_person_creator
from repast4py import logging, schedule
from mpi4py import MPI
from dataclasses import dataclass
import os, re
from datetime import datetime

@dataclass
class CountsLog:
    pop_size: int = 0
    n_incarcerated: int = 0
    n_current_smokers: int = 0
    n_AUD: int = 0
    n_alcohol_abstainers: int = 0
    n_exits: int = 0
    n_entries: int = 0


class Model:
    """
    The Model class encapsulates the simulation, and is
    responsible for initialization (scheduling events, creating agents, etc),
    and the overall iterating behavior of the model.

    Args:
        comm: the mpi communicator over which the model is distributed.
        params: the simulation input parameters

    """
    output_directory = None #class-level attribute for storing outputs

    def __init__(self, comm: MPI.Intracomm, params: Dict):
        # create the schedule
        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_repeating_event(1, 10, self.log_agents)
        self.runner.schedule_repeating_event(1, 10, self.print_progress)
        self.runner.schedule_stop(params["STOP_AT"])
        # self.runner.schedule_end_event(self.log_network)
        self.runner.schedule_repeating_event(1, 10, self.log_network)
        self.runner.schedule_end_event(self.log_agents)
        self.runner.schedule_end_event(self.at_end)

        self.dump_parameters()

        self.person_creator = init_person_creator()

        # initialize network and add projection to context
        self.network = ErdosReyniNetwork(comm, load_params.params_list["N_AGENTS"],
                                         load_params.params_list["TARGET_MEAN_DEGREE"])

        self.network.init_network(
            load_params.params_list["N_AGENTS"],
        )

        self.rank = comm.Get_rank()
        
        # Set the base output directory
        self.output_directory = self.get_output_directory()
        self.update_output_paths()

        # initialize the agent logging
        tabular_logging_cols = [
            "tick",
            "id",
            "age",
            "race",
            "female",
            "alc_use_status",
            "smoking_status",
            "last_incarceration_tick",
            "last_release_tick",
            "current_incarceration_status",
            "entry_at_tick",
            "exit_at_tick",
            "n_incarcerations",
            "n_releases",
            "n_smkg_stat_trans",
            "n_alc_use_stat_trans",
        ]
        self.agent_logger = logging.TabularLogger(
            comm, load_params.params_list["agent_log_file"], tabular_logging_cols
        )

        agent_count = self.network.get_num_agents()
        n_incarcerated = []
        current_smokers = []
        AUD = []
        abstainers = []

        # initialize the network logging
        network_tabular_logging_cols = ["tick", "p1", "p2"]
        self.network_logger = logging.TabularLogger(
            comm,
            load_params.params_list["network_log_file"],
            network_tabular_logging_cols,
        )

        # initialize the counts logging

        self.counts = CountsLog(
            agent_count,
            len(n_incarcerated),
            len(current_smokers),
            len(AUD),
            len(abstainers),
        )
        loggers = logging.create_loggers(
            self.counts,
            op=MPI.SUM,
            names={
                "pop_size": "pop_size",
                "n_incarcerated": "n_incarcerated",
                "n_current_smokers": "n_current_smokers",
                "n_AUD": "n_AUD",
                "n_alcohol_abstainers": "n_alcohol_abstainers",
                "n_exits": "n_exits",
                "n_entries": "n_entries",
            },
            rank=self.rank,
        )
        self.data_set = logging.ReducingDataSet(
            loggers, MPI.COMM_WORLD, load_params.params_list["counts_log_file"]
        )

    def log_agent(self, person, tick):
        self.agent_logger.log_row(
            tick,
            person.name,
            round(person.age),
            person.race,
            person.female,
            person.alc_use_status,
            person.smoker,
            person.last_incarceration_tick,
            person.last_release_tick,
            person.current_incarceration_status,
            person.entry_at_tick,
            person.exit_at_tick,
            person.n_incarcerations,
            person.n_releases,
            person.n_smkg_stat_trans,
            person.n_alc_use_stat_trans
        )

    def log_agents(self):
        tick = self.runner.schedule.tick
        for person in self.network.get_agents():
            self.log_agent(person, tick)
        self.agent_logger.write()
    

    def get_instance_number(self):
        """
        Extracts the instance number from the current working directory path.

        Returns:
        - int: Extracted instance number or raises an error if the pattern isn't found.
        """
        cwd = os.getcwd()
        match = re.search(r'instance_(\d+)', cwd)
        if not match:
            raise ValueError(f"Cannot extract instance number from current working directory: {cwd}")
        return int(match.group(1))

    def log_network(self):
        tick = self.runner.schedule.tick

        for edge in self.network.get_edges():
            agent1 = edge[0]
            agent2 = edge[1]
            self.network_logger.log_row(tick, agent1.id, agent2.id)
        self.network_logger.write()

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

        all_agents = self.network.get_agents()
        white_male_count = sum([1 for agent in all_agents if agent.race == "White" and agent.female == 0])
        black_male_count = sum([1 for agent in all_agents if agent.race == "Black" and agent.female == 0])
        hispanic_male_count = sum([1 for agent in all_agents if agent.race == "Hispanic" and agent.female == 0])
        asian_male_count = sum([1 for agent in all_agents if agent.race == "Asian" and agent.female == 0])

        white_female_count = sum([1 for agent in all_agents if agent.race == "White" and agent.female == 1])
        black_female_count = sum([1 for agent in all_agents if agent.race == "Black" and agent.female == 1])
        hispanic_female_count = sum([1 for agent in all_agents if agent.race == "Hispanic" and agent.female == 1])
        asian_female_count = sum([1 for agent in all_agents if agent.race == "Asian" and agent.female == 1])


        print("White male count:", white_male_count)
        print("Black male count:", black_male_count)
        print("Hispanic male count:", hispanic_male_count)
        print("Asian male count:", asian_male_count)

        print("White female count:", white_female_count)
        print("Black female count:", black_female_count)
        print("Hispanic female count:", hispanic_female_count)
        print("Asian female count:", asian_female_count)


        for person in self.network.get_agents():
            person.aging()

            person.transition_alc_use()
            person.transition_smoking_status(tick)
            person.simulate_incarceration(
                tick=tick,
                probability_daily_incarceration=load_params.params_list[
                    "PROBABILITY_DAILY_INCARCERATION"
                ]
            )
            if person.current_incarceration_status == 1:
                person.incarceration_duration += 1
            person.simulate_recidivism(
                tick=tick,
                probability_daily_recidivism_females=load_params.params_list[
                    "PROBABILITY_DAILY_RECIDIVISM"
                ]["FEMALES"],
                probability_daily_recidivism_males=load_params.params_list[
                    "PROBABILITY_DAILY_RECIDIVISM"
                ]["MALES"],
                probability_daily_incarceration=load_params.params_list[
                    "PROBABILITY_DAILY_INCARCERATION"
                ],
            )

            incaceration_states.append(person.current_incarceration_status)
            smokers.append(person.smoker)
            alc_use_status.append(person.alc_use_status)

        current_smokers = [i for i, x in enumerate(smokers) if x == "Current"]
        AUD_persons = [i for i, x in enumerate(alc_use_status) if x == 3]
        alc_abstainers = [i for i, x in enumerate(alc_use_status) if x == 0]

        self.network_step(tick)

        self.counts.pop_size = self.network.get_num_agents()
        self.counts.n_incarcerated = sum(incaceration_states)
        self.counts.n_current_smokers = len(current_smokers)
        self.counts.n_AUD = len(AUD_persons)
        self.counts.n_alcohol_abstainers = len(alc_abstainers)

    def network_step(self, tick):
        for p in self.network.get_agents():
            if p.exit_of_age(tick):
                p.exit_at_tick = tick
                self.log_agent(p, tick)
                self.network.remove_agent(p)
                new = self.person_creator.create_person(tick=tick)
                self.network.add(new)
  

    def get_output_directory(self):
        """
        Get the appropriate output directory based on if Turbine is being used.
        """
        if self.output_directory:
            return self.output_directory  # If already defined, just return it
        
        turbine_output = os.environ.get('TURBINE_OUTPUT')

        if turbine_output:
            # If running within EMEWS (Turbine)
            if 'instance_' in os.getcwd():
                instance_number = self.get_instance_number()
                self.output_directory = os.path.join(turbine_output, f"instance_{instance_number}", 'output')
            else:
                self.output_directory = os.path.join(turbine_output, 'output')
        else:
            # Running in standalone mode
            datetime_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_directory = os.path.join(os.getcwd(), f'output_{datetime_str}')
            print(f"Running in standalone mode. Using output directory: {self.output_directory}")

        return self.output_directory

  
    def dump_parameters(self):
        # Get the output directory using the method we previously defined
        output_directory = self.get_output_directory()
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Construct path for the parameters file within the output directory
        params_file = find_free_filename(os.path.join(output_directory, 'parameters.txt'))

        # Write the parameters
        with open(params_file, 'w') as p:
            p.write(yaml.dump(load_params.params_list))

    def update_output_paths(self):
        
        # Get the correct output directory
        output_directory = self.get_output_directory()

        # Update paths for the log files
        load_params.params_list['agent_log_file'] = os.path.join(output_directory, 'agent_log.csv')
        load_params.params_list['network_log_file'] = os.path.join(output_directory, 'network_log.csv')
        load_params.params_list['counts_log_file'] = os.path.join(output_directory, 'counts_log.csv')

        
        # Since load_params.params_list contains keys like 'agent_log_file', 'network_log_file', etc.
        # We update their paths to ensure they are saved in the same directory as the parameters
        load_params.params_list['agent_log_file'] = os.path.join(self.output_directory, 'agent_log.csv')
        load_params.params_list['network_log_file'] = os.path.join(self.output_directory, 'network_log.csv')
        load_params.params_list['counts_log_file'] = os.path.join(self.output_directory, 'counts_log.csv')

    def start(self):
        self.runner.execute()
