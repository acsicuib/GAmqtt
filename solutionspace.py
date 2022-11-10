from typing import List
from typing import Tuple
from solution import Solution
import random
import numpy
from collections import Counter

class PopulationElement:

    def __init__(self, workerId: str, solId: int, sol: Solution) -> None:
        self.solution = sol
        self.workerId = workerId
        self.solId = solId

    def getSolution(self) -> Solution:
        return self.solution

    def getWorkerId(self) -> str:
        return self.workerId

    def getSolutionId(self) -> int:
        return self.solId


class FrontElement:

    def __init__(self, popElement: PopulationElement, crowdingDistance: float) -> None:
        self.populationElement = popElement
        self.crowding = crowdingDistance
        #self.objectivesNumber = numberOfObjectives

    def setCrowding(self, crowVal: float) -> None:
        self.crowding = crowVal

    def getCrowding(self) -> float:
        return self.crowding

    def getPopulationElement(self) -> PopulationElement:
        return self.populationElement

    def getSolution(self) -> Solution:
        popEl = self.getPopulationElement()
        return popEl.getSolution()

    def getSolutionId(self) -> int:
        return self.getPopulationElement().getSolutionId()

    def getWorkerId(self) -> str:
        return self.getPopulationElement().getWorkerId()



class SolutionSpace:

    def __init__(self, numObj: int, rng: numpy.random.mtrand.RandomState) -> None:
        self.fronts = list()
        self.population = list()
        self.solutionId=0
        self.objectivesNumber = numObj
        self.randomNG = rng

    def getFrontCrowdingBySolId(self,idWorker: str, idSol:int ) -> Tuple[int,float]:

        for i,front in enumerate(self.fronts):
            for j,element in enumerate(front):
                if element.getWorkerId()==idWorker and element.getSolutionId()==idSol:
                    return i, element.getCrowding()
        return 0 #ERROR: solution is not found



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
    def createRandomPopulationAndJoin(self,solTemplate: dict, infrastructure: dict, workerId: str, numberOfSolutions: int) -> None:
        # we create the population with the specified solution template
