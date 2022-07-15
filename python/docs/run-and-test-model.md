## From the `python` directory, execute:  

### To Run Model

``` python -m pycadre myparams/model_params.yaml```
- The parameters file is specified since we are using repast to parse the yaml 
- Since there is a `__main__.py` file in `pycadre`, this command works. 
- If the file in `pycadre` is called `main.py`, then `python -m pycadre.main` has to be run instead


### To Test Model

```python -m unittest mytests.test_person.TestPerson.test_simulate_incarceration```

to test `test_simulate_incarceration` method in `TestPerson` class in `test_person` module in `mytests`.


