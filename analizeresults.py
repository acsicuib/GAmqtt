#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 09:18:21 2022

@author: carlos
"""

import pickle
import matplotlib.pyplot as plt
import os
import numpy as np
import solutionConfig


global markers4Experiment

markers4Experiment = {}
#markers = ["." , "," , "o" , "v" , "^" , "<", ">"]
markers4Experiment["fullMigration"]="o"
markers4Experiment["fullOnlyNeighbours"]=","
markers4Experiment["traditionalNSGA"]="*"
markers4Experiment["centralizedNSGA"]="x"
markers4Experiment["fullydistributed"]="o"
markers4Experiment["neighboraware"]=","
markers4Experiment["traditionalNSGA"]="*"
markers4Experiment["semidistributed"]="x"


journalLabels = {}
#markers = ["." , "," , "o" , "v" , "^" , "<", ">"]
journalLabels["fullMigration"]="Fully-distributed"
journalLabels["fullydistributed"]="Fully-distributed"
journalLabels["fullOnlyNeighbours"]="Neighbor-aware"
journalLabels["neighboraware"]="Neighbor-aware"
journalLabels["traditionalNSGA"]="Traditional"
journalLabels["centralizedNSGA"]="Semi-distributed"
journalLabels["semidistributed"]="Semi-distributed"
journalLabels["semidistributed-pathLengthIslands"]="__noShow__"
journalLabels["semidistributed-pathLengthCentralizedFront"]="Semi-distributed"


#this function cut all the lists in the list to the size of the smallest one.
#this is necessary to use the np accumulative functions.
# def homogenizeTheSizeOfTheListToTheSmallestOne(listOfLists: list) -> list:
#
#     newListOfLists = []
#     smallestLength = float('inf')
#     for mylist in listOfLists:
#         smallestLength=min(smallestLength,len(mylist))
#     for mylist in listOfLists:
#         newListOfLists.append(mylist[:smallestLength])
#     return newListOfLists

def plotEvolutionPathLength(pathLengthByExperiments: dict , targetDir: str, myXlimit:int) -> None:
    global meanValuesByExperiment
    global accumulativeMeanValuesByExperiment
    global journalLabels

    # meanValuesByExperiment = {}
    # accumulativeMeanValuesByExperiment = {}
    # for experimentName, listOfLengthLists in pathLengthByExperiments.items():
    #     # listOfLengthLists = homogenizeTheSizeOfTheListToTheSmallestOne(listOfLengthLists)
    #     arrays =dnp.array(x) for x in listOfLengthLists]
    #     meanValuesByExperiment[experimentName] = [np.mean(k) for k in zip(*arrays)]
    #     accumulativeMeanValuesByExperiment[experimentName] = np.cumsum(meanValuesByExperiment[experimentName]).tolist()


    meanValuesByExperiment = {}
    arrayname, arraycum, arraymean, arraystd = [], [],[],[]

    accumulativeMeanValuesByExperiment = {}
    for experimentName, listOfLengthLists in pathLengthByExperiments.items():
        #listOfLengthLists = homogenizeTheSizeOfTheListToTheSmallestOne(listOfLengthLists)
        if not experimentName == "semidistributed-pathLengthIslands":
            arrays = np.array([np.array(x[:myXlimit]) for x in listOfLengthLists])
            ac = np.cumsum(arrays, axis=1)
            arraycum.append(ac)
            arraymean.append(np.mean(ac, axis=0))
            arraystd.append(np.std(ac, axis=0))
            arrayname.append(experimentName)

            meanValuesByExperiment[experimentName] = [np.mean(k) for k in zip(*arrays)]
            accumulativeMeanValuesByExperiment[experimentName] = np.cumsum(meanValuesByExperiment[experimentName]).tolist()

    color = np.array(plt.cm.plasma(np.linspace(0, 1,len(arrayname))))


    fig, ax = plt.subplots()
    for idx in range(len(arrayname)):
        for j in range(arraycum[idx].shape[0]):
            plt.plot(arraycum[idx][j], color='gray', label='_nolegend_',alpha=0.3)
        plt.plot(arraymean[idx],  color=color[idx], label=journalLabels[arrayname[idx]])
        if (arrayname[idx]=='fullydistributed'):
            textshifted=-18000
        if (arrayname[idx]=='neighboraware'):
            textshifted=17000
        if (arrayname[idx]=='semidistributed-pathLengthCentralizedFront'):
            textshifted=28000
        #plt.text(myXlimit, arraymean[idx][-1] - textshifted, "$\overline{hops}$", ha='right')
        plt.text(myXlimit, arraymean[idx][-1]-(textshifted+9000),  "$\overline{hops}=$"+str(round(arraymean[idx][-1]/myXlimit,3)),ha='right')
        plt.text(myXlimit, arraymean[idx][-1]-(textshifted+18000), "$\sigma$="+str(round(arraystd[idx][-1] / myXlimit, 3)),ha='right')


    #plt.title('Path evolution')
    plt.xlabel('Solution number')
    plt.ylabel('Accumulated network path distance (hops)')

    ax.legend()
    plt.savefig(targetDir+"pathEvolution2.pdf", format='pdf')
    plt.close()

    for idx in range(len(arrayname)):
        print(arrayname[idx])
        print(arraymean[idx][-1]/myXlimit)
        print(arraystd[idx][-1]/myXlimit)
        print("-"*20)


    # for experimentName, listOfLengthLists in pathLengthByExperiments.items():
    #     if not (experimentName == "centralizedNSGA-pathLengthIslands"):
    #         for i in listOfLengthLists:
    #             plt.plot(i[:myXlimit], color='gray', label='_nolegend_')


def plotFrontScatter(generationNumber: int, fronts: list, targetDir: str) -> None:

    global myXlabel
    global myYlabel

    color = list(iter(plt.cm.plasma(np.linspace(0, 1,len(fronts)))))


    fig, ax = plt.subplots()
    for idx,front in enumerate(fronts):
        plt.scatter([i[0] for i in front], [i[1] for i in front], color=color[idx], label="Front number: "+str(idx))
    # plt.scatter(oneIterationData['all_paretox'][i], oneIterationData['all_paretoy'][i])
    # plt.scatter(controlCases['ot1c'], controlCases['rt1c'], marker='x', color='g')
    # plt.scatter(controlCases['otCc'], controlCases['rtCc'], marker='x', color='r')
    # plt.scatter(oneIterationData['all_paretox'][i][indxMin], oneIterationData['all_paretoy'][i][indxMin], marker='*',
    #             color='#000000')

    plt.title('Objective space - generation '+str(generationNumber))
    plt.xlabel(myXlabel)
    plt.ylabel(myYlabel)

    ax.legend()
    plt.savefig(targetDir+"scaled_scatterPlot_GEN" + str(generationNumber) + ".pdf", format='pdf')
    plt.close()



def plotParetoEvolutionInScatter(allData: list, targetDir: str, mymarkersize: int, experimentName:str, lengedStep:int) -> None:

    global myXlabel
    global myYlabel

    import matplotlib.pyplot as plt
    import matplotlib as mpl

    color = iter(plt.cm.rainbow(np.linspace(0, 1,len(allData))))

    fig, ax = plt.subplots(1, 1, figsize=(8.4, 4.8))
    myalfa = 0.8
    for idx,execStep in enumerate(allData):
        lastPareto = execStep[1][0]
        #print(len(lastPareto))
        #print(lastPareto)
        # if (((idx+1) % lengedStep)==0) or idx==0:
        #     generationLabel="Generation: "+str(idx+1)
        # else:
        #     generationLabel='_nolegend_'
        #p1 = plt.scatter([i[0] for i in lastPareto], [i[1] for i in lastPareto], s=mymarkersize, marker=markers4Experiment[experimentName], color=next(color), alpha=myalfa, label=generationLabel)
        p1 = plt.scatter([i[0] for i in lastPareto], [i[1] for i in lastPareto], s=mymarkersize,
                     marker=markers4Experiment[experimentName], color=next(color), alpha=myalfa)
    cmap = mpl.cm.rainbow
#    norm = mpl.colors.Normalize(vmin=1, vmax=len(allData))
    norm = mpl.colors.Normalize(vmin=1, vmax=200)
    #fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='horizontal', label='Some Units')
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), label='generation number')
        #fig.colorbar(p1, label='generations')
        #myalfa -= 0.1
    # plt.scatter(oneIterationData['all_paretox'][i], oneIterationData['all_paretoy'][i])
    # plt.scatter(controlCases['ot1c'], controlCases['rt1c'], marker='x', color='g')
    # plt.scatter(controlCases['otCc'], controlCases['rtCc'], marker='x', color='r')
    # plt.scatter(oneIterationData['all_paretox'][i][indxMin], oneIterationData['all_paretoy'][i][indxMin], marker='*',
    #             color='#000000')

    #plt.title('Objective space - pareto evolution')
    plt.xlabel(myXlabel)
    plt.ylabel(myYlabel)

    ax.set_title(journalLabels[experimentName], loc= 'left', pad=-340)
    #ax.legend(loc='upper right')
    plt.savefig(targetDir+"paretoEvolution.pdf", format='pdf')
    plt.close()

def plotParetosGroupedByExperimentType(paretosByExperiments: dict, targetDir: str, fn: str, mymarkersize: int) -> None:

    global myXlabel
    global myYlabel
    global markers4Experiment

    color = iter(plt.cm.rainbow(np.linspace(0, 1,len(paretosByExperiments))))

    fig, ax = plt.subplots()
    myalfa = 0.6
    for experimentName, listOfParetos in paretosByExperiments.items():
        joinedParetos=list()
        for onePareto in listOfParetos:
            joinedParetos += onePareto
        #print(joinedParetos)
        plt.scatter([i[0] for i in joinedParetos], [i[1] for i in joinedParetos], s=mymarkersize, marker=markers4Experiment[experimentName], color=next(color), alpha=myalfa, label=journalLabels[experimentName])
        #myalfa -= 0.1

    #plt.title('Objective space - comparison of resulting paretos joined by experiment type')
    plt.xlabel(myXlabel)
    plt.ylabel(myYlabel)

    ax.legend()
    plt.savefig(targetDir+fn, format='pdf')
    plt.close()

def loadPathLengthData(pickleFileName: str) -> list:
    loadedData = []
    #print(pickleFileName)
    with open(pickleFileName, 'rb') as f:
        while True:
            try:
                nextData = pickle.load(f)
                #print("path"+str(nextData))
                loadedData.append(nextData)

            except EOFError:
                break
    f.close()
    return loadedData

def calculateFronts(listOfFronts: list) -> list:

    population = list()
    for oneFront in listOfFronts:
        population = population + oneFront

    n = len(population)
    fronts = [[]]
    dominators = [[] for i in range(n)]
    dominated_by = [0 for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if all(population[i][k] <= population[j][k] for k in range(2)):
                if any(population[i][k] < population[j][k] for k in range(2)):
                    dominators[i].append(j)
                    dominated_by[j] += 1
            elif all(population[i][k] >= population[j][k] for k in range(2)):
                if any(population[i][k] > population[j][k] for k in range(2)):
                    dominators[j].append(i)
                    dominated_by[i] += 1
    for i in range(n):
        if dominated_by[i] == 0:
            fronts[0].append(population[i])
    i = 0
    while fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in dominators[population.index(p)]:
                dominated_by[q] -= 1
                if dominated_by[q] == 0:
                    next_front.append(population[q])
        i += 1
        fronts.append(next_front)
    return fronts[:-1]



def dump4pfevaluator(thePareto: list,algorithmName: str,algorithmRepetition: str,targetDir: str) -> None:

    dirStep = './'+targetDir+'/'
    if not os.path.exists(dirStep):
        os.mkdir(dirStep)
    dirStep += algorithmName +'/'
    if not os.path.exists(dirStep):
        os.mkdir(dirStep)
    dirStep += algorithmRepetition + '/'
    if not os.path.exists(dirStep):
        os.mkdir(dirStep)

    with open(dirStep+'100-50-100-results.csv', 'w') as targetFile:
        lineString = 'Obj1,Obj2'
        targetFile.write(lineString+'\n')
        for id, sol in enumerate(thePareto):
            lineString = str(sol[0])+','+str(sol[1])
            targetFile.write(lineString + '\n')
    targetFile.close()





if __name__ == '__main__':

    generateScatter4EachGeneration = False
    generateScatter4ParetoEvolution = True
    generateScatter4FinalParetoInAllExecutions = True
    generatePlot4PathLength = True


    if not os.path.exists('./plots/'):
        os.mkdir('./plots/')

    myXlabel = "$\overline{instances}$   ($o_1$ mean "+solutionConfig.objectivesFunctions[0][0].lower()+")"
    myYlabel = "$\overline{distances}$   ($o_2$ "+solutionConfig.objectivesFunctions[1][0].lower()+" in ms)"

    result_dir = './results/'
    with os.scandir(result_dir) as filesInDir:
        experiments_subdir = [oneFile.name for oneFile in filesInDir if oneFile.is_dir()]
    print(experiments_subdir)

    experimentRepetitionsNames = set([dirname.split("-")[0] for dirname in experiments_subdir])

    groupedLastParetoExperiments = {}
    groupedEvolutionPathLength = {}

    for expName in experimentRepetitionsNames:
        #create the structure to load (in the future) the last pareto of execution grouped by experiment type
        groupedLastParetoExperiments[expName] = list()
        #create the structure to load (in the future) the data for the path length
        if expName.startswith('semidistributed'):
            groupedEvolutionPathLength['semidistributed-pathLengthCentralizedFront'] = list()
            groupedEvolutionPathLength['semidistributed-pathLengthIslands'] = list()
        elif expName.startswith('traditionalNSGA'):
            pass
        else:
            groupedEvolutionPathLength[expName] = list()

    for oneExperimentDir in experiments_subdir:
        print("00: STARTING WITH EXPERIMENT "+oneExperimentDir)
        print("01: Loading data of the fronts for "+oneExperimentDir)
        if not os.path.exists('./plots/'+oneExperimentDir+'/'):
            os.mkdir('./plots/'+oneExperimentDir+'/')
        loadedData = []
        with open(result_dir+oneExperimentDir+'/fronts.pkl', 'rb') as f:
            while True:
                try:
                    #the data in the pickle file is a list that is loaded into loadedData
                    #each element of the list is a tuple of 3 elements. Each element of the list stores the data for a given generation.
                    #Not all the generations are stored, only some of them
                    # loadedData[n][0] --> stores an int that representes the number of solutions that has evolved until this point of the execution
                    #                      i.e., it correspond to the generation calculated as loadedData[n][0]/(sum of the numer of solutions in the workers)
                    # loadedData[n][1] --> stores a list of lists, that stores all the pareto fronts for that generation. the parte front is the one in [0]
                    # loadedData[n][1] --> stores the distribution of the solutions in the workers.
                    #                      it is a dictionary with two elements
                    #                      ['front'] a distionary where the lables are the number of solutions and the value how many workers has that number of solutions
                    #                                distribution of quantity of workers with a given number of solutions, for example, 12:3 there are 3 workers with 12 elements. and
                    #                      ['pareto'] equal to the previous one, but for the number of solutions in the pareto front
                    elementLoaded=pickle.load(f)
                    if oneExperimentDir.startswith('fullMigration') or oneExperimentDir.startswith('fullOnlyNeighbours'):
                        #in this two experiment executions, the pareto fronts are not calculated during execution
                        #thus, we need to calculate them in the result analysis
                        elementLoaded=(elementLoaded[0],calculateFronts(elementLoaded[1]),elementLoaded[2])
                    loadedData.append(elementLoaded)
                except EOFError:
                    break
        f.close()
        if generateScatter4EachGeneration:
            print("02: Starting generation of scatter plots for each generatio of"+oneExperimentDir)
            for executionStep in loadedData:
                plotFrontScatter(executionStep[0],executionStep[1],'./plots/'+oneExperimentDir+'/')
            print("03: End of generation of scatter plots for each generatio of" + oneExperimentDir)
        lastPareto = loadedData[-1][1][0] #we get the last executionstep (-1) the fronts (second element in the tuple, 1) the first front (0)
        pfevalDir='pfevaluator'
        dump4pfevaluator(lastPareto,oneExperimentDir.split("-")[0],oneExperimentDir.split("-")[1],pfevalDir)
        groupedLastParetoExperiments[oneExperimentDir.split("-")[0]].append(lastPareto)

        #print(oneExperimentDir)
        print("04: Loading data of the path length for " + oneExperimentDir)
        if oneExperimentDir.startswith('semidistributed'):
            # loadedData = []
            # print(result_dir + oneExperimentDir + '/pathLengthCentralizedFront.pkl')
            # with open(result_dir + oneExperimentDir + '/pathLengthCentralizedFront.pkl', 'rb') as f:
            #     while True:
            #         try:
            #             loadedData.append(pickle.load(f))
            #         except EOFError:
            #             break
            # f.close()
            fileName=result_dir + oneExperimentDir + '/pathLengthCentralizedFront.pkl'
            loadedDataPath = loadPathLengthData(fileName)
            groupedEvolutionPathLength['semidistributed-pathLengthCentralizedFront'].append(loadedDataPath)
            fileName=result_dir + oneExperimentDir + '/pathLengthIslands.pkl'
            loadedDataPath = loadPathLengthData(fileName)
            groupedEvolutionPathLength['semidistributed-pathLengthIslands'].append(loadedDataPath)
        elif oneExperimentDir.startswith('traditionalNSGA'):
            pass
        else:
            fileName=result_dir + oneExperimentDir + '/pathLength.pkl'
            loadedDataPath = loadPathLengthData(fileName)
            groupedEvolutionPathLength[oneExperimentDir.split("-")[0]].append(loadedDataPath)

        if generateScatter4ParetoEvolution:
            print("05: Starting generation of scatter plot for the evolution of the pareto front along the generations in " + oneExperimentDir)
            plotParetoEvolutionInScatter(loadedData,'./plots/'+oneExperimentDir+'/',5,oneExperimentDir.split("-")[0],20)
            print("06: End of generation of scatter plot for the evolution of the pareto front along the generations in " + oneExperimentDir)

    print("07: STARTING PLOTS FOR AGGREGATED RESULTS OF ALL THE EXPERIMENTS")
    if generateScatter4FinalParetoInAllExecutions:
        print("08: Starting the plot of all the final pareto fronts of all the experiments")
        plotParetosGroupedByExperimentType(groupedLastParetoExperiments, './plots/', "joinedParetos.pdf",2)
        print("09: End the plot of all the final pareto fronts of all the experiments")
        print("10: Starting the plot of the pareto obtained with the set of repetitions of all the final pareto fronts of all the experiments")
        uniqueGroupedLastParetoExperiments = {}
        for experimentType, paretosInRepetitions in groupedLastParetoExperiments.items():
            newPareto = calculateFronts(paretosInRepetitions)[0]
            uniqueGroupedLastParetoExperiments[experimentType] = list()
            uniqueGroupedLastParetoExperiments[experimentType].append(newPareto)
            dump4pfevaluator(newPareto, experimentType, 'referencePF', pfevalDir)
        plotParetosGroupedByExperimentType(uniqueGroupedLastParetoExperiments, './plots/', "joinedUniqueParetos.pdf",15)
        print("11: End the plot of the pareto obtained with the set of repetitions of all the final pareto fronts of all the experiments")

if generatePlot4PathLength:
        print("12: Starting the plot of all the path distances for all the experiments")
        plotEvolutionPathLength(groupedEvolutionPathLength,'./plots/',17500)
        print("13: Starting the plot of all the path distances for all the experiments")
