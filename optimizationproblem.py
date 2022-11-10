#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 10:18:56 2022

@author: carlos
"""
import random

import solutionConfig as solCnf
import optimizationConfig as optCnf
from solution import Solution
import random
import domainConfiguration
import networkx as nx
from solutionspace import SolutionSpace
from solutionspace import PopulationElement
from typing import List
from typing import Set
from log import Log
from infrastructure import Infrastructure
import numpy

class OptimizationProblem:
    
    #numberOfSolutions = None
    solutionTemplate = None
    #population = None
    #solutionId=0 #autoincrement to identify the solutions in the population
    
    def __init__(self, log: Log, randomseed:int,  numSol: int = None, solTemp: dict = None, solInfr:dict = None) -> None:
#    def __init__(self, numSol = None, solTemp = None, solInfr = None):
        self.log = log
        self.randomSeed = randomseed
        if optCnf.randomReproducible4Optimization:
            self.randomNG = numpy.random.RandomState(self.randomSeed)
        else:
            self.randomNG = numpy.random.RandomState()
        if (numSol==None) and (solTemp == None) and (solInfr == None):
            self.initCoordinator()

        elif (isinstance(numSol,int) and isinstance(solTemp,dict) and isinstance(solInfr,dict)):
            self.initWorker(numSol,solTemp,solInfr)

        else:
            #self.log.print("ERROR::::Argument type of class OptimizationProblem not correct")
            print("ERROR::::Argument type of class OptimizationProblem not correct")

        


        
    def initCoordinator(self) -> None:
        solTempl=dict()
        solTempl['numberOfNodes']=solCnf.numberOfNodes
        solTempl['numberOfServices']=solCnf.numberOfServices
        
        self.solutionTemplate = solTempl
        self.numberOfSolutionsInWorker = optCnf.numberOfSolutionsInWorkers
        self.solutionSpace = SolutionSpace(len(solCnf.objectivesFunctions),self.randomNG)

        self.deployedInfr = Infrastructure()
        netGeneratorStr = "nx.barabasi_albert_graph(n="+str(solCnf.numberOfNodes)+", m=2)"
        self.deployedInfr.setConfiguration('newage',solCnf.numberOfNodes,solCnf.numberOfServices,netGeneratorStr)
        self.deployedInfr.deployScenario(False)

        # domainConfiguration.initializeRandom(optCnf.randomSeeds)
        # domainConfiguration.setRandomState(optCnf.randomSeeds)
        # domainConfiguration.getConfiguration('')
        # #changing default configuration
        # domainConfiguration.TOTALNUMBEROFNODES = solCnf.numberOfNodes
        # domainConfiguration.TOTALNUMBEROFAPPS = solCnf.numberOfServices
        # domainConfiguration.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(domainConfiguration.TOTALNUMBEROFNODES)+", m=2)"
        #
        #
        # domainConfiguration.setRandomState(optCnf.randomSeeds)
        # domainConfiguration.networkModel('n'+str(domainConfiguration.TOTALNUMBEROFNODES)+'-')
        # domainConfiguration.appsGeneration()
        # domainConfiguration.usersConnectionGeneration()

        self.infrastructure4mqttJson = dict()
        #En esta estructura dict metemos todos los datos que necesites low workers para calcular el fitness
    #TODO considerar que las distancias tendrian que esr basadas en los tiempos de propagacion y transmision, es decir, calcular con el weigth del edge

        #all the features of the infrastructure needed by the worker are included in infrastructure dictionary
        self.infrastructure4mqttJson['Gdistances'] = self.deployedInfr.deviceDistances()
        self.infrastructure4mqttJson['clientNodes'] = self.deployedInfr.getEdgesDevices()
        #self.g_distances_with_cloud = self.deviceDistances(domainConfiguration.G) ## este tiene el cloud

        #self.solutionSpace.createRandomPopulationCoordinator(self.solutionTemplate, self.infrastructure,optCnf.selfId4Worker)



        
        
    def initWorker(self, numSol: int, solTemp: dict, solInfr: dict) -> None:
        #self.numberOfSolutions = numSol
        self.solutionSpace = SolutionSpace(len(solCnf.objectivesFunctions),self.randomNG)
        self.solutionTemplate = solTemp
        self.infrastructure4mqttJson=solInfr
        self.solutionSpace.createRandomPopulationAndJoin(self.solutionTemplate, self.infrastructure4mqttJson,optCnf.selfId4Worker,numSol)
        


    '''
    The current population is joined with the solutions received from the workers. This solutions only have the fitnes
    so new solutions elements are created and append to the population
    '''
    def joinToPopulation(self,workerId: str,solSet: List[dict]) -> None:
        self.solutionSpace.createSolutionWithInputAndJoinWithCurrentPopulation(workerId,solSet)

    def removeManyWorstSolutions(self, quantity: int) -> List[PopulationElement]:
        return self.solutionSpace.removeSetOfWorstSolutions(quantity)



    def removeOneWorstSolutionById(self, idSol: str, idWorker: str) -> bool:
        return self.solutionSpace.removeSolution(idSol,idWorker)


    def joinTwoPopulations(self,offspring: List[PopulationElement]) -> None:
        self.solutionSpace.joinToThePopulation(offspring)

    def evolveWithRemoteSolution(self,chromosome: List[List[int]]) -> List[PopulationElement]:

        popElement = self.TournamentSelection()
        solutions = popElement.getSolution().crossover(chromosome)
        for sol in solutions:
            if self.randomNG.random()<optCnf.mutationProbability:
                sol.mutate()
            sol.calculateFitness()

        offspring = self.solutionSpace.createSubPopulation(solutions, optCnf.selfId4Worker)
        return offspring



    #
    # def crossOverSolutions(self,chromosome):
    #
    #     #think about if the new children are just joined with the current population in the local worker, increasing the size of the local population,
    #     #or they should replace other solutions in the local population, keeping always the same size in the local population but (maybe) removing solutions
    #     #that are classified in good fronts in the global population in the coordinator
    #     #ANSWER: we add it without removing. The role to remove solutions is in charge of the coordinator.
    #
    #     offspring = list()
    #
    #     oneSolution = Solution(self.solutionTemplate,self.infrastructure)
    #     #newSolutionElement = (idWorker, self.solutionId, oneSolution, 'active')
    #     firstNewSolutionElement = dict()
    #     firstNewSolutionElement['workerId']='local'
    #     firstNewSolutionElement['solutionId']=self.solutionId
    #     firstNewSolutionElement['solution']=oneSolution
    #     self.solutionId = self.solutionId+1
    #
    #     oneSolution = Solution(self.solutionTemplate,self.infrastructure)
    #     #newSolutionElement = (idWorker, self.solutionId, oneSolution, 'active')
    #     secondNewSolutionElement = dict()
    #     secondNewSolutionElement['workerId']='local'
    #     secondNewSolutionElement['solutionId']=self.solutionId
    #     secondNewSolutionElement['solution']=oneSolution
    #     self.solutionId = self.solutionId+1
    #
    #     popElement = self.TournamentSelection()
    #     secondFatherId = self.getSolutionId(popElement)
    #     secodFatherWorkerId = self.getWorkerId(popElement)
    #
    #
    #     #we search the solutionid in the list containing all the dictionaries, which element solutionid is the one to search
    #     secondChromosome= self.getSolutionChromosomeById(secondFatherId,secodFatherWorkerId)
    #
    #     childChrom1, childChrom2 = self.twoPointServiceCrossover(chromosome, secondChromosome)
    #     firstNewSolutionElement['solution'].chromosome=childChrom1
    #     secondNewSolutionElement['solution'].chromosome=childChrom2
    #
    #     firstNewSolutionElement['solution'].calculateFitness()
    #     secondNewSolutionElement['solution'].calculateFitness()
    #
    #     offspring.append(firstNewSolutionElement)
    #     offspring.append(secondNewSolutionElement)
    #
    #     return offspring
    #



    def getSolutionChromosomeById(self,solId: int, workerId: str) -> List[List[int]]:
        populationElement,pos = self.solutionSpace.getPopulationElementBySolutionId(solId,workerId)
        if populationElement==None:
            return None
        else:
            return populationElement.getSolution().getChromosome()




    # def incorporateSolutionIntoFront(self,sol):
    #     movingSolutions = list()
    #     movingSolutions.append(sol)
    #     self.shiftSolutionsToHigherFronts(movingSolutions,0)



    def TournamentSelection(self) -> PopulationElement:
        popEl1, popEl2 = self.solutionSpace.getRandomSolutions(2)
        bestPopEl = self.solutionSpace.chooseBetter(popEl1,popEl2)
        return bestPopEl

        # we obtain their front and crowding


    def getPopulationFitnessInJson(self) -> List[dict]:
        return self.solutionSpace.fitness2json()

    def getSolutionsFitnessInJson(self, peList: List[PopulationElement]) -> List[dict]:
        return self.solutionSpace.fitness2json(peList)

    def getSolutionSpace(self) -> SolutionSpace:
        return self.solutionSpace