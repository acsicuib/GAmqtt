#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:58:58 2018

@author: carlos
"""

import networkx as nx
import random
import operator
import json
import numpy
import os
import optimizationConfig as optCnf
from typing import Set


class Infrastructure:

    def __init__(self, strFolder: str = None) -> None:
        if isinstance(strFolder,str):
            self.storageFolder = strFolder
        else:
            self.storageFolder = './json4Infrastructure/'
        if not os.path.exists(self.storageFolder):
            os.mkdir(self.storageFolder)

        #https://networkx.org/documentation/stable/reference/randomness.html
        if optCnf.randomReproducible4Infrastructure:
            self.myRnd = numpy.random.RandomState(optCnf.randomSeed4Infrastructure)
        else:
            self.myRnd = numpy.random.RandomState()

    #****************************************************************************************************
    #Generacion de la topologia de red
    #****************************************************************************************************
    def createNetwork(self, save2Files: bool) -> None:

        self.G = eval(self.func_NETWORKGENERATION)
        self.Gfdev=self.G.copy()
        self.devices = list()

        #A resource capacity is randomly assigned to each node
        self.nodeResources = {}
        self.nodeFreeResources = {}
        for i in self.G.nodes:
            self.nodeResources[i]=eval(self.func_NODERESOURECES)
            self.nodeFreeResources[i] = self.nodeResources[i]

        #A random network features is assigned to each network edge
        for e in self.G.edges:
            self.G[e[0]][e[1]]['PR']=eval(self.func_PROPAGATIONTIME)
            self.G[e[0]][e[1]]['BW']=eval(self.func_BANDWITDH)
            self.Gfdev[e[0]][e[1]]['PR'] = self.G[e[0]][e[1]]['PR']
            self.Gfdev[e[0]][e[1]]['BW'] = self.G[e[0]][e[1]]['BW']

        netJson={}

        for i in self.G.nodes:
            myNode ={}
            myNode['id']=i
            myNode['RAM']=self.nodeResources[i]
            myNode['HD']=1
            myNode['IPT']=1
            self.devices.append(myNode)

        myEdges = list()
        for e in self.G.edges:
            myLink={}
            myLink['s']=e[0]
            myLink['d']=e[1]
            myLink['PR']=self.G[e[0]][e[1]]['PR']
            myLink['BW']=self.G[e[0]][e[1]]['BW']

            myEdges.append(myLink)

        #TODO, debería de estar con weight='weight' ??????

        #the centrality value is used to choose the nodes connected to the cloud (highest centrality) and
        #the nodes where the clients are connected to (lowest centrality)
        #gatewaysDevices is the set of devices where user can be connected to
        #and cloudgatewaysDevices is the set of devices that has the highest centrality (usually one device)

        #centralityValuesNoOrdered = nx.betweenness_centrality(G,weight="weight",seed=2022)
        centralityValuesNoOrdered = nx.betweenness_centrality(self.G,weight="weight",seed=self.myRnd)
        centralityValues=sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

        self.gatewaysDevices = set()
        self.cloudgatewaysDevices = set()

        highestCentrality = centralityValues[0][1]

        for device in centralityValues:
            if device[1]==highestCentrality:
                self.cloudgatewaysDevices.add(device[0])

        #centralityValues has the nodes ordered from the higher centrality to the lowest
        #to choose the edges devices (gateways) the structure is iterated only in the percentatge
        #number of devices at the end of the list
        initialIndx = int((1-self.PERCENTATGEOFGATEWAYS)*len(self.G.nodes))  #Indice del final para los X tanto por ciento nodos

        for idDev in range(initialIndx,len(self.G.nodes)):
            self.gatewaysDevices.add(centralityValues[idDev][0])

        #the cloud node is generated and connected to all the fog devices with the highest centrality values.
        self.cloudId = len(self.G.nodes)
        myNode ={}
        myNode['id']=self.cloudId
        myNode['RAM']=self.CLOUDCAPACITY
        myNode['HD']=1
        myNode['IPT']=1
        myNode['type']='CLOUD'
        self.devices.append(myNode)

        self.G.add_node(self.cloudId)

        for cloudGtw in self.cloudgatewaysDevices:
            myLink={}
            myLink['s']=cloudGtw
            myLink['d']=self.cloudId
            myLink['PR']=self.CLOUDPR
            myLink['BW']=self.CLOUDBW

            self.G.add_edge(self.cloudId,cloudGtw)
            self.G[self.cloudId][cloudGtw]['PR']=self.CLOUDPR
            self.G[self.cloudId][cloudGtw]['BW']=self.CLOUDBW

            myEdges.append(myLink)

        netJson['entity']=self.devices
        netJson['link']=myEdges


        if save2Files:
            #JSON EXPORT
            file = open(self.storageFolder+"network.json","w")
            file.write(json.dumps(netJson))
            file.close()

    def setConfiguration(self,nameInfr: str, numNodes: int = None, numServices: int = None, netGenerator: str = None) -> None:

        if nameInfr == 'newage':

            #CLOUD
            self.CLOUDCAPACITY = 9999999999999999  #MB RAM
            self.CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
            self.CLOUDPR = 1 # MS


            #NETWORK
            self.PERCENTATGEOFGATEWAYS = 0.25
            self.TOTALNUMBEROFNODES = 17
            self.func_PROPAGATIONTIME = "self.myRnd.randint(1,5)" #MS
            self.func_BANDWITDH = "self.myRnd.randint(50000,75000)" # BYTES / MS
            #func_NETWORKGENERATION = "nx.barabasi_albert_graph(seed=2022,n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
            self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(self.TOTALNUMBEROFNODES)+", m=2, seed=self.myRnd)" #algorithm for the generation of the network topology
            self.func_NODERESOURECES = "self.myRnd.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
            self.func_NODERESOURECES = "self.myRnd.randint(10,15)" #MB RAM #random distribution for the resources of the fog devices


            #APSS
            self.TOTALNUMBEROFAPPS = 5
            self.func_APPMESSAGESIZE = "self.myRnd.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
            self.func_APPRESOURCES = "self.myRnd.randint(1,6)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
            self.func_SERVICEINSTR = "self.myRnd.randint(400000,600000)"
            self.func_SERVICEINSTR = "4"

            #USERS and IoT DEVICES
            #func_REQUESTPROB="self.myRnd.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
            self.func_REQUESTPROB="self.myRnd.random()/2" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
            self.func_USERREQRAT="self.myRnd.randint(200,1000)"  #MS

        elif nameInfr == "toguapho":
            #CLOUD
            self.CLOUDCAPACITY = 9999999999999999  #MB RAM
            self.CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
            self.CLOUDPR = 1 # MS


            #NETWORK
            self.PERCENTATGEOFGATEWAYS = 0.25
            self.TOTALNUMBEROFNODES = 200
            self.func_PROPAGATIONTIME = "self.myRnd.randint(1,5)" #MS
            self.func_BANDWITDH = "self.myRnd.randint(50000,75000)" # BYTES / MS
            #func_NETWORKGENERATION = "nx.barabasi_albert_graph(seed=2022,n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
            self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(self.TOTALNUMBEROFNODES)+", m=2, seed=self.myRnd)" #algorithm for the generation of the network topology
            #func_NODERESOURECES = "self.myRnd.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
            self.func_NODERESOURECES = "self.myRnd.randint(10,15)" #MB RAM #random distribution for the resources of the fog devices

            #APSS
            self.TOTALNUMBEROFAPPS = 20
            self.func_APPMESSAGESIZE = "self.myRnd.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
            self.func_APPRESOURCES = "self.myRnd.randint(1,6)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
            self.func_SERVICEINSTR = "self.myRnd.randint(400000,600000)"


            #USERS and IoT DEVICES
            #func_REQUESTPROB="self.myRnd.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
            self.func_REQUESTPROB="3*self.myRnd.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
            self.func_USERREQRAT="self.myRnd.randint(200,1000)"  #MS



        elif nameInfr == "journal":
            #CLOUD
            self.CLOUDCAPACITY = 9999999999999999  #MB RAM
            self.CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
            self.CLOUDPR = 100 # MS


            #NETWORK
            self.PERCENTATGEOFGATEWAYS = 0.25
            self.TOTALNUMBEROFNODES = 200
            self.func_PROPAGATIONTIME = "self.myRnd.randint(2,6)" #MS
            self.func_BANDWITDH = "self.myRnd.randint(50000,75000)" # BYTES / MS
            #func_NETWORKGENERATION = "nx.barabasi_albert_graph(seed=2022,n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
            self.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(self.TOTALNUMBEROFNODES)+", m=2, seed=self.myRnd)" #algorithm for the generation of the network topology
            #func_NODERESOURECES = "self.myRnd.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
            self.func_NODERESOURECES = "self.myRnd.randint(1,4)" #MB RAM #random distribution for the resources of the fog devices

            #APSS
            self.TOTALNUMBEROFAPPS = 20
            self.func_APPMESSAGESIZE = "self.myRnd.randint(100,20000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
            self.func_APPRESOURCES = "self.myRnd.randint(1,2)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
            self.func_SERVICEINSTR = "self.myRnd.randint(1000,3500)"


            #USERS and IoT DEVICES
            #func_REQUESTPROB="self.myRnd.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
            self.func_REQUESTPROB="3*self.myRnd.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
            self.func_USERREQRAT="self.myRnd.randint(5,10)"  #MS

        else:
            print("ERROR: infrastructure configuration not defined")
            return

        if (isinstance(numNodes,int)):
            self.TOTALNUMBEROFNODES = numNodes
        if (isinstance(numServices, int)):
            self.TOTALNUMBEROFAPPS = numServices
        if (isinstance(netGenerator, str)):
            seededNetGenerator = self.includeSeedParameter(netGenerator)
            self.func_NETWORKGENERATION = seededNetGenerator


    def includeSeedParameter(self, evalStr: str) -> None:
        return evalStr.replace(")",",seed=self.myRnd)")

    def deployScenario(self, save2Files: bool = False) -> None:
        self.createNetwork(save2Files)
        self.createApps(save2Files)
        self.createUsers(save2Files)

    def createApps(self, save2Files: bool) -> None:

        appJson=list()

        self.appsResources = [0 for j in range(self.TOTALNUMBEROFAPPS)]
        self.appsPacketsSize = [0 for j in range(self.TOTALNUMBEROFAPPS)]
        self.appsInstructions = [0 for j in range(self.TOTALNUMBEROFAPPS)]
        self.apps = [0 for j in range(self.TOTALNUMBEROFAPPS)]


        for j in range(0,self.TOTALNUMBEROFAPPS):
            self.appsResources[j]=eval(self.func_APPRESOURCES)
            self.appsPacketsSize[j]=eval(self.func_APPMESSAGESIZE)
            self.appsInstructions[j]=eval(self.func_SERVICEINSTR)
            self.apps[j]={}
            self.apps[j]['app']=j
            self.apps[j]['resources']=self.appsResources[j]
            self.apps[j]['packetsize']=self.appsPacketsSize[j]
            self.apps[j]['instructions']=self.appsInstructions[j]
            #all the lines below for json generation
            oneApp = {}
            oneApp['name']=str(j)
            oneApp['id']=0
            oneApp['deadline']=999999
            #adding modules
            oneApp['module']=list()
            moduleCoord ={}
            moduleCoord['RAM'] = 0
            moduleCoord['type'] = 'MANAGEMENT'
            moduleCoord['id'] = j*2
            moduleCoord['name'] = "C_"+str(j)
            oneApp['module'].append(moduleCoord)
            moduleApp ={}
            moduleApp['RAM'] = self.apps[j]['resources']
            moduleApp['type'] = 'APP'
            moduleApp['id'] = j*2+1
            moduleApp['name'] = "A_"+str(j)
            oneApp['module'].append(moduleApp)
            #adding transmissions
            oneApp['transmission']=list()
            transUserCoord ={}
            transUserCoord['message_out'] = 'MCA.'+str(j)
            transUserCoord['message_in'] = 'MUC.'+str(j)
            transUserCoord['module'] = "C_"+str(j)
            oneApp['transmission'].append(transUserCoord)
            transCoordApp ={}
            transCoordApp['message_in'] = 'MCA.'+str(j)
            transCoordApp['module'] = "A_"+str(j)
            oneApp['transmission'].append(transCoordApp)
            #adding messages
            oneApp['message']=list()
            messUserCoord ={}
            messUserCoord['name'] = 'MUC.'+str(j)
            messUserCoord['bytes'] = self.apps[j]['packetsize']
            messUserCoord['d'] = "C_"+str(j)
            messUserCoord['s'] = "None"
            messUserCoord['id'] = j*2
            messUserCoord['instructions'] = 0
            oneApp['message'].append(messUserCoord)
            messCoordApp ={}
            messCoordApp['name'] = 'MCA.'+str(j)
            messCoordApp['bytes'] = self.apps[j]['packetsize']
            messCoordApp['d'] = "A_"+str(j)
            messCoordApp['s'] = "C_"+str(j)
            messCoordApp['id'] = j*2+1
            messCoordApp['instructions'] = self.apps[j]['instructions']
            oneApp['message'].append(messCoordApp)

            appJson.append(oneApp)

        if save2Files:
            file = open(self.storageFolder+"appDefinition.json","w")
            file.write(json.dumps(appJson))
            file.close()




    def createUsers(self, save2Files: bool) -> None:
        #****************************************************************************************************
        #Generacion de los IoT devices (users) que requestean cada aplciacion
        #****************************************************************************************************

        userJson ={}

        self.myUsers=list()
        self.appsRequests = list()
        for i in range(0,self.TOTALNUMBEROFAPPS):
            userRequestList = set()
            probOfRequested = eval(self.func_REQUESTPROB)
            atLeastOneAllocated = False
            for j in self.gatewaysDevices:
                if self.myRnd.random()<probOfRequested:
                    myOneUser={}
                    myOneUser['app']=str(i)
                    myOneUser['message']="MUC."+str(i)
                    myOneUser['id_resource']=j
                    myOneUser['lambda']=eval(self.func_USERREQRAT)
                    userRequestList.add(j)
                    self.myUsers.append(myOneUser)
                    atLeastOneAllocated = True
            if not atLeastOneAllocated:
                j=self.myRnd.randint(0,len(self.gatewaysDevices)-1)
                myOneUser={}
                myOneUser['app']=str(i)
                myOneUser['message']="MUC."+str(i)
                myOneUser['id_resource']=j
                myOneUser['lambda']=eval(self.func_USERREQRAT)
                userRequestList.add(j)
                self.myUsers.append(myOneUser)
            self.appsRequests.append(userRequestList)

        userJson['sources']=self.myUsers

        if save2Files:
            file = open(self.storageFolder+"usersDefinition.json","w")
            file.write(json.dumps(userJson))
            file.close()

    def getEdgesDevices(self) -> Set[int]:
        return list(self.gatewaysDevices)

    def deviceDistances(self) -> dict:
        dist_ = nx.shortest_path_length(self.Gfdev)
        distances = {}
        for i in dist_:
            distances[i[0]] = i[1]
        return distances


if __name__ == '__main__':

    a = Infrastructure()
    a.setConfiguration("journal")
    a.deployScenario(False)