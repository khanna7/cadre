from typing import Dict
import pycadre.load_params as load_params
from pycadre.cadre_network import ErdosReyniNetwork
from pycadre.person_creator import init_person_creator
from repast4py import logging, schedule
from mpi4py import MPI
from dataclasses import dataclass


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

        self.person_creator = init_person_creator()

        # initialize network and add projection to context
        self.network = ErdosReyniNetwork(self.comm, load_params.params_list["EDGE_PROB"])

        self.network.init_network(
            load_params.params_list["N_AGENTS"],
        )

        self.rank = comm.Get_rank()

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

        for person in self.network.get_agents():
            person.aging()

            person.transition_alc_use()
            person.transition_smoking_status()
            person.simulate_incarceration(
                tick=tick,
                probability_daily_incarceration=load_params.params_list[
                    "PROBABILITY_DAILY_INCARCERATION"
                ],
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

    def start(self):
        self.runner.execute()
