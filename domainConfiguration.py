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





# random.seed(8)
#random_state = numpy.random.RandomState(8)
verbose_log = False
generatePlots = True
graphicTerminal =True
myConfiguration_ = 'newage'
myConfiguration_ = "toguapho"
myConfiguration_ = "journal"
storageFolder = ''


def initializeRandom(seed_):
    random.seed(seed_)
    

def setRandomState(value):
    random_state = numpy.random.RandomState(value)

#****************************************************************************************************
#Generacion de la topologia de red
#****************************************************************************************************
def networkModel(filePrefix):
    
    #TOPOLOGY GENERATION
    
    global G
    global nodeResources
    global nodeFreeResources
    global devices
    global gatewaysDevices
    global cloudgatewaysDevices
    global cloudId
    global Gfdev
    
    
    
    G = eval(func_NETWORKGENERATION)
    #G = nx.barbell_graph(5, 1)
    # if graphicTerminal:
    #     nx.draw(G)
    #     #nx.draw_networkx_labels(G,pos=nx.spring_layout(G,seed=2022))
    #     nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    Gfdev=G.copy()
    
    devices = list()
    
    nodeResources = {}
    nodeFreeResources = {}
    for i in G.nodes:
        nodeResources[i]=eval(func_NODERESOURECES)
        nodeFreeResources[i] = nodeResources[i]
    
    for e in G.edges:
        G[e[0]][e[1]]['PR']=eval(func_PROPAGATIONTIME)
        G[e[0]][e[1]]['BW']=eval(func_BANDWITDH)
        
        Gfdev[e[0]][e[1]]['PR'] = G[e[0]][e[1]]['PR']
        Gfdev[e[0]][e[1]]['BW'] = G[e[0]][e[1]]['BW']
        
    
    
    #JSON EXPORT
    
    netJson={}
    
    
    for i in G.nodes:
        myNode ={}
        myNode['id']=i
        myNode['RAM']=nodeResources[i]
        myNode['HD']=1
        myNode['IPT']=1
        devices.append(myNode)
    
    
    
    
    myEdges = list()
    for e in G.edges:
        myLink={}
        myLink['s']=e[0]
        myLink['d']=e[1]
        myLink['PR']=G[e[0]][e[1]]['PR']
        myLink['BW']=G[e[0]][e[1]]['BW']
    
        myEdges.append(myLink)
    
    
    #TODO, debería de estar con weight='weight' ??????
    
    #the centrality value is used to choose the nodes connected to the cloud (highest centrality) and
    #the nodes where the clients are connected to (lowest centrality)
    #gatewaysDevices is the set of devices where user can be connected to
    #and cloudgatewaysDevices is the set of devices that has the highest centrality (usually one device)

    #centralityValuesNoOrdered = nx.betweenness_centrality(G,weight="weight",seed=2022)
    centralityValuesNoOrdered = nx.betweenness_centrality(G,weight="weight")
    centralityValues=sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)
    
    gatewaysDevices = set()
    cloudgatewaysDevices = set()
    
    highestCentrality = centralityValues[0][1]
    
    for device in centralityValues:
        if device[1]==highestCentrality:
            cloudgatewaysDevices.add(device[0])
    
    
    #centralityValues has the nodes ordered from the higher centrality to the lowest
    #to choose the edges devices (gateways) the structure is iterated only in the percentatge
    #number of devices at the end of the list
    initialIndx = int((1-PERCENTATGEOFGATEWAYS)*len(G.nodes))  #Indice del final para los X tanto por ciento nodos
    
    for idDev in range(initialIndx,len(G.nodes)):
        gatewaysDevices.add(centralityValues[idDev][0])
    
    

    
    
    cloudId = len(G.nodes)
    myNode ={}
    myNode['id']=cloudId
    myNode['RAM']=CLOUDCAPACITY
    myNode['HD']=1
    myNode['IPT']=1
    myNode['type']='CLOUD'
    devices.append(myNode)
    
    G.add_node(cloudId)
    
    for cloudGtw in cloudgatewaysDevices:
        myLink={}
        myLink['s']=cloudGtw
        myLink['d']=cloudId
        myLink['PR']=CLOUDPR
        myLink['BW']=CLOUDBW
        

        G.add_edge(cloudId,cloudGtw)
        G[cloudId][cloudGtw]['PR']=CLOUDPR
        G[cloudId][cloudGtw]['BW']=CLOUDBW
    
        myEdges.append(myLink)
    
    
    netJson['entity']=devices
    netJson['link']=myEdges
    
    
    #file = open(filePrefix+"network.json","w")
    file = open(storageFolder+"network.json","w")
    file.write(json.dumps(netJson))
    file.close()
    





