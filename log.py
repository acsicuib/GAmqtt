#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 18:41:41 2022

@author: carlos
"""

import os


class Log:


    logLevels4File = ['testing','coordinator','operation','operation-details','mqtt-details','worker','dump-population']
    logLevels4Screen = ['testing','coordinator','operation','operation-details','mqtt-details','worker','dump-population']
    logLevels4Screen = ['coordinator','worker','dump-population']
    logLevels4File = ['coordinator','worker','dump-population']

    def __init__(self,logname,messageHeader):
        self.logname = logname
        self.messageHeader = messageHeader
        if not os.path.exists('./logs/'):
            os.mkdir('./logs/')


    def printf(self,str,f,level=None):
        if level == None or level in self.logLevels4File:
            f.write(self.messageHeader + str + '\n')
        if level == None or level in self.logLevels4Screen:
            print(self.messageHeader + str)

    def print(self,str,level=None):

        if level==None or level in self.logLevels4File:
            f = open ('./logs/'+self.logname+'.txt','w')
            f.write(self.messageHeader+str+'\n')
            f.close()
        if level==None or level in self.logLevels4Screen:
            print(self.messageHeader+str)


    def dumpFronts(self,fronts,level=None):
        f = open('./logs/' + self.logname + '.txt', 'w')

        for i,front in enumerate(fronts):
            self.printf('FRONT NUMBER: '+str(i),f,level)
            for element in front:
                self.print('---- fitness: '+str(element[0]['solution'].fitness)+'\t\tcrowding distance: '+str(element[1]),level)

        f.close()
