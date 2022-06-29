## Check unit test coverage

From the `python` directory, exeucte:  

```
coverage run -m unittest mytests.test_person.TestPerson
coverage report
``` 

or, per Daniel, :

```
coverage run -m unittest discover mytests
coverage report
```

Either way, there is an issue. See [Issue #24](https://github.com/khanna7/cadre/issues/24#issue-1283832743)

More on [Coverage](https://docs.google.com/document/d/1XSAST_h8jHBffyLSX693eRaQwUsm8u1DN7I87UseLV0/edit#bookmark=id.vnnc6g6mpdfv)  

For Continuous Integration, following the example of P2M4Py as CircleCI. 
Also explore GitHub Actions. 