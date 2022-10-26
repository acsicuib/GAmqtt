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
from log import Log


class OptimizationProblem:
    
    numberOfSolutions = None
    solutionTemplate = None
    population = None
    solutionId=0 #autoincrement to identify the solutions in the population
    
    def __init__(self, log, numSol = None, solTemp = None, solInfr = None):
#    def __init__(self, numSol = None, solTemp = None, solInfr = None):
        self.log = log
        if (numSol==None) and (solTemp == None) and (solInfr == None):
            self.initCoordinator()
            self.createPopulationCoordinator()
        elif (isinstance(numSol,int) and isinstance(solTemp,dict) and isinstance(solInfr,dict)):
            self.initWorker(numSol,solTemp,solInfr)
            self.createPopulationWorker()
        else:
            #self.log.print("ERROR::::Argument type of class OptimizationProblem not correct")
            print("ERROR::::Argument type of class OptimizationProblem not correct")

        


        
    def initCoordinator(self):
        solTempl=dict()
        solTempl['numberOfNodes']=solCnf.numberOfNodes
        solTempl['numberOfServices']=solCnf.numberOfServices
        
        self.solutionTemplate = solTempl
        self.numberOfSolutions = optCnf.numberOfSolutionsInWorkers

        #TODO tener dos secuencias aleatorias, una para la infrastructura y otra para el GA. la de la infrastructura siempre con el mismo seed

        domainConfiguration.initializeRandom(optCnf.randomSeeds)
        domainConfiguration.setRandomState(optCnf.randomSeeds)
        domainConfiguration.setConfigurations()
        #changing default configuration
        domainConfiguration.TOTALNUMBEROFNODES = solCnf.numberOfNodes
        domainConfiguration.TOTALNUMBEROFAPPS = solCnf.numberOfServices
        domainConfiguration.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(domainConfiguration.TOTALNUMBEROFNODES)+", m=2)"
        
    
        domainConfiguration.setRandomState(optCnf.randomSeeds)
        domainConfiguration.networkModel('n'+str(domainConfiguration.TOTALNUMBEROFNODES)+'-')
        domainConfiguration.appsGeneration()
        domainConfiguration.usersConnectionGeneration()

        self.infrastructure = dict()
        #En esta estructura dict metemos todos los datos que necesites low workers para calcular el fitness
    #TODO considerar que las distancias tendrian que esr basadas en los tiempos de propagacion y transmision, es decir, calcular con el weigth del edge

        #all the features of the infrastructure needed by the worker are included in infrastructure dictionary
        self.infrastructure['Gdistances'] = self.deviceDistances(domainConfiguration.Gfdev)
        self.infrastructure['clientNodes'] = self.getEdgesDevices(domainConfiguration.Gfdev)
        #self.g_distances_with_cloud = self.deviceDistances(domainConfiguration.G) ## este tiene el cloud
  
    def getEdgesDevices(self,GRAPH):
        return list(domainConfiguration.gatewaysDevices)

    def deviceDistances(self,GRAPH):
        dist_ = nx.shortest_path_length(GRAPH)
        distances = {}
    
        for i in dist_:
            distances[i[0]]=i[1]
    
        return distances

        
        
    def initWorker(self, numSol, solTemp, solInfr):
        self.numberOfSolutions = numSol
        self.solutionTemplate = solTemp
        self.infrastructure=solInfr
        

    def getWorkerId(self, popElement):
        return popElement['workerId']

    def getSolutionId(self, popElement):
        return popElement['solutionId']

    def getFrontBySolId(self,idWorker,idSol):
        for i,front in enumerate(self.fronts):
            for j,element in enumerate(front):
                if element[0]['workerId']==idWorker and element[0]['solutionId']==idSol:
                    return i,element[1]
        return 0 #ERROR: solution is not found


    def TournamentSelection(self):
        populationPos1,populationPos2 = random.sample(range(0,len(self.population)),2)  #two solution are randomly selected

        #we obtain their front and crowding
        frontNumber1,crowding1 = self.getFrontBySolId(self.population[populationPos1]['workerId'],self.population[populationPos1]['solutionId'])
        frontNumber2,crowding2 = self.getFrontBySolId(self.population[populationPos2]['workerId'],self.population[populationPos2]['solutionId'])

        #the best solution is returned. The best is the one in the lowest front, and if they are in the same front, the one with the highest crowding distance
        if frontNumber1 > frontNumber2:
            return self.population[populationPos1]
        elif frontNumber2 > frontNumber1:
            return self.population[populationPos2]
        elif frontNumber1 == frontNumber2:
            if crowding1 > crowding2:
                return self.population[populationPos1]
            else:
                return self.population[populationPos2]
        else:
            return 0 # error, not comparable fronts

    
    
    def joinWithNewWorkerPopulation(self,workerId,solSet):
        solutionsForParetors = list()
        for sol in solSet:
            newSol = Solution()
            newSol.fitness = sol['fitness']
            newSolutionElement = dict()
            newSolutionElement['workerId']=workerId
            newSolutionElement['solutionId']=sol['id']
            newSolutionElement['solution']=newSol
            self.population.append(newSolutionElement)
            solutionsForParetors.append(newSolutionElement)
            #self.incorporateSolutionIntoFront(newSolutionElement)  # recalculate pareto fronts

        self.shiftSolutionsToHigherFronts(solutionsForParetors, 0) #recalculate pareto fronts for all the new solutions
        

    def incorporateChildrenInCoordinatorPopulation(self,workerId,solSet):
        self.joinWithNewWorkerPopulation(workerId,solSet)
        return self.removeWorstSolutions(len(solSet))


    def removeWorstSolutions(self, solNumber):
        #TODO escoger las peores soluciones de los pareto fronts
        toRemove = list()
