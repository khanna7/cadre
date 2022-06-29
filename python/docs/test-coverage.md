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

Either way, there is an issue. See [Issue #24](https://github.com/khanna7/cadre/issues/24#issue-1283832743)

More on [Coverage](https://coverage.readthedocs.io/en/6.4.1/)  

For Continuous Integration, following the example of P2M4Py as CircleCI. 
Also explore GitHub Actions. 