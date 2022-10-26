#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:53:01 2022

@author: carlos
"""

import solutionConfig as config
from random import randrange


class Solution:

    def __init__(self, solConf=None,solInfr=None):

        # __init__(self, solConf=dict())
        # __init__(self)

        if (solConf == None) and (solInfr == None):
            self.initCoordinator()
        elif isinstance(solConf, dict) and isinstance(solInfr, dict) :
            self.initWorker(solConf,solInfr)
        else:
            print("ERROR::::Argument type of class Solution not correct")
            pass

    def initCoordinator(self):
        # self.numberOfNodes = config.numberOfNodes
        # self.numberOfServices = config.numberOfServices
        # self.solutionConfig = dict()
        # self.solutionConfig['numberOfNodes']=self.numberOfNodes
        # self.solutionConfig['numberOfServices']=self.numberOfServices
        # self.generateRandomSolution()
        # self.calculateFitness()
        self.state = 'active'
        pass

    def initWorker(self, solConf, solInfr):
        # self.numberOfNodes = solConf['numberOfNodes']
        # self.numberOfServices = solConf['numberOfServices']
        # self.solutionConfig = solConf
        self.state = 'active'
        self.infrastructure = solInfr
        self.generateRandomSolution(solConf['numberOfNodes'], solConf['numberOfServices'])
        self.calculateFitness()

    # TODO
    def generateRandomSolution(self, numberOfNodes, numberOfServices):
        self.chromosome = [[randrange(2) for iNode in range(numberOfNodes)] for iService in range(numberOfServices)]
        # TODO, the generated chromosome should satisfy the constraints
        pass


    def meanNumberOfInstances(self):
        numInstances = 0
        for serviceAllocation in self.chromosome:
            numInstances = numInstances + sum(serviceAllocation)
        return float(float(numInstances) / float(len(self.chromosome)))

    # TODO check if it is correct
    def meanEdgeDistance(self):
        finalTotalDistance = 0
        for serviceAllocation in self.chromosome: #we run all the services in the system
            closestInstanceDistance = 0 #mean value of the distance between all the clients and its closest instance
            numberOfInstances = sum(serviceAllocation)
            if numberOfInstances > 0:
                for edgeNodeId in self.infrastructure['clientNodes']:
                    #for each service we run across all the edgenodes/clients to find the closest instance of each client
                    minDistance = float('inf')
                    for nodeId, value in enumerate(serviceAllocation):
                        if value == 1:
                            distanceBetweenNodes = self.infrastructure['Gdistances'][str(nodeId)][str(edgeNodeId)]
                            if distanceBetweenNodes < minDistance:
                                minDistance = distanceBetweenNodes
                    closestInstanceDistance = closestInstanceDistance + minDistance
                closestInstanceDistance = float(float(closestInstanceDistance)/float(numberOfInstances))
            else:
                closestInstanceDistance = float('inf')  # if not instances available the distance between the clients and the service is infinite
            finalTotalDistance = finalTotalDistance + closestInstanceDistance
        return float(float(finalTotalDistance) / float(len(self.chromosome)))

    def dominatesTo(self,solB): # checks if self.solution (A) dominates input solB (B)
        atLeastOneBetter = False
        for i in range(len(config.objectivesFunctions)):
            if solB.fitness[i] < self.fitness[i]:
                return False #a does not dominate b because b has at least one better objective
            elif self.fitness[i] < solB.fitness[i]:
                atLeastOneBetter = True
        if atLeastOneBetter:
            return True #a dominates b because b does not have any objective better than a, and at least, one objective in a is better than in b
        else:
            return False #a and b have all the objectives equal. A does not dominate b.



    def calculateFitness(self):
        objectives = list()
        for i in config.objectivesFunctions:
            objValue = eval(i[1])
            objectives.append(objValue)
        self.fitness = objectives
