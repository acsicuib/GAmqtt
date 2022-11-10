#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:46:40 2022

@author: carlos
"""

numberOfGenerations = 100

#setup for the execution of decentralized evolutino but centralized solution space (fronts in coordinator)
#numberOfSolutionsInWorkers = 10  #there are 20 workers

#setup for traditional NSGA-II
numberOfSolutionsInWorkers = 200 #there are only 1 worker

mutationProbability = 0.3
selfId4Worker = 'local'


#The same infrastructure is used for all the repetitions of the same execution scenario
randomReproducible4Infrastructure = True
randomSeed4Infrastructure = 2022

# the seed is different for each repetition. But it is necessary to guarantee as many seeds as repetition are executed
randomReproducible4Optimization = True
randomSeed4Optimization = [1, 1001, 2001, 3001, 4001, 5001, 6001, 7001, 8001, 9001] #eval(IP equipo)
randomSeed4OptimizationInCoordinator = [1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987]

