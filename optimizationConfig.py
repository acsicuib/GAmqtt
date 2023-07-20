#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:46:40 2022

@author: carlos
"""

import executionConfig

#numberOfGenerations = 100
numberOfGenerations = 20

if executionConfig.executionConfig=='traditionalNSGA':
    numberOfSolutionsInWorkers = 200
else:
    numberOfSolutionsInWorkers = 10
#setup for fullMigration, fullOnlyNeighbours and centralizedNSGA
#numberOfSolutionsInWorkers = 10  #there are 20 workers
#setup for traditionalNSGA
#numberOfSolutionsInWorkers = 200 #there are only 1 worker

mutationProbability = 0.3
selfId4Worker = 'local'


#The same infrastructure is used for all the repetitions of the same execution scenario
randomReproducible4Infrastructure = True #If True, the seed is used for the random generation of the infrasctructure. If False, a different infracstructure is generated in each execution
randomSeed4Infrastructure = 2022  # The seed for the random generation of the infrastructure.

# the seed is different for each repetition. But it is necessary to guarantee as many seeds as repetition are executed
randomReproducible4Optimization = True #If True, the list of seeds is used for the random number generators of the optimization algorithms. If False, the random values of the optimization are different in each execution
randomSeed4Optimization = [1, 1001, 2001, 3001, 4001, 5001, 6001, 7001, 8001, 9001] #eval(IP equipo)  #Seeds values for each execution repetition in the worker. the value is transformed in the worker with the worker id to generate different seeds in each coodinator
randomSeed4OptimizationInCoordinator = [1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987] #Seeds values for each execution repetition in the coordinator

