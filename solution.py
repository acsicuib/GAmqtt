#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:53:01 2022

@author: carlos
"""

import solutionConfig as config
from typing import List
from typing import Tuple
import random
import numpy

class Solution:

    def __init__(self, rng: numpy.random.mtrand.RandomState, solConf: dict =None, solInfr: dict =None) -> None:

        # __init__(self, solConf=dict())
        # __init__(self)
        self.randomNG = rng
        if (solConf == None) and (solInfr == None):
            self.initCoordinator()
        elif isinstance(solConf, dict) and isinstance(solInfr, dict) :
            self.initWorker(solConf,solInfr)
        else:
            print("ERROR::::Argument type of class Solution not correct")


    def initCoordinator(self) -> None:
        # self.numberOfNodes = config.numberOfNodes
        # self.numberOfServices = config.numberOfServices
        # self.solutionConfig = dict()
        # self.solutionConfig['numberOfNodes']=self.numberOfNodes
        # self.solutionConfig['numberOfServices']=self.numberOfServices
        # self.generateRandomSolution()
        # self.calculateFitness()
        self.state = 'active'


    def initWorker(self, solConf: dict, solInfr: dict) -> None:
        # self.numberOfNodes = solConf['numberOfNodes']
        # self.numberOfServices = solConf['numberOfServices']
        # self.solutionConfig = solConf
        self.state = 'active'
        self.infrastructure = solInfr
        satisfiedConstraints = False
        while not satisfiedConstraints:
            self.generateRandomChromosome(solConf['numberOfNodes'], solConf['numberOfServices'])
            satisfiedConstraints = self.checkConstraints()
        self.calculateFitness()


    def generateRandomChromosome(self, numberOfNodes: int, numberOfServices: int) -> None:
        self.chromosome = [[self.randomNG.randint(2) for iNode in range(numberOfNodes)] for iService in range(numberOfServices)]



    def meanNumberOfInstances(self) -> float:
        numInstances = 0
        for serviceAllocation in self.chromosome:
            numInstances = numInstances + sum(serviceAllocation)
        return float(float(numInstances) / float(len(self.chromosome)))

    # TODO check if it is correct
    def meanEdgeDistance(self) -> float:
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

    def dominatesTo(self, solB: 'Solution') -> bool: # checks if self.solution (A) dominates input solB (B)
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



    def calculateFitness(self) -> None:
        objectives = list()
        for i in config.objectivesFunctions:
            objValue = eval(i[1])
            objectives.append(objValue)
        self.fitness = objectives


    def setFitness(self, fitnessValues: List[float]) -> None:
        self.fitness = fitnessValues

    def getFitness(self) -> List[float]:
        return self.fitness

    def mutationSwapNode(self) -> None:
        node1,node2 = self.randomNG.choice(len(self.chromosome[0]),2,replace=False) #two random number between 0 and the number of nodes, the number of columns of the chromosome
        for i in range(len(self.chromosome)): #go through the line of the chromosome to interchange the two columns node1 and node2
            self.chromosome[i][node1],self.chromosome[i][node2] = self.chromosome[i][node2],self.chromosome[i][node1]

    def mutationSwapService(self) -> None:
        s1, s2 = self.randomNG.choice(len(self.chromosome), 2, replace=False) #two random services, ie. two random lines of the chromosome
        self.chromosome[s1],self.chromosome[s2] = self.chromosome[s2],self.chromosome[s1] # interchange the two lines of the chromosome, the two services

    '''
    INPUT solution: is a solution instance that we want to mutate
    '''
    def mutate(self) -> None:
        satisfiedConstraints = False
        while not satisfiedConstraints:
            mutationOperators = []
            mutationOperators.append(self.mutationSwapNode)
            mutationOperators.append(self.mutationSwapService)

            mutationOperators[self.randomNG.randint(len(mutationOperators))]()  #a mutation is randomly executed between the mutations defined at the beginning of the function
            satisfiedConstraints = self.checkConstraints()


    def crossover(self, chromosome: List[list]) -> List['Solution']:

        satisfiedConstraints = False
        while not satisfiedConstraints:
            chr = [0]*2
            chr[0], chr[1] = self.twoPointServiceCrossover(self.chromosome,chromosome)

            solutions = list()
            satisfiedConstraints = True
            for i in range(len(chr)):
                sol = Solution(self.randomNG)
                sol.infrastructure = self.infrastructure
                sol.chromosome = chr[i]
                self.state = 'active'
                solutions.append(sol)
                satisfiedConstraints = satisfiedConstraints and sol.checkConstraints()

        return solutions



    def twoPointServiceCrossover(self,chr1: List[list], chr2: List[list]) -> Tuple[List[list],List[list]] :

        newChild1=list()
        newChild2=list()

        for idService in range(len(chr1)):
            serviceFather1 = chr1[idService]
            serviceFather2 = chr2[idService]
            serviceChild1=list()
            serviceChild2=list()
            firstCrossoverPoint=self.randomNG.randint(len(serviceFather1))
            secondCrossoverPoint=self.randomNG.randint(firstCrossoverPoint,len(serviceFather1))
            for idNode in range(firstCrossoverPoint):
                serviceChild1.append(serviceFather1[idNode])
                serviceChild2.append(serviceFather2[idNode])
            for idNode in range(firstCrossoverPoint,secondCrossoverPoint+1):
                serviceChild2.append(serviceFather1[idNode])
                serviceChild1.append(serviceFather2[idNode])
            for idNode in range(secondCrossoverPoint+1,len(serviceFather1)):
                serviceChild1.append(serviceFather1[idNode])
                serviceChild2.append(serviceFather2[idNode])
            newChild1.append(serviceChild1)
            newChild2.append(serviceChild2)

        return newChild1, newChild2


    def getChromosome(self) -> List[list]:
        return self.chromosome

    def checkConstraints(self) -> bool:
        #the loops where this function is called could get into in an infinite loop without finishing the croosover/
        #mutation/random initialization
        #TODO implement this for the specific optimization problem
        #TODO a repeir operator can be applied to fix the constraints unmeet
        return True