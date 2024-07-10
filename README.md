This repository includes the source code, the data and the plots for the paper entitled "Distributed Genetic Algorithm for Service Placement in Fog Computing Leveraging Infrastructure Nodes for Optimization", published in the journal "Future Generation Computer Systems":

```
Carlos Guerrero, Isaac Lera, Carlos Juiz, Distributed genetic algorithm for application placement in the compute continuum leveraging infrastructure nodes for optimization,
Future Generation Computer Systems, Volume 160, 2024, Pages 154-170, ISSN 0167-739X, https://doi.org/10.1016/j.future.2024.05.044.
```

If you would consider to cite the paper, you could use this bibtex record:

```
@article{GUERRERO2024154,
title = {Distributed genetic algorithm for application placement in the compute continuum leveraging infrastructure nodes for optimization},
journal = {Future Generation Computer Systems},
volume = {160},
pages = {154-170},
year = {2024},
issn = {0167-739X},
doi = {https://doi.org/10.1016/j.future.2024.05.044},
url = {https://www.sciencedirect.com/science/article/pii/S0167739X24002760},
author = {Carlos Guerrero and Isaac Lera and Carlos Juiz},
keywords = {Cloud–edge continuum, Fog computing, Distributed genetic algorithm, Resource optimization, Multi-objective optimization, Application placement}
}
```


Four different distributed executions are studied in the article.

It is necessary to start the mosquitto server for all the experiments executions:

```
/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf
```
The general set-up of the optimization process require to be fixed through the following files:




# Traditional centralized NSGA-II (traditionalNSGA)

Edit the executionConfig.py fila and set

```
executionConfig='traditionalNSGA'
```

Start the python file that execute the solutions that require a coordinator

```
python coordinator.py
```

If the executionConfig value is correctly fixed, the following configuration parameters are considered in this experiment scenario execution:

optimizationConfig.py
```python
numberOfSolutionsInWorkers = 200
```

experimentationConfig.py
```python
executionScenario = 'traditionalNSGA'
numOfWorkers = 1
time2SleepInCoordinator = 0.05
time2SleepInWorker = 0.0
time2Sleep2Finish = 20
```

# Decentralized NSGA-II, with centralized population in the coordinator (Semi-distributed)


Edit the executionConfig.py fila and set

```
executionConfig='semidistributed'
```

Start the python file that execute the solutions that require a coordinator


```
python coordinator.py
```


If the executionConfig value is correctly fixed, the following configuration parameters are considered in this experiment scenario execution:



optimizationConfig.py
```python
numberOfSolutionsInWorkers = 10
```

experimentationConfig.py
```python
executionScenario = 'semidistributed'
numOfWorkers = 20
time2SleepInCoordinator = 0.05
time2SleepInWorker = 0.0
time2Sleep2Finish = 20
```


# Full decentralized NSGA-II, with the population distributed in the nodes (Fully-distributed)



Edit the executionConfig.py fila and set

```
executionConfig='fullydistributed'
```

Start the python file that execute the solutions that DO NOT require a coordinator



```
python coordinatorFullMigration.py
```


If the executionConfig value is correctly fixed, the following configuration parameters are considered in this experiment scenario execution:

optimizationConfig.py
```python
numberOfSolutionsInWorkers = 10
```

experimentationConfig.py
```python
executionScenario = 'fullMigration'
onlyNeighbors = False
numOfWorkers = 20
time2SleepInCoordinator = 0.1
time2SleepInWorker = 0.15
time2Sleep2Finish = 60
```


# Full decentralized NSGA-II, with the population distributed in the nodes and the communication limited to the neigboring nodes (Neighbor-aware)



Edit the executionConfig.py fila and set

```
executionConfig='neighboraware'
```

Start the python file that execute the solutions that DO NOT require a coordinator


```
python coordinatorFullMigration.py
```


If the executionConfig value is correctly fixed, the following configuration parameters are considered in this experiment scenario execution:

optimizationConfig.py
```python
numberOfSolutionsInWorkers = 10
```

experimentationConfig.py
```python
executionScenario = 'neighboraware'
onlyNeighbors = True
neighborsRadius = 1  #measured in distance(latency) or number of hops
unit4Radius = 'hop'  #distance or hop
numOfWorkers = 20
time2SleepInCoordinator = 0.1
time2SleepInWorker = 0.15
time2Sleep2Finish = 60
```


The results are usually (fixed by the configuration) stored in the "results" folder. Folder "results" contains data and the plots of the experimentation phase for all the repetitions of all the experiments scenarios. These results are organized in folders. Each folder contains the results of one of the 10 repetitions of one of the 4 experiment scenarios. The forlder name indicates the number of repetition and the number of applications and nodes in the expriment sceniaro.


# Plots generation

The results are summarized and the plots generated by executing:

```
python analizeresults.py
```
Usually (set-up by configuration) the results are read from "results" folder and the plots are stored in "plots" folder.  This folder follows the same structure than the "results" folder. Additionally, some plots that aggregate data from all the exeuction repetitions and experiment scenarios are directly stored in the root of folder "results".

Additionally, csv-files are stored with the values of the Pareto fronts for each execution repetition and stored in "pfevaluator" folder. This files can be exported to the pfevaluator project and calculate multi-objective metrics, such as Generational Distance and Spacing, of the results. More information in https://github.com/thieu1995/pfevaluator

