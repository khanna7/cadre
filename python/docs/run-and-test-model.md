
# Locally (on Mac OS X)

From the `python` directory, execute:  

### To Run Model as a Single Process

``` python -m pycadre myparams/model_params.yaml```
- The parameters file is specified since we are using repast to parse the yaml 
- Since there is a `__main__.py` file in `pycadre`, this command works. 
- If the file in `pycadre` is called `main.py`, then `python -m pycadre.main` has to be run instead

### To Run Model on Multiple Processes

```
 mpirun -n 4 python3 -m pycadre myparams/model_params.yaml
```

### Specify parameters through command line 
```
python -m pycadre myparams/model_params.yaml '{"STOP_AT": 12, "N_AGENTS": 13}'
```

### Testing: Specific Method
```python -m unittest mytests.test_person.TestPerson.test_simulate_incarceration```

to test `test_simulate_incarceration` method in `TestPerson` class in `test_person` module in `mytests`


### Test Coverage
```
coverage run -m unittest discover mytests
coverage report
```

(Use `coverage run -m --source=pycadre/ unittest discover mytests` to avoid unnecessary report on top matter on personal Macbook. )

More on [Coverage](https://coverage.readthedocs.io/en/6.4.1/)


# On OSCAR 

- Without `swift-t`:

 From `/gpfs/home/akhann16/code/cadre/python`, do 
 `ls -ltr *.sh`

 Then:
 ```
 sbatch jobscript.sh 
 ```
 
- With `swift-t`:

 ```
 sbatch submit_using_swift.sh
 ```


