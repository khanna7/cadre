# CADRE - Code Repository

Welcome to the CADRE code repository, maintained by researchers at The Brown University School of Public Health! 

## Badges
[![ci](https://github.com/khanna-lab/cadre/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/khanna-lab/cadre/actions/workflows/python-app.yml)

[![codecov](https://codecov.io/gh/khanna-lab/cadre/branch/master/graph/badge.svg?token=FI7VUOTLCH)](https://codecov.io/gh/khanna-lab/cadre)



## About CADRE

This codebase was developed for NIH-funded projects that aim to model the social networks of persons involved with the criminal legal system (PCLS).
* The [first](https://reporter.nih.gov/search/DKQSaMna9U2-D1GPVdwZoA/project-details/10488980) of these focuses, funded by NIGMS, is modeling tobacco smoking and alcohol use in the networks of PCLS. 
* A [second](https://reporter.nih.gov/search/p94t_kwSokGrAaxrbNLTig/project-details/10879972) project, supported by NIMHD, is building upon this codebase to simulate the impact of social network dynamics on COVID-19 testing and vaccination among PCLS. 

## Contributors

### Current

#### Tobacco Smoking & Alcohol Use:
* [Aditya Khanna](https://github.com/khanna7)
* [Daniel Sheeler](https://github.com/dsheeler)

#### COVID-19 Testing and Vaccination:
* [Aditya Khanna](https://github.com/khanna7)
* [Nick Collier](https://github.com/ncollier)
* [Jonathan Ozik](https://github.com/jozik)

### Past
* [Noah Rousell](https://github.com/nwrousell)
* [Yurui Zhang](https://github.com/yuruizhang9734)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Contact

- [Aditya Khanna](https://github.com/khanna7) for code reviews and feedback.


## Running the Model

- Instructions for running a [single instance](https://github.com/khanna-lab/cadre/blob/master/python/docs/single-instance-model-installation-running-testing.md)

- Instructions for running [multiple instances](https://github.com/khanna-lab/cadre/blob/master/python/docs/EMEWS-working-instructions.md) through EMEWS

## Reproducing Plots

Set working directory as 
```cadre/data-analysis-plotting/Simulated-Data-Analysis/r```.
There is an Rproj at this location that can run the various agent, incarceration, and network logs to produce outputs.

Plots for the paper are in the `multiple-runs` subdirectories under `agent-log-analysis`, `incarceration-log-analysis` and `network-log-analysis`.

## Acknowledgments

We would like to thank the following entities:
* NIGMS (P20 GM 130414)
* NIMHD (R21 MD 019388)
* [Center for Addiction and Disease Risk Exacerbation (CADRE)](https://www.brown.edu/academics/public-health/cadre/home) at Brown University
* [Center for Alcohol and Addiction Studies (CAAS)](https://www.brown.edu/public-health/caas/home) at Brown University
* THe [EMEWS](https://web.cels.anl.gov/projects/emews/tutorial/) project
* The [Repast4Py](https://repast.github.io/repast4py.site/index.html) project
* The [nextworkx](https://networkx.org/) project

