#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 09:18:21 2022

@author: carlos
"""

import pickle
import matplotlib.pyplot as plt
import os
from matplotlib.pyplot import cm
import numpy as np
import solutionConfig


def plotFrontScatter(generationNumber: int, fronts: list, destinyDir: str) -> None:

    global myXlabel
    global myYlabel

    color = iter(cm.plasma(np.linspace(0, 1,len(fronts))))

    fig, ax = plt.subplots()
    for idx,front in enumerate(fronts):
        plt.scatter([i[0] for i in front], [i[1] for i in front], c=next(color), label="Front number: "+str(idx))
    # plt.scatter(oneIterationData['all_paretox'][i], oneIterationData['all_paretoy'][i])
    # plt.scatter(controlCases['ot1c'], controlCases['rt1c'], marker='x', color='g')
    # plt.scatter(controlCases['otCc'], controlCases['rtCc'], marker='x', color='r')
    # plt.scatter(oneIterationData['all_paretox'][i][indxMin], oneIterationData['all_paretoy'][i][indxMin], marker='*',
    #             color='#000000')

    plt.title('Objective space - generation '+str(generationNumber))
    plt.xlabel(myXlabel)
    plt.ylabel(myYlabel)

    ax.legend()
    plt.savefig(destinyDir+"scaled_scatterPlot_GEN" + str(generationNumber) + ".pdf", format='pdf')
    plt.close()



def plotParetoEvolutionInScatter(allData: list, destinyDir: str) -> None:

    global myXlabel
    global myYlabel

    color = iter(cm.rainbow(np.linspace(0, 1,len(allData))))

    fig, ax = plt.subplots()
    myalfa = 0.8
    for idx,execStep in enumerate(allData):
        lastPareto = execStep[1][0]
        print(len(lastPareto))
        print(lastPareto)
        plt.scatter([i[0] for i in lastPareto], [i[1] for i in lastPareto], c=next(color), alpha=myalfa, label="Generation: "+str(idx))
        #myalfa -= 0.1
    # plt.scatter(oneIterationData['all_paretox'][i], oneIterationData['all_paretoy'][i])
    # plt.scatter(controlCases['ot1c'], controlCases['rt1c'], marker='x', color='g')
    # plt.scatter(controlCases['otCc'], controlCases['rtCc'], marker='x', color='r')
    # plt.scatter(oneIterationData['all_paretox'][i][indxMin], oneIterationData['all_paretoy'][i][indxMin], marker='*',
    #             color='#000000')

    plt.title('Objective space - pareto evolution')
    plt.xlabel(myXlabel)
    plt.ylabel(myYlabel)

    ax.legend()
    plt.savefig(destinyDir+"paretoEvolution.pdf", format='pdf')
    plt.close()

def plotParetosGroupedByExperimentType(paretosByExperiments: dict, destinyDir: str) -> None:

    global myXlabel
    global myYlabel

    color = iter(cm.rainbow(np.linspace(0, 1,len(paretosByExperiments))))

    fig, ax = plt.subplots()
    myalfa = 0.6
    for experimentName, listOfParetos in paretosByExperiments.items():
        joinedParetos=list()
        for onePareto in listOfParetos:
            joinedParetos += onePareto
        print(joinedParetos)
        plt.scatter([i[0] for i in joinedParetos], [i[1] for i in joinedParetos], c=next(color), alpha=myalfa, label=experimentName)
        #myalfa -= 0.1

    plt.title('Objective space - comparison of resulting paretos joined by experiment type')
    plt.xlabel(myXlabel)
    plt.ylabel(myYlabel)

    ax.legend()
    plt.savefig(destinyDir+"joinedParetos.pdf", format='pdf')
    plt.close()


if __name__ == '__main__':

    if not os.path.exists('./plots/'):
        os.mkdir('./plots/')

    myXlabel = solutionConfig.objectivesFunctions[0][0]
    myYlabel = solutionConfig.objectivesFunctions[1][0]

    result_dir = './results/'
    with os.scandir(result_dir) as filesInDir:
        experiments_subdir = [oneFile.name for oneFile in filesInDir if oneFile.is_dir()]
    print(experiments_subdir)

    experimentRepetitionsNames = set([dirname.split("-")[0] for dirname in experiments_subdir])

    groupedLastParetoExperiments = {}
    for expName in experimentRepetitionsNames:
        groupedLastParetoExperiments[expName] = list()

    for oneExperimentDir in experiments_subdir:
        if not os.path.exists('./plots/'+oneExperimentDir+'/'):
            os.mkdir('./plots/'+oneExperimentDir+'/')
        loadedData = []
        with open('./results/'+oneExperimentDir+'/fronts.pkl', 'rb') as f:
            while True:
                try:
                    loadedData.append(pickle.load(f))
                except EOFError:
                    break
        f.close()

        #for executionStep in loadedData:
            #plotFrontScatter(executionStep[0],executionStep[1],'./plots/'+oneExperimentDir+'/')
        lastPareto = loadedData[-1][1][0] #we get the last executionstep (-1) the fronts (second element in the tuple, 1) the first front (0)
        groupedLastParetoExperiments[oneExperimentDir.split("-")[0]].append(lastPareto)

        plotParetoEvolutionInScatter(loadedData,'./plots/'+oneExperimentDir+'/')

    plotParetosGroupedByExperimentType(groupedLastParetoExperiments,'./plots/')