



workersAutomaticStart = True #true if we want that the coordinator automatically start
numberOfRepetitions = 10



#setup for the execution of decentralized evolutino but centralized solution space (fronts in coordinator)
#required for the execution of coordinator.py and worker.py
#executionScenario = 'centralizedNSGA'
#numOfWorkers = 20
#time2SleepInCoordinator = 0.05
#time2SleepInWorker = 0.0
#time2Sleep2Finish = 20

#setup for traditional NSGA-II
#required for the execution of coordinator.py and worker.py
#executionScenario = 'traditionalNSGA'
#numOfWorkers = 1
#time2SleepInCoordinator = 0.05
#time2SleepInWorker = 0.0
#time2Sleep2Finish = 20

#setup for full distributed with migration of solutions between any node
#required for the execution of coordinatorFullMigration.py and workerFullMigration.py
#executionScenario = 'fullMigration'
#onlyNeighbors = False
#numOfWorkers = 20
#time2SleepInCoordinator = 0.1
#time2SleepInWorker = 0.15
#time2Sleep2Finish = 60

#setup for full distributed with migration of solutions only between neighbours
#required for the execution of coordinatorFullMigration.py and workerFullMigration.py
executionScenario = 'fullOnlyNeighbours'
onlyNeighbors = True
neighborsRadius = 1  #measured in distance(latency) or number of hops
unit4Radius = 'hop'  #distance or hop
numOfWorkers = 20
time2SleepInCoordinator = 0.1
time2SleepInWorker = 0.15
time2Sleep2Finish = 60


