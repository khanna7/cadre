## From the `python` directory, execute:  

### To Run Model as a Single Process

``` python -m pycadre myparams/model_params.yaml```
- The parameters file is specified since we are using repast to parse the yaml 
- Since there is a `__main__.py` file in `pycadre`, this command works. 
- If the file in `pycadre` is called `main.py`, then `python -m pycadre.main` has to be run instead

### To Run Model on Multiple Processes

```
 mpirun -n 4 python3 -m pycadre myparams/model_params.yaml
```

### To Test Model

```python -m unittest mytests.test_person.TestPerson.test_simulate_incarceration```

to test `test_simulate_incarceration` method in `TestPerson` class in `test_person` module in `mytests`.