#        self.log.print("COORDINATOR:::choosing to remove")
        for i in range(solNumber):
            frontPos=random.randrange(len(self.fronts[-1])) #TODO no hay que elmininar una del ultimo front aleatoriamente, hay que eliminar la que tenga menor crowding distance

            sol2Remove = dict()
            sol2Remove['solutionId']=self.fronts[-1][frontPos][0]['solutionId']
            sol2Remove['workerId']=self.fronts[-1][frontPos][0]['workerId']
            #self.log.print("COORDINATOR:::removing["+str(sol2Remove['solutionId'])+ " from " + str(sol2Remove['workerId']))
            toRemove.append(sol2Remove)

            popElementToRemove,posPopElement = self.getPopulationElementBySolutionId(sol2Remove['solutionId'],sol2Remove['workerId'])

            self.removeWorstSolutionFromFront(popElementToRemove)
            self.population.pop(posPopElement)

            
#        self.log.print("COORDINATOR:::all to remove" + str(toRemove)) 
        return(toRemove)


    def removeSolution(self,idSol):
        for pos,popElement in enumerate(self.population):
            if popElement['solutionId']==idSol:
                self.removeWorstSolutionFromFront(popElement)
                self.population.pop(pos)
                return True
        return False
                


    def incorporateChildrenInWorkerPopulation(self,offspring):
        #decide what it is explained in def crossoverWithRemoteSolution join the two new children or replace two old solutions.
        ##ANSWER: we add it without removing. The role to remove solutions is in charge of the coordinator.
        self.population = self.population + offspring
        #for sol in offspring:
        #    self.incorporateSolutionIntoFront(sol) #call to recalculate pareto fronts for only one solution
        self.shiftSolutionsToHigherFronts(offspring, 0)  # call to recalculate pareto fronts can be done with both of the solutions in the same set

    def twoPointServiceCrossover(self,chr1,chr2):

        newChild1=list()
        newChild2=list()

        for idService in range(len(chr1)):
            serviceFather1 = chr1[idService]
            serviceFather2 = chr2[idService]
            serviceChild1=list()
            serviceChild2=list()
            firstCrossoverPoint=random.randrange(len(serviceFather1))
            secondCrossoverPoint=random.randrange(firstCrossoverPoint,len(serviceFather1))
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


    def evolveWithRemoteSolution(self,chromosome):

        offspring = self.crossOverSolutions(chromosome)
        for sol in offspring:
            if random.random()<optCnf.mutationProbability:
                self.mutateSolution(sol['solution'])
        return offspring

    def mutationSwapNode(self, sol):
        node1,node2 = random.sample(range(0,len(sol.chromosome[0])),2) #two random number between 0 and the number of nodes, the number of columns of the chromosome
        for i in range(len(sol.chromosome)): #go through the line of the chromosome to interchange the two columns node1 and node2
            sol.chromosome[i][node1],sol.chromosome[i][node2] = sol.chromosome[i][node2],sol.chromosome[i][node1]

    def mutationSwapService(self, sol):
        s1, s2 = random.sample(range(0, len(sol.chromosome)), 2) #two random services, ie. two random lines of the chromosome
        sol.chromosome[s1],sol.chromosome[s2] = sol.chromosome[s2],sol.chromosome[s1] # interchange the two lines of the chromosome, the two services

    '''
    INPUT solution: is a solution instance that we want to mutate
    '''
    def mutateSolution(self,solution):
        mutationOperators = []
        mutationOperators.append(self.mutationSwapNode)
        mutationOperators.append(self.mutationSwapService)

        mutationOperators[random.randint(0, len(mutationOperators) - 1)](solution)  #a mutation is randomly executed between the mutations defined at the beginning of the function


    def crossOverSolutions(self,chromosome):
        
        #think about if the new children are just joined with the current population in the local worker, increasing the size of the local population,
        #or they should replace other solutions in the local population, keeping always the same size in the local population but (maybe) removing solutions
        #that are classified in good fronts in the global population in the coordinator
        #ANSWER: we add it without removing. The role to remove solutions is in charge of the coordinator.

        offspring = list()
    
        oneSolution = Solution(self.solutionTemplate,self.infrastructure)
        #newSolutionElement = (idWorker, self.solutionId, oneSolution, 'active')
        firstNewSolutionElement = dict()
        firstNewSolutionElement['workerId']='local'
        firstNewSolutionElement['solutionId']=self.solutionId
        firstNewSolutionElement['solution']=oneSolution
        self.solutionId = self.solutionId+1

        oneSolution = Solution(self.solutionTemplate,self.infrastructure)
        #newSolutionElement = (idWorker, self.solutionId, oneSolution, 'active')
        secondNewSolutionElement = dict()
        secondNewSolutionElement['workerId']='local'
        secondNewSolutionElement['solutionId']=self.solutionId
        secondNewSolutionElement['solution']=oneSolution
        self.solutionId = self.solutionId+1

        popElement = self.TournamentSelection()
        secondFatherId = self.getSolutionId(popElement)
        secodFatherWorkerId = self.getWorkerId(popElement)

        #we search the solutionid in the list containing all the dictionaries, which element solutionid is the one to search
        secondChromosome= self.getSolutionChromosomeById(secondFatherId,secodFatherWorkerId)

        childChrom1, childChrom2 = self.twoPointServiceCrossover(chromosome, secondChromosome)
        firstNewSolutionElement['solution'].chromosome=childChrom1
        secondNewSolutionElement['solution'].chromosome=childChrom2

        firstNewSolutionElement['solution'].calculateFitness()
        secondNewSolutionElement['solution'].calculateFitness()

        offspring.append(firstNewSolutionElement)
        offspring.append(secondNewSolutionElement)

        return offspring



    def getPopulationElementBySolutionId(self,solId,workerId):
        for i,sol in enumerate(self.population):
            if sol['solutionId']==solId and sol['workerId']==workerId:
                return sol,i
        return None,None

    def getSolutionChromosomeById(self,solId,workerId):
        populationElement,pos = self.getPopulationElementBySolutionId(solId,workerId)
        if populationElement==None:
            return None
        else:
            return populationElement['solution'].chromosome


    def calculateCuboid(self,sortedElements,pos,front):
        solMiddle = sortedElements[pos]

        if pos!=1:
            solPrev = sortedElements[pos-1]
            if solMiddle[0]==solPrev[0]:
                if front[solPrev[1]][0]['solution'].fitness == front[solMiddle[1]][0]['solution'].fitness:
                    return 0.0
        if pos!=-1:
            solNext = sortedElements[pos + 1]
            if solMiddle[0] == solNext[0]:
                if front[solNext[1]][0]['solution'].fitness == front[solMiddle[1]][0]['solution'].fitness:
                    return 0.0
        if pos!=1 and pos!=-1:
            return solNext[0] - solPrev[0]
        elif pos==1:
            return solNext[0] - solMiddle[0]
        elif pos==-1:
            return solMiddle[0] - solPrev[0]

    def calculateCrawdingDistance(self, front):

        for frontElement in front:
            frontElement[1]=0.0 #all the crowding distances are initialized to 0
        if len(front)<3:
            return None#if there are only 2, 1 or 0 elements in the front, the crowding distance is 0
        for objPos in range(len(solCnf.objectivesFunctions)):
            listOfObjectivePosPair =list()
            for pos, frontElement in enumerate(front): #we create a structure to know the value of the fitness and the position in the front for the solution with this value
                fitnessValue =  frontElement[0]['solution'].fitness[objPos]
                objectivePosElement = [fitnessValue,pos]
                listOfObjectivePosPair.append(objectivePosElement)
            sortedElements = sorted(listOfObjectivePosPair,key=lambda x:x[0])
            minValue = sortedElements[0][0]
            maxValue = sortedElements[-1][0]
            normalizedDenominator=float(maxValue-minValue)
            if normalizedDenominator>0.0: #check normalizedDenominator bigger than 0.0
                #if the max and minimum value are equal, the crowding distance of all the elements is 0.0
                #if normalizeddenominator == 0.0 do nothing FOR THIS OBJECTIVE because all the crowding distances were initialized to 0.0 at the beginning of the function
                for thePair in sortedElements:
                    thePair[0]=float(float(thePair[0])/float(normalizedDenominator))
                #assumption: there are more than 2 elements in the list, because it was checked at the beginning of the function
                for posPair in range(1,len(sortedElements)-1):
                    #crawdingIncrement = sortedElements[posPair + 1][0] - sortedElements[posPair - 1][0]
                    crawdingIncrement = self.calculateCuboid(sortedElements,posPair,front)
                    #front[listPosition][1:crowdingdistancevalue]
                    front[sortedElements[posPair][1]][1] = front[sortedElements[posPair][1]][1] + crawdingIncrement

                #the smallest and biggest elements have a crawding distance of the double distance with the only neighbourd they have
                posPair = 1
                #crawdingIncrement = 2*(sortedElements[posPair + 1][0] - sortedElements[posPair][0])
                crawdingIncrement = 2*self.calculateCuboid(sortedElements, posPair, front)
                front[sortedElements[posPair][1]][1] = front[sortedElements[posPair][1]][1] + crawdingIncrement
                posPair = -1
                #crawdingIncrement = 2*(sortedElements[posPair][0] - sortedElements[posPair-1][0])
                crawdingIncrement = self.calculateCuboid(sortedElements, posPair, front)
                front[sortedElements[posPair][1]][1] = front[sortedElements[posPair][1]][1] + crawdingIncrement


#LOS TRES SITIOS DONDE CALCULO CRAWDING INCREMENT DEBO SUSTITUIRLO POR CALCULAR  CUBOIDE, LA NUEVA FUNCION




    '''
    Recursive functions that,for a set of new solutions, checks if the are in the current pareto front. Each
    solution in the set of moving solutions is isolated analyzed to check if it dominates solutions in the current
    front, or if it is dominated by solutions in the fronts.
    If the the solution dominates solutions in the fronts, the set of dominated solution is included in the set of 
    solutions to include in the next recursive call to the function. I,e, they are moved to higher fronts.
    If the solution is not dominated by any solution in the front, the new solution is included in this front. If not,
    the new solution is included in the in the set of solutions to include in the next recursive call to the function,
    i.e. the search of its front will continue in higher fronts.
    INPUTS: listOfMovingSolutions: the solutions that need to be checked if the are included in the front. The elements
    of this list are population elements, which are dictionaries with workerId, solutionId and solution (object instance).
    frontNumber: the current front to analyize the inclusion of the set of solutions
    '''
    def shiftSolutionsToHigherFronts(self,listOfMovingSolutions,frontNumber):
        if len(self.fronts)<=frontNumber: #if we have already analized all the previous fronts, we need to create a new front to include the current moving/shifted solutions. Those solutions are the ones that are not included in previous fronts.
            newFront = list()
            for newSolution in listOfMovingSolutions:
                frontElement = [newSolution, float('inf')] #the front element is a tuple with the population element and the crowding distance
                newFront.append(frontElement)
            self.fronts.append(newFront)
            self.calculateCrawdingDistance(newFront)
            return 0 #no more fronts require to be analyzed.
        currentFront = self.fronts[frontNumber]
        newShiftedSolutions = list() # the set of solutions that will be moved/shifted to higher fronts
        recalculateCrawding = False
        for newSolution in listOfMovingSolutions: #for all the solutions in the parameter of solution lists to evaluate where to be placed in the fronts
            solInstanceInMovingList = newSolution['solution']
            dominatedSolutions = list()
            for i,frontElement in enumerate(currentFront):  #searching the solutions that are dominated by the newsolution in the current from
                solInstanceInFront = frontElement[0]['solution']
                if solInstanceInMovingList.dominatesTo(solInstanceInFront):
                    dominatedSolutions.append(i)
            if len(dominatedSolutions) > 0:
                recalculateCrawding = True
            dominatedSolutions.sort(reverse=True)#the elements in a list has to be removed in descending order, if not, the indexes change as the elements are removed
            for pos in dominatedSolutions: #all the dominated solutions are removed from the front and shifted to the higher front
                newShiftedSolutions.append(currentFront[pos][0])
                currentFront.pop(pos)
            isNewSolutionDominatedbySomeOne = False
            for i,frontElement in enumerate(currentFront): #we check if the new solution is dominated by someone
                solInstanceInFront = frontElement[0]['solution']
                if solInstanceInFront.dominatesTo(solInstanceInMovingList):
                    isNewSolutionDominatedbySomeOne = True #we found that at least one solutin in the front dominates the new solution
                    break
            if isNewSolutionDominatedbySomeOne:
                newShiftedSolutions.append(newSolution) #if it is dominated by some solution in the front, the new solutions is pass through to a higher front
            else:
                frontElement = [newSolution,float('inf')] #it no other solution dominates the new one, it is included in the front.
                currentFront.append(frontElement)
                recalculateCrawding = True


        if recalculateCrawding: #if some solutions are removed from this front and shifted to higher fronts, or if any of the new solution is included in the front we need to recalculate crawding distances
            self.calculateCrawdingDistance(currentFront)

        if len(newShiftedSolutions)>0: #if there is still solutions to place into the fronts, the function is recursevilly called to the next higher front
            self.shiftSolutionsToHigherFronts(newShiftedSolutions,frontNumber+1)



    # def incorporateSolutionIntoFront(self,sol):
    #     movingSolutions = list()
    #     movingSolutions.append(sol)
    #     self.shiftSolutionsToHigherFronts(movingSolutions,0)


    '''
    Remove one solution of the fronts. The removing process is performed under the assumption that the element to
    remove is the worst one, and consequently, it is placed in the last front. Thus, a reorganization of the fronts
    is not required.
    INPUTS: one the population Element from the list self.population. This popElement is a dictionary with the 
    workerId the solutionId and the solution (instance of the solution) 
    '''
    def removeWorstSolutionFromFront(self,popElement):
        for i,front in enumerate(self.fronts):  #go through the fronts
            for j,frontElement in enumerate(front): #go through the solutions in a front. those front elements ara a duple of the populationElement and the croding distance
                if frontElement[0]['solutionId']==popElement['solutionId'] and frontElement[0]['workerId']==popElement['workerId']:
                   #when the solution to remove is found, the front element is removed
                   front.pop(j)
                   if len(front)==0:
                       #if the removed solution is the last one in the front, the front must be removed.
                       self.fronts.pop(i)
                   return
        #self.log.print("ERRORRRR: solution to remove from the front is not found")
        print("ERRORRRR: solution to remove from the front is not found")

    '''
    This function is executed when the execution of the coordinator starts. The initial population of the 
    coordinator is empty, because the random initial populations are created in the workers.
    INPUTS: None
    '''
    def createPopulationCoordinator(self):
        self.population=list()
        self.fronts=list()


    '''
    This function is executed when the execution of the worker starts. The initial population of the 
    worker has the size of the configuration file and the solution template.
    The population is stored in self.population and the elements of this list are dictionaries with
    the workerId the solutionId and the solution (instance of the solution object)
    The structure to store the fronts self.fronts is also created (empty). For each new solution
    (one loop of the for) the new solution is included in the self.population and in the corresponding
    front (calling function self.incorporateSolutionIntoFront). The identificator of the solution is
    also increased (solutionId)
    INPUTS: None
    '''
    def createPopulationWorker(self):
        #we create the population with the specified solution template
        self.population = list()
        self.fronts = list()
        solutionsForParetors = list()
        for i in range(self.numberOfSolutions):
            oneSolution = Solution(self.solutionTemplate,self.infrastructure)
            newSolutionElement = dict()
            newSolutionElement['workerId']=optCnf.selfId4Worker
            newSolutionElement['solutionId']=self.solutionId
            newSolutionElement['solution']=oneSolution


            self.population.append(newSolutionElement)
            solutionsForParetors.append(newSolutionElement)
            #self.incorporateSolutionIntoFront(newSolutionElement) #recalculate pareto for each single solution
            self.solutionId = self.solutionId+1

        self.shiftSolutionsToHigherFronts(solutionsForParetors, 0)  # recalculate pareto fronts for all the new solutions
            
    '''
    This function returns a list/dictionary structure with the fitnesses of the solutions. This structure
    can be serialized into a json file
    INPUTS: If a population is included as parameter, we serialized the input populaiton, if not, 
    self.populuation is serialized
    '''
    def fitness2json(self, pop=None):
        # If a population is included as parameter, we serialized the input populaiton, if not, self.populuation is serialized
        if pop==None:
            population = self.population
        else:
            population = pop

        #a dictionary structure is create where id is the solutionId and fitness is the array with all the fitness values of the objectives
        setOfSolutions = list()
        for sol in population:
            oneSolution = dict()
            oneSolution['id']=sol['solutionId']
            oneSolution['fitness']=list(sol['solution'].fitness)
            setOfSolutions.append(oneSolution)
        return setOfSolutions