def setConfigurations():

    global CLOUDCAPACITY
    global CLOUDBW
    global CLOUDPR

    global func_NETWORKGENERATION
    global PERCENTATGEOFGATEWAYS
    global func_PROPAGATIONTIME
    global func_BANDWITDH
    global func_NODERESOURECES


    global TOTALNUMBEROFAPPS
    global TOTALNUMBEROFNODES
    global func_APPMESSAGESIZE
    global func_APPRESOURCES
    global func_SERVICEINSTR

    global func_USERREQRAT
    global func_REQUESTPROB
    
    
    
    #****************************************************************************************************
    
    #INICIALIZACIONES Y CONFIGURACIONES
    
    #****************************************************************************************************
    if myConfiguration_ == 'newage':
    
        #CLOUD
        CLOUDCAPACITY = 9999999999999999  #MB RAM
        CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
        CLOUDPR = 1 # MS
    
    
        #NETWORK
        PERCENTATGEOFGATEWAYS = 0.25
        #TOTALNUMBEROFNODES = 10 # se queda en loop infinito en GAcolonyPartition2 metodo createPopulationCol
        TOTALNUMBEROFNODES = 17
        func_PROPAGATIONTIME = "random.randint(1,5)" #MS
        func_BANDWITDH = "random.randint(50000,75000)" # BYTES / MS
        #func_NETWORKGENERATION = "nx.barabasi_albert_graph(seed=2022,n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
        func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
        #func_NODERESOURECES = "random.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
        func_NODERESOURECES = "random.randint(10,15)" #MB RAM #random distribution for the resources of the fog devices
    
    
        #APSS
        TOTALNUMBEROFAPPS = 5
        func_APPMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
        func_APPRESOURCES = "random.randint(1,6)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
        func_SERVICEINSTR = "random.randint(400000,600000)"
        func_SERVICEINSTR = "4"
    
        #USERS and IoT DEVICES
        #func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_REQUESTPROB="random.random()/2" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_USERREQRAT="random.randint(200,1000)"  #MS

    if myConfiguration_ == "toguapho":       
        #CLOUD
        CLOUDCAPACITY = 9999999999999999  #MB RAM
        CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
        CLOUDPR = 1 # MS
    
    
        #NETWORK
        PERCENTATGEOFGATEWAYS = 0.25
        TOTALNUMBEROFNODES = 200
        func_PROPAGATIONTIME = "random.randint(1,5)" #MS
        func_BANDWITDH = "random.randint(50000,75000)" # BYTES / MS
        #func_NETWORKGENERATION = "nx.barabasi_albert_graph(seed=2022,n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
        func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
        #func_NODERESOURECES = "random.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
        func_NODERESOURECES = "random.randint(10,15)" #MB RAM #random distribution for the resources of the fog devices
    
        #APSS
        TOTALNUMBEROFAPPS = 20
        func_APPMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
        func_APPRESOURCES = "random.randint(1,6)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
        func_SERVICEINSTR = "random.randint(400000,600000)"
        
        
        #USERS and IoT DEVICES
        #func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_REQUESTPROB="3*random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_USERREQRAT="random.randint(200,1000)"  #MS



    if myConfiguration_ == "journal":       
        #CLOUD
        CLOUDCAPACITY = 9999999999999999  #MB RAM
        CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
        CLOUDPR = 100 # MS
    
    
        #NETWORK
        PERCENTATGEOFGATEWAYS = 0.25
        TOTALNUMBEROFNODES = 200
        func_PROPAGATIONTIME = "random.randint(2,6)" #MS
        func_BANDWITDH = "random.randint(50000,75000)" # BYTES / MS
        #func_NETWORKGENERATION = "nx.barabasi_albert_graph(seed=2022,n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
        func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(TOTALNUMBEROFNODES)+", m=2)" #algorithm for the generation of the network topology
        #func_NODERESOURECES = "random.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
        func_NODERESOURECES = "random.randint(1,4)" #MB RAM #random distribution for the resources of the fog devices
    
        #APSS
        TOTALNUMBEROFAPPS = 20
        func_APPMESSAGESIZE = "random.randint(100,20000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
        func_APPRESOURCES = "random.randint(1,2)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
        func_SERVICEINSTR = "random.randint(1000,3500)"
        
        
        #USERS and IoT DEVICES
        #func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_REQUESTPROB="3*random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_USERREQRAT="random.randint(5,10)"  #MS




