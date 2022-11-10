#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 18:41:41 2022

@author: carlos
"""

import os
import typing
import pickle


class Log:


    logLevels4File = ['testing','coordinator','operation','operation-details','mqtt-details','worker','dump-population']
    logLevels4Screen = ['testing','coordinator','operation','operation-details','mqtt-details','worker','dump-population']
    logLevels4Screen = ['coordinator','worker','dump-population']
    logLevels4File = ['coordinator','worker','dump-population']

    frontsFileName='fronts.pkl'

    def __init__(self,logname: str, messageHeader: str, executionId: str) -> None:
        self.logname = logname
        self.messageHeader = messageHeader
        self.executionId = executionId
        self.logPath = './logs/'+self.executionId+'/'
        self.resultsPath = './results/'+self.executionId+'/'
        if not os.path.exists(self.logPath):
            os.mkdir(self.logPath)


    def printf(self, str2Print: str, f: typing.TextIO, level: str = None) -> None:
        if level == None or level in self.logLevels4File:
            f.write(self.messageHeader + str2Print + '\n')
        if level == None or level in self.logLevels4Screen:
            print(self.messageHeader + str2Print)

    def print(self, str2Print: str,level: str = None) -> None:

        if level==None or level in self.logLevels4File:
            f = open (self.logPath+self.logname+'.txt','a')
            f.write(self.messageHeader+str2Print+'\n')
            f.close()
        if level==None or level in self.logLevels4Screen:
            print(self.messageHeader+str2Print)


    def dumpData(self,strData: str, level: str = None) -> None:
        f = open(self.logPath + self.logname + '.txt', 'a')
        self.printf(strData, f, level)
        f.close()


    def initializeDumpFronts(self) -> None:
        if not os.path.exists(self.resultsPath):
            os.mkdir(self.resultsPath)
        list2store = []
        with open(self.resultsPath + self.frontsFileName, 'wb') as f:
            [pickle.dump(elementList, f) for elementList in list2store]
        f.close()

    def dumpFronts(self,step: int, fronts2Store: list, distInWorkers: dict) -> None:
        #TODO   https://stackoverflow.com/questions/28077573/python-appending-to-a-pickled-list
        with open(self.resultsPath + self.frontsFileName, 'ab') as f:
            pickle.dump((step, fronts2Store, distInWorkers), f)
        f.close()