#        self.population = list()
#        self.fronts = list()
        solutionsForParetos = list()
        for i in range(numberOfSolutions):
            oneSolution = Solution(self.randomNG,solTemplate, infrastructure)
            newPopulationElement = PopulationElement(workerId,self.solutionId,oneSolution)
            #newSolutionElement['workerId'] = optCnf.selfId4Worker
            #newSolutionElement['solutionId'] = self.solutionId
            #newSolutionElement['solution'] = oneSolution

            self.population.append(newPopulationElement)
            solutionsForParetos.append(newPopulationElement)
            # self.incorporateSolutionIntoFront(newSolutionElement) #recalculate pareto for each single solution
            self.solutionId = self.solutionId + 1

        self.shiftSolutionsToHigherFronts(solutionsForParetos,
                                          0)  # recalculate pareto fronts for all the new solutions

    '''
    When a new worker is started, it locally create a set of N solutions. Those N new solutions in the worker, 
    are included in the coordinator population. The size of the population of the coordinator is increased by N, 
    i.e., no solutions are removed front coordinator population
    '''
    def createSolutionWithInputAndJoinWithCurrentPopulation(self, workerId: str, solSet: List[dict]) -> None:
        solutionsForParetos = list()
        for sol in solSet:
            newSol = Solution(self.randomNG)
            newSol.setFitness(sol['fitness'])
            newPopulationElement = PopulationElement(workerId,sol['id'],newSol)
            #newSolutionElement['workerId'] = workerId
            #newSolutionElement['solutionId'] = sol['id']
            #newSolutionElement['solution'] = newSol
            self.population.append(newPopulationElement)
            solutionsForParetos.append(newPopulationElement)
            # self.incorporateSolutionIntoFront(newSolutionElement)  # recalculate pareto fronts

        self.shiftSolutionsToHigherFronts(solutionsForParetos,
                                          0)  # recalculate pareto fronts for all the new solutions




    def joinToThePopulation(self,offspring: List[PopulationElement]) -> None:
        #decide what it is explained in def crossoverWithRemoteSolution join the two new children or replace two old solutions.
        ##ANSWER: we add it without removing. The role to remove solutions is in charge of the coordinator.
        self.population = self.population + offspring
        #for sol in offspring:
        #    self.incorporateSolutionIntoFront(sol) #call to recalculate pareto fronts for only one solution
        self.shiftSolutionsToHigherFronts(offspring, 0)  # call to recalculate pareto fronts can be done with both of the solutions in the same set


    '''
    This function is executed when the execution of the coordinator starts. The initial population of the 
    coordinator is empty, because the random initial populations are created in the workers.
    INPUTS: None
    '''
    def createRandomPopulationCoordinator(self, solTemplate: dict, infrastructure: dict, workerId: str) -> None:
        pass

    '''
    This function is call from the worker, when a solution has to be removed as the action of a topic of removesolution
    This topic indicates the solutions to remove that have been discarded from the coordinator, and this is always the
    worst solution in the pareto fronts of the coordinator. The worst solution in the coordinator fronts, is also the 
    worst solution in the worker fronts.
    '''
    def removeSolution(self, idSol: str, idWorker: str) -> bool:
        for pos, popElement in enumerate(self.population):
            if popElement.getSolutionId() == idSol and popElement.getWorkerId() == idWorker:
                self.removeWorstSolutionFromFront(popElement)
                self.population.pop(pos)
                return True
        return False


    '''
    This funciton is usually call after a crossover operation and the following incorporation of the children in the
    population. A set of the input size is removed from the population. The removed solutions are the worst ones in 
    the fronts, ie, the solutions with the smallest crowding distance in the last front
    '''
    def removeSetOfWorstSolutions(self, solNumber: int) -> List[PopulationElement]:
        # The worst solutions from the fronts are selected. The worst solutions are the ones in the last front
        #with the smallest crowding distance (closest to other solutions).
        toRemove = list()
        #        self.log.print("COORDINATOR:::choosing to remove")
        for i in range(solNumber):
            fe,posFe = self.getFrontElementWithSmallestCrowdingInFront(-1)
            self.removeSolutionFromFrontByFrontIdAndPos(-1,posFe)
            #frontPos = random.randrange(len(self.fronts[
            #                                    -1]))    no hay que elmininar una del ultimo front aleatoriamente, hay que eliminar la que tenga menor crowding distance

            #sol2Remove = dict()
            #sol2Remove['solutionId'] = self.fronts[-1][frontPos][0]['solutionId']
            #sol2Remove['workerId'] = self.fronts[-1][frontPos][0]['workerId']
            # self.log.print("COORDINATOR:::removing["+str(sol2Remove['solutionId'])+ " from " + str(sol2Remove['workerId']))


            popElementToRemove, posPopElement = self.getPopulationElementBySolutionId(fe.getSolutionId(),fe.getWorkerId())
            self.population.pop(posPopElement)

            toRemove.append(fe.getPopulationElement())
            #self.removeWorstSolutionFromFront(popElementToRemove)


        #        self.log.print("COORDINATOR:::all to remove" + str(toRemove))
        return (toRemove)

    def removeSolutionFromFrontByFrontIdAndPos(self, front:int, pos:int) -> None:
        self.fronts[front].pop(pos)
        if len(self.fronts[front])==0:
            self.fronts.pop(front)


    '''
    Remove one solution of the fronts. The removing process is performed under the assumption that the element to
    remove is the worst one, and consequently, it is placed in the last front. Thus, a reorganization of the fronts
    is not required.
    INPUTS: one the population Element from the list self.population. This popElement is a dictionary with the 
    workerId the solutionId and the solution (instance of the solution) 
    '''
    def removeWorstSolutionFromFront(self,popElement: PopulationElement) -> None:
        for i,front in enumerate(self.fronts):  #go through the fronts
            for j,frontElement in enumerate(front): #go through the solutions in a front. those front elements ara a duple of the populationElement and the croding distance
                if frontElement.getSolutionId()==popElement.getSolutionId() and frontElement.getWorkerId()==popElement.getWorkerId():
                   #when the solution to remove is found, the front element is removed
                   front.pop(j)
                   if len(front)==0:
                       #if the removed solution is the last one in the front, the front must be removed.
                       self.fronts.pop(i)
                   return
        #self.log.print("ERRORRRR: solution to remove from the front is not found")
        print("ERRORRRR: solution to remove from the front is not found")



    def calculateCuboid(self, sortedElements: List[dict], pos: int, front: List[FrontElement]) -> float:
        solMiddle = sortedElements[pos]
        if pos != 0: #check if the middle solution has the same values for all the objectives of the previous lower solution
            solPrev = sortedElements[pos - 1]
            if solMiddle['fitness'] == solPrev['fitness']:
                if front[solPrev['posInFront']].getSolution().fitness == front[solMiddle['posInFront']].getSolution().fitness:
                    return 0.0
        if pos != -1 and pos != (len(sortedElements)-1): #check if the middle solution has the same values for all the objectives of the next higher solution
            solNext = sortedElements[pos + 1]
            if solMiddle['fitness'] == solNext['fitness']:
                if front[solNext['posInFront']].getSolution().fitness == front[solMiddle['posInFront']].getSolution().fitness:
                    return 0.0
        if pos != 0 and pos != -1:
            return solNext['fitness'] - solPrev['fitness']
        elif pos == 0:   #the smallest and biggest elements have a crawding distance of the double distance with the only neighbourd they have
            return 2.0*(solNext['fitness'] - solMiddle['fitness'])
        elif pos == -1 or pos == (len(sortedElements)-1):   #the smallest and biggest elements have a crawding distance of the double distance with the only neighbourd they have
            return 2.0*(solMiddle['fitness'] - solPrev['fitness'])

    def calculateCrawdingDistance(self, front: List[FrontElement], numObjectives: int) -> None:
        for frontElement in front:
            frontElement.setCrowding(0.0) #all the crowding distances are initialized to 0
            #frontElement[1]=0.0
        if len(front)<3:
            return #if there are only 2, 1 or 0 elements in the front, the crowding distance is 0
        for objPos in range(numObjectives):
            listOfObjectivePosPair =list()
            for pos, frontElement in enumerate(front): #we create a structure to know the value of the fitness and the position in the front for the solution with this value
                fitnessValue =  frontElement.getSolution().fitness[objPos]
                objectivePosElement = dict()
                objectivePosElement['fitness']=fitnessValue
                objectivePosElement['posInFront']=pos
                listOfObjectivePosPair.append(objectivePosElement)
            sortedElements = sorted(listOfObjectivePosPair,key=lambda x:x['fitness'])
            minValue = sortedElements[0]['fitness']
            maxValue = sortedElements[-1]['fitness']
            normalizedDenominator=float(maxValue-minValue)
            if normalizedDenominator>0.0: #check normalizedDenominator bigger than 0.0
                #if the max and minimum value are equal, the crowding distance of all the elements is 0.0
                #if normalizeddenominator == 0.0 do nothing FOR THIS OBJECTIVE because all the crowding distances were initialized to 0.0 at the beginning of the function
                for thePair in sortedElements:
                    thePair['fitness']=float(float(thePair['fitness'])/float(normalizedDenominator))
                #assumption: there are more than 2 elements in the list, because it was checked at the beginning of the function
                for posPair in range(1,len(sortedElements)-1):
                    #crawdingIncrement = sortedElements[posPair + 1][0] - sortedElements[posPair - 1][0]
                    crawdingIncrement = self.calculateCuboid(sortedElements,posPair,front)
                    frontPos = sortedElements[posPair]['posInFront']
                    front[frontPos].setCrowding(front[frontPos].getCrowding() + crawdingIncrement)

                for posPair in [0,-1]:  #calculation of the crowding distances of the two extrem elements (the smallest and the highest)
                    #crawdingIncrement = 2*(sortedElements[posPair + 1][0] - sortedElements[posPair][0])
                    crawdingIncrement = self.calculateCuboid(sortedElements, posPair, front)
                    frontPos = sortedElements[posPair]['posInFront']
                    front[frontPos].setCrowding(front[frontPos].getCrowding() + crawdingIncrement)







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
    of this list are population elements, which are classes of PopulationElement with workerId, solutionId
    and PopuliatonElement (object instance).
    frontNumber: the current front to analyize the inclusion of the set of solutions
    '''
    def shiftSolutionsToHigherFronts(self, listOfMovingSolutions: List[PopulationElement] ,frontNumber: int) -> None:
        if self.getNumberOfFronts()<=frontNumber: #if we have already analized all the previous fronts, we need to create a new front to include the current moving/shifted solutions. Those solutions are the ones that are not included in previous fronts.
            newFront = self.addFront(listOfMovingSolutions)
            self.calculateCrawdingDistance(newFront, self.objectivesNumber)
            return #no more fronts require to be analyzed.
        currentFront = self.getFrontByNumber(frontNumber)
        newShiftedSolutions = list() # the set of solutions that will be moved/shifted to higher fronts
        recalculateCrawding = False
        for newSolution in listOfMovingSolutions: #for all the solutions in the parameter of solution lists to evaluate where to be placed in the fronts
            solInstanceInMovingList = newSolution.getSolution()
            dominatedSolutions = list()
            for i,frontElement in enumerate(currentFront):  #searching the solutions that are dominated by the newsolution in the current from
                solInstanceInFront = frontElement.getSolution()
                if solInstanceInMovingList.dominatesTo(solInstanceInFront):
                    dominatedSolutions.append(i)
            if len(dominatedSolutions) > 0:
                recalculateCrawding = True
            dominatedSolutions.sort(reverse=True)#the elements in a list has to be removed in descending order, if not, the indexes change as the elements are removed
            for pos in dominatedSolutions: #all the dominated solutions are removed from the front and shifted to the higher front
                newShiftedSolutions.append(currentFront[pos].getPopulationElement())
                currentFront.pop(pos)
            isNewSolutionDominatedbySomeOne = False
            for i,frontElement in enumerate(currentFront): #we check if the new solution is dominated by someone
                solInstanceInFront = frontElement.getSolution()
                if solInstanceInFront.dominatesTo(solInstanceInMovingList):
                    isNewSolutionDominatedbySomeOne = True #we found that at least one solutin in the front dominates the new solution
                    break
            if isNewSolutionDominatedbySomeOne:
                newShiftedSolutions.append(newSolution) #if it is dominated by some solution in the front, the new solutions is pass through to a higher front
            else:
                self.addElement2Front(newSolution,frontNumber) #if no other solution dominates the new one, it is included in the front.
                recalculateCrawding = True

        if recalculateCrawding: #if some solutions are removed from this front and shifted to higher fronts, or if any of the new solution is included in the front we need to recalculate crawding distances
            self.calculateCrawdingDistance(currentFront, self.objectivesNumber)

        if len(newShiftedSolutions)>0: #if there is still solutions to place into the fronts, the function is recursevilly called to the next higher front
            self.shiftSolutionsToHigherFronts(newShiftedSolutions,frontNumber+1)


    def getRandomSolutions(self,numberOfSolutions: int) -> List[PopulationElement]:
        #idsList = random.sample(range(0, len(self.population)),
        #                                               numberOfSolutions)  # two solution are randomly selected
        idsList = self.randomNG.choice(len(self.population), numberOfSolutions, replace=False).tolist()
        solutionList = list()
        for i in idsList:
            solutionList.append(self.population[i])
        return solutionList

    def chooseBetter(self, pe1: PopulationElement, pe2: PopulationElement) -> PopulationElement:
        frontNumber1, crowding1 = self.getFrontCrowdingBySolId(pe1.getWorkerId(),
                                                       pe1.getSolutionId())
        frontNumber2, crowding2 = self.getFrontCrowdingBySolId(pe2.getWorkerId(),
                                                       pe2.getSolutionId())
        # the best solution is returned. The best is the one in the lowest front, and if they are in the same front, the one with the highest crowding distance
        if frontNumber1 > frontNumber2:
            return pe1
        elif frontNumber2 > frontNumber1:
            return pe2
        elif frontNumber1 == frontNumber2:
            if crowding1 > crowding2:
                return pe1
            else:
                return pe2
        else:
            return 0  # error, not comparable fronts




    def getFrontByNumber(self,frontNumber: int) -> List[FrontElement]:
        return self.fronts[frontNumber]

    def getNumberOfFronts(self) -> int:
        return len(self.fronts)

    def getSolutionByFrontAndPos(self, frontId: int, frontElementId: int) -> Solution:
        return self.fronts[frontId][frontElementId].getSolution()

    def addFront(self, listOfSolutions: List[PopulationElement]) -> List[FrontElement]:
        newFront = list()
        for newSolution in listOfSolutions:
            fe = FrontElement(newSolution, 0.0)  # the front element is a class with the population element and the crowding distance
            newFront.append(fe)
        self.fronts.append(newFront)
        return newFront

    def addElement2Front(self, newSolution: PopulationElement, frontNumber: int) -> List[FrontElement]:
        currentFront = self.getFrontByNumber(frontNumber)
        fe = FrontElement(newSolution, 0.0)
        currentFront.append(fe)
        return currentFront

    def getFrontElementWithSmallestCrowdingInFront(self, frontNumber: int) -> Tuple[FrontElement,int]:
        feSmallestCrowding = None
        pos_fe = -1
        valueSmallest = float('inf')
        #if two elements solutions have the same crowding, we select the first in the list, that is the one
        #that was generated before. Consequently, we increase the probability to replace old solutions with newest
        #solutions, in the case with the same crowding.
        for i,fe in enumerate(self.fronts[frontNumber]):
            if fe.getCrowding()<valueSmallest:
                valueSmallest = fe.getCrowding()
                feSmallestCrowding = fe
                pos_fe = i
        return feSmallestCrowding, pos_fe


    def getPopulationElementBySolutionId(self, solId:int, workerId: str)-> Tuple[PopulationElement, int]:
        for i, pe in enumerate(self.population):
            if pe.getSolutionId() == solId and pe.getWorkerId() == workerId:
                return pe, i
        return None, None

    '''
    This function returns a list/dictionary structure with the fitnesses of the solutions. This structure
    can be serialized into a json file
    INPUTS: If a population is included as parameter, we serialized the input populaiton, if not, 
    self.populuation is serialized
    '''
    def fitness2json(self, pop: List[PopulationElement] =None) -> List[dict]:
        # If a population is included as parameter, we serialized the input populaiton, if not, self.populuation is serialized
        if pop==None:
            population = self.population
        else:
            population = pop

        #a dictionary structure is create where id is the solutionId and fitness is the array with all the fitness values of the objectives
        setOfSolutions = list()
        for sol in population:
            oneSolution = dict()
            oneSolution['id']=sol.getSolutionId()
            oneSolution['fitness']=list(sol.getSolution().getFitness())
            setOfSolutions.append(oneSolution)
        return setOfSolutions

    def getFitnessInFronts2List(self) -> list:
        fitFronts = list()
        for i, front in enumerate(self.fronts):
            oneFront = list()
            for fe in front:
                oneFront.append(fe.getSolution().getFitness())
            fitFronts.append(oneFront)
        return fitFronts

    def getSolDistributionInWorkers(self) -> dict:
        #TODO  check if correct
        #devolver una distribucion de soluciones entre los workers. num de  workers con 1 solution, num de workers con
        #dos soluciones, etc... y lo mismo con el pareto. Asi veremos la distribucion de las soluciones entre los workers

        #calculate the density function of number of solutions in workers
        theWorkersInAll = list()
        for i, front in enumerate(self.fronts):
            for fe in front:
                theWorkersInAll.append(fe.getWorkerId())
        countInEachWorker = Counter(theWorkersInAll) #count how many solutions in each workerId
        countsValues=list(countInEachWorker.values()) #get the list of the number of solutions
        distributionOfCountValues = Counter(countsValues) #count how many workers has the same quantity of solutions

        #calculate the density functino of number of pareto's solutions in workers
        theWorkersInPareto = list()
        front=self.fronts[0]
        for fe in front:
            theWorkersInPareto.append(fe.getWorkerId())
        countInEachWorkerPareto = Counter(theWorkersInPareto)  # count how many solutions in each workerId
        countsValuesPareto = list(countInEachWorkerPareto.values())  # get the list of the number of solutions
        distributionOfCountValuesPareto = Counter(countsValuesPareto)  # count how many workers has the same quantity of solutions

        totalValues = dict()
        totalValues['front']=dict(distributionOfCountValues)
        totalValues['pareto']=dict(distributionOfCountValuesPareto)

        print(totalValues)
        return totalValues





    def serializeFronts(self) -> str:
        returnedStr  = ''
        for i, front in enumerate(self.fronts):
            returnedStr += 'FRONT NUMBER: ' + str(i) + '\n'
            for fe in front:
                theFitness = fe.getSolution().getFitness()
                theCrowdingDistance = fe.getCrowding()
                theSolId = fe.getSolutionId()
                theWorkerId = fe.getWorkerId()
                returnedStr  += '---- fitness('+str(theWorkerId)+'-'+str(theSolId)+'): ' + str(theFitness) + '\t\tcrowding distance: ' + str(theCrowdingDistance) + '\n'
        return returnedStr

    '''
    The input is a lists of solutions that has to be pre-included in the self.population by only generating the 
    populationElement instance and by adding the solutionID
    '''
    def createSubPopulation(self, solutions: List[Solution], workerId: str):
        offspring = list()
        for sol in solutions:
            pe = PopulationElement(workerId, self.solutionId, sol)
            self.solutionId = self.solutionId + 1
            offspring.append(pe)

        return offspring

