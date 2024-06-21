# Installation

```
module load python/3.11.0s-ixrhc3q
module load openmpi/4.1.2-s5wtoqb
module load r/4.3.1-lmofgb4

MPI_LIB="/oscar/rt/9.2/software/0.20-generic/0.20.1/opt/spack/linux-rhel9-x86_64_v3/gcc-11.3.1/openmpi-4.1.2-s5wtoqbqirz4ivubo6uzp2ndglheablu/lib"
export LD_LIBRARY_PATH=$MPI_LIB:$LD_LIBRARY_PATH
```

Then, install `repast4py`

from PyPI:

```
env CC=mpicxx pip install repast4py
```

or from the requirements:

```
env CC=mpicxx pip install repast4py
```

# Running (Single instance)

```
python -m pycadre myparams/model_params.yaml '{"STOP_AT": 12, "N_AGENTS": 13}' 
```

(Note `python3 ...` does not work!!!)

# Testing 

## Run all tests:

```
python -m unittest discover -s mytests/ -p "test_*.py"
```

## Specific methods

```
python -m unittest mytests.test_person.TestPerson.test_simulate_incarceration
```

to test `test_simulate_incarceration` method in `TestPerson` class in `test_person` module in `mytests``