def appsGeneration():

    global appsResources
    global appsPacketsSize
    global ReadPacketsSize
    global filesReadRatio
    global apps
    
    appJson=list()
    
    appsResources = [0 for j in range(TOTALNUMBEROFAPPS)]
    appsPacketsSize = [0 for j in range(TOTALNUMBEROFAPPS)]
    appsInstructions = [0 for j in range(TOTALNUMBEROFAPPS)]
    apps = [0 for j in range(TOTALNUMBEROFAPPS)]

   
    for j in range(0,TOTALNUMBEROFAPPS):
        appsResources[j]=eval(func_APPRESOURCES)
        appsPacketsSize[j]=eval(func_APPMESSAGESIZE)
        appsInstructions[j]=eval(func_SERVICEINSTR)
        apps[j]={}
        apps[j]['app']=j
        apps[j]['resources']=appsResources[j]
        apps[j]['packetsize']=appsPacketsSize[j]
        apps[j]['instructions']=appsInstructions[j]
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
        moduleApp['RAM'] = apps[j]['resources']
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
        messUserCoord['bytes'] = apps[j]['packetsize']
        messUserCoord['d'] = "C_"+str(j)
        messUserCoord['s'] = "None"
        messUserCoord['id'] = j*2
        messUserCoord['instructions'] = 0
        oneApp['message'].append(messUserCoord)
        messCoordApp ={}
        messCoordApp['name'] = 'MCA.'+str(j)
        messCoordApp['bytes'] = apps[j]['packetsize']
        messCoordApp['d'] = "A_"+str(j)
        messCoordApp['s'] = "C_"+str(j)
        messCoordApp['id'] = j*2+1
        messCoordApp['instructions'] = apps[j]['instructions']
        oneApp['message'].append(messCoordApp)                
    
        appJson.append(oneApp)


    file = open(storageFolder+"appDefinition.json","w")
    file.write(json.dumps(appJson))
    file.close()
   
    

    
def usersConnectionGeneration():
    
    
    #****************************************************************************************************
    #Generacion de los IoT devices (users) que requestean cada aplciacion
    #****************************************************************************************************
    
    global myUsers
    global appsRequests



    userJson ={}

    myUsers=list()
    appsRequests = list()
    for i in range(0,TOTALNUMBEROFAPPS):
        userRequestList = set()
        probOfRequested = eval(func_REQUESTPROB)
        atLeastOneAllocated = False
        for j in gatewaysDevices:
            if random.random()<probOfRequested:
                myOneUser={}
                myOneUser['app']=str(i)
                myOneUser['message']="MUC."+str(i)
                myOneUser['id_resource']=j
                myOneUser['lambda']=eval(func_USERREQRAT)
                userRequestList.add(j)
                myUsers.append(myOneUser)
                atLeastOneAllocated = True
        if not atLeastOneAllocated:
            j=random.randint(0,len(gatewaysDevices)-1)
            myOneUser={}
            myOneUser['app']=str(i)
            myOneUser['message']="MUC."+str(i)
            myOneUser['id_resource']=j
            myOneUser['lambda']=eval(func_USERREQRAT)
            userRequestList.add(j)
            myUsers.append(myOneUser)
        appsRequests.append(userRequestList)
    
    userJson['sources']=myUsers
    
    file = open(storageFolder+"usersDefinition.json","w")
    file.write(json.dumps(userJson))
    file.close()



#****************************************************************************************************

#FIN GENERACION MODELO

#****************************************************************************************************



