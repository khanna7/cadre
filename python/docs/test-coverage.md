## Check unit test coverage

From the `python` directory, exeucte:  

```
coverage run -m unittest mytests.test_person.TestPerson
coverage report
``` 

or, per Daniel:

```
coverage run -m unittest discover mytests
coverage report
```

(Use 
```coverage run -m --source=pycadre/ unittest discover mytests```
to avoid unnecessary report on top matter on personal Macbook.
)

More on [Coverage](https://coverage.readthedocs.io/en/6.4.1/)  

For Continuous Integration, following the example of P2M4Py as CircleCI. 
Also explore GitHub Actions. 