from os.path import join
from mpi4py import MPI

from repast4py import logging, parameters, util
from dataclasses import dataclass
from typing import Iterable, List

class NullTabularLogger:

    def __init__(self):
        raise(ValueError)
        
    def log_row(self, *args):
        pass

    def close(self):
        pass

    def write(self):
        pass


@dataclass
class CountsLog:
    pop_size: int = 0
    n_incarcerated: int = 0
    n_current_smokers: int = 0
    n_AUD: int = 0
    n_alcohol_abstainers: int = 0
    n_exits: int = 0
    n_entries: int = 0


counts = None
data_set = None
agent_logger = None
network_logger = None
incarceration_logger = None


def create_logger(output_dir, comm, key: str, header: List[str]):
    if key in parameters.params:
        return logging.TabularLogger(comm, join(output_dir, parameters.params[key]), header)
    else:
        return NullTabularLogger()


def init_logging(num_agents, comm, rank, output_dir):
    global counts, data_set, agent_logger, network_logger, incarceration_logger

    agent_logger = create_logger(output_dir, comm, "agent_log_file",[
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
    ])
    network_logger = create_logger(output_dir, comm, "network_log_file", ["tick", "p1", "p2"])
    incarceration_logger = create_logger(output_dir, comm, "incarceration_log_file", 
        ["tick", "id", "age", "race", "female", "alc_use_status", "smoking_status"])

    # initialize the counts logging
    counts = CountsLog(
        num_agents,
        0,
        0,
        0,
        0,
    )

    loggers = logging.create_loggers(
        counts,
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
        rank=rank,
    )
    data_set = logging.ReducingDataSet(
        loggers, MPI.COMM_WORLD, parameters.params["counts_log_file"]
    )
    


def close_loggers():
    agent_logger.close()
    network_logger.close()
    incarceration_logger.close()


def write_loggers():
    agent_logger.write()
    network_logger.write()
    incarceration_logger.write()


def log_agent(person, tick):
    agent_logger.log_row(
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

def log_incarceration(person, tick, event_type):
    incarceration_logger.log_row(
        tick,
        person.name,
        round(person.age),
        person.race,
        person.female,
        person.alc_use_status,
        person.smoker,
        event_type
    )
    incarceration_logger.write()

""" 
def log_persons(tick, context, type):
    for p in context.agents():
        log_person(tick, p, type)
    person_logger.write()


def log_person(tick, person, type):
    person_logger.log_row(tick, type, person.id, race, identity, person.age,
                          person.infected, person.viral_load, person.cd4_count)


def log_diagnosis(tick, person_id, category):
    diagnosis_logger.log_row(tick, person_id)
    epi_data_logger.log_diagnosis(category)


def log_biomarkers(tick, person):
    biomarker_logger.log_row(tick, person.id, person.cd4_count,
                             person.viral_load, int(person.is_on_art()))
 """