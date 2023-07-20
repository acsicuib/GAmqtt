#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 09:18:45 2022

@author: carlos
"""
import sys

import experimentationConfig
import optimizationConfig

"""
Subscribed to: 
    
command/nodeX/solutionTemplate	{solutionQuantity: <int>, solutionNumLines: <int>, solutionNumRows: <int>}		coordinator  --> worker(nodeX)

command/nodeY/sendSolution {solId:<int>, originNodeId:<str>}         master-->worker(nodeY)
solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
command/stopOptimization {}
"""



"""
Publishes:

    
command/join	{id: <str>}          worker -->coordinator    
fitness/nodeX   {idSol: <int>, fitness:{obj1:<float>...,objn:<float>}}		worker(nodeX)-->coordinator
solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
#####command/nodeX/removeSolutions {solIds:[<int>...<int>]}			worker(nodeY)-->coordinator
"""


import paho.mqtt.client as paho
import paho.mqtt.publish as publish
import time
import threading
import json
from solution import Solution
from optimizationproblem import OptimizationProblem
from log import Log


def getNeighborsOrderedByDistance(originWorker:str, listOfWorkers:list, mappingWorker2Node:dict) -> dict:

    try:
        originNode=mappingWorker2Node[originWorker]
    except KeyError:
        print("##########")
        print(originWorker)
        print(mappingWorker2Node)
        print(len(mappingWorker2Node))
        print(listOfWorkers)
        print(len(listOfWorkers))
    workersIndexedByDistance = dict()
    for idworker in listOfWorkers:
        idnode = mappingWorker2Node[idworker]
        distanceBetweenWorkers = nodesDistance(originNode,idnode)
        if not distanceBetweenWorkers in workersIndexedByDistance:
            workersIndexedByDistance[distanceBetweenWorkers] = list()
        workersIndexedByDistance[distanceBetweenWorkers].append(idworker)

    return workersIndexedByDistance

def sendMessage(topic:str, payload:str, hostname:str ) -> None:
    if experimentationConfig.time2SleepInWorker > 0.0:
        time.sleep(experimentationConfig.time2SleepInWorker)
    publish.single(topic=topic, payload=payload,
                   hostname=hostname)


def nodesDistance(a:int, b:int) -> float:
    global optProblem

    return optProblem.infrastructure4mqttJson['Gdistances'][str(a)][str(b)]

def getNeighbors(listOfWorkers: list, neighborDistances: dict) -> list:
    listOfNeighbors = list()

    if experimentationConfig.unit4Radius=='distance':
        for distance,workers in neighborDistances.items():
            if distance>0 and distance <= experimentationConfig.neighborsRadius:
                listOfNeighbors = listOfNeighbors + workers
        return listOfNeighbors

    if experimentationConfig.unit4Radius=='hop':
        distances= list(neighborDistances.keys())
        distances.sort()
        for hop,distance in enumerate(distances):
            if hop>0:
                listOfNeighbors = listOfNeighbors + neighborDistances[distance]
            if hop == experimentationConfig.neighborsRadius:
                break
        return listOfNeighbors

        # for numHops in range(1,experimentationConfig.neighborsRadius+1):
        #     distance4ThisHop = distances[numHops]
        #     workersInThisDistance = neighborDistances[distance4ThisHop]
        #     listOfNeighbors = listOfNeighbors + workersInThisDistance




    #TODO return only the neighbors


def requireSolution2startNewCrossOver() -> None:
    global listOfWorkers
    global listOfNeighbors

    # we choose a worker to require it a new random solution
    if experimentationConfig.onlyNeighbors and len(listOfNeighbors)>0:  #if no neighbors are detected, we select between all the nodes
        workerIdWithTheSolution=optProblem.selectRandomWorker(listOfNeighbors)
    else:
        workerIdWithTheSolution=optProblem.selectRandomWorker(listOfWorkers)


    #populationElement = optProblem.TournamentSelection()
    #workerIdWithTheSolution = populationElement.getWorkerId()
    #solutionId = populationElement.getSolutionId()

    # the message command/nodeY/sendSolution {solId:<int>, originNodeId:<str>}      coordinator --> nodeY
    # is published to ask the worker with the solution to send the whole solution to the origin worker
    dictPayload = dict()
    #dictPayload['solId'] = solutionId
    dictPayload['originNodeId'] = nodeIdStr
    sendMessage(topic="command/" + workerIdWithTheSolution + "/sendSolution", payload=json.dumps(dictPayload),
                   hostname=mqtt_host)

    # TODO crear una lista de mensajes enviados a workers para que reenvien solucion con el instante de tiempo que se hizo.
    # pasado un tiempo, deberia de eliminarse cancelarse la solicitud y realizar una nueva a otro nodo. llevar un contador de veces que un nodo
    # no responde, y superado un limite, darlo de baja, con sus soluciones correspondientes.


#actions to perform when arrives the message command/all/solutionTemplate	{solutionQuantity: <int>, solutionConfig: <dict>}		coordinator  --> worker(nodeX)
#this message is recieved as answer when all the workers have sent the command/join of the command to notify to the coordinator that a new worker (this one) is started.
# Once  all those messages are received by the coordinator, it sends to new worker the template
#of the solutions. Once recieved, all the workers should start to create its population with random solutions. Once it finished, the worker sends the fitness
#of the new solutions to the coordinator

def globalInitialization(jConf: bytes) -> None:
    log.print(nodeIdStr+":::defining the solution template",'operation')
    global optProblem
    global simulatedNode
    global cloudNode
    global listOfWorkers
    global mappingWorker2Node
    global listOfNeighbors
    global neighborDistances

    #we retrieve the size of the population and the solution template
    jsonContent = json.loads(jConf)
    numberOfSolutionsInWorkers = jsonContent['solutionQuantity']
    solutionConfig = jsonContent['solutionConfig']
    infrastructure = jsonContent['infrastructure']
    cloudNode = jsonContent['cloudNode']
    listOfWorkers = jsonContent['listOfWorkers']
    mappingWorker2Node = jsonContent['mappingWorker2Node']

    simulatedNode = mappingWorker2Node[nodeIdStr]
    workerJoinOrder = listOfWorkers.index(nodeIdStr)
    randomseed = jsonContent['randomseed'] * workerJoinOrder

    optProblem = OptimizationProblem(log,randomseed,numberOfSolutionsInWorkers,solutionConfig,infrastructure)
#    optProblem = OptimizationProblem(numberOfSolutionsInWorkers,solutionConfig,infrastructure)

    if experimentationConfig.onlyNeighbors:
        neighborDistances = getNeighborsOrderedByDistance(nodeIdStr, listOfWorkers, mappingWorker2Node)
        listOfNeighbors = getNeighbors(listOfWorkers, neighborDistances)

    dictPayload = dict()
    dictPayload['workerId']=nodeIdStr
    setOfSolutions = optProblem.getPopulationFitnessInJson()
    dictPayload['solutions']=setOfSolutions


    log.print(nodeIdStr+":::sending set of solution's fitnesses",'operation')
    log.print(nodeIdStr+":::with topic "+"fitness/"+nodeIdStr+"/newpopulation",'operation-details')
    log.print(nodeIdStr+":::with payload "+json.dumps(dictPayload),'operation-details')
    sendMessage(topic="fitness/"+nodeIdStr+"/newpopulation", payload=json.dumps(dictPayload), hostname=mqtt_host)


    #TODO if a local final condition to stop the execution of the worker is required, this is the place to check it.
    #if the condition is met, the requireSolution2startNewCrossover is not called.

    requireSolution2startNewCrossOver()





#actions to perform when arrives the message command/nodeX/solutionTemplate	{solutionQuantity: <int>, solutionConfig: <dict>}		coordinator  --> worker(nodeX)
#this message is recieved as answer of the command to notify to the coordinator that a new worker (this one) is started. Then the coordinator send to new worker the template
#of the solutions. Once recieved, the worker should start to create its population with random solutions. Once it finished, the worker sends the fitness
#of the new solutions to the coordinator
def initSolutionTemplate(jConf: bytes) -> None:
    log.print(nodeIdStr+":::defining the solution template",'operation')
    global optProblem
    global simulatedNode
    global cloudNode
    global listOfWorkers
    global mappingWorker2Node
    global listOfNeighbors
    global neighborDistances

    #we retrieve the size of the population and the solution template
    jsonContent = json.loads(jConf)
    numberOfSolutionsInWorkers = jsonContent['solutionQuantity']
    solutionConfig = jsonContent['solutionConfig']
    infrastructure = jsonContent['infrastructure']
    simulatedNode = jsonContent['simulatedNode']
    cloudNode = jsonContent['cloudNode']
    randomseed = jsonContent['randomseed']
    listOfWorkers = jsonContent['listOfWorkers']
    mappingWorker2Node = jsonContent['mappingWorker2Node']



    optProblem = OptimizationProblem(log,randomseed,numberOfSolutionsInWorkers,solutionConfig,infrastructure)
#    optProblem = OptimizationProblem(numberOfSolutionsInWorkers,solutionConfig,infrastructure)

    if experimentationConfig.onlyNeighbors:
        neighborDistances = getNeighborsOrderedByDistance(nodeIdStr, listOfWorkers, mappingWorker2Node)
        listOfNeighbors = getNeighbors(listOfWorkers, neighborDistances)

    dictPayload = dict()
    dictPayload['workerId']=nodeIdStr
    setOfSolutions = optProblem.getPopulationFitnessInJson()
    dictPayload['solutions']=setOfSolutions


    log.print(nodeIdStr+":::sending set of solution's fitnesses",'operation')
    log.print(nodeIdStr+":::with topic "+"fitness/"+nodeIdStr+"/newpopulation",'operation-details')
    log.print(nodeIdStr+":::with payload "+json.dumps(dictPayload),'operation-details')
    sendMessage(topic="fitness/"+nodeIdStr+"/newpopulation", payload=json.dumps(dictPayload), hostname=mqtt_host)


    #TODO if a local final condition to stop the execution of the worker is required, this is the place to check it.
    #if the condition is met, the requireSolution2startNewCrossover is not called.

    #time.sleep(1) #1 second
    requireSolution2startNewCrossOver()



# #actions to perform when arrives the message command/nodeX/removeSolutions {solIds:[<int>...<int>]}			coordinator-->worker(nodeY)
# def removeSolutions(jConf: bytes) -> None:
#     log.print(nodeIdStr+":::removing solutions",'operation')
#
#     #we retrieve {solIds:[<int>...<int>]}
#     jsonContent = json.loads(jConf)
#     solIds = jsonContent['solIds']
#
#     for idSol in solIds:
#         if optProblem.removeOneWorstSolutionById(idSol,optimizationConfig.selfId4Worker)==False:
#             log.print(nodeIdStr+":::ERROR removing solution, solution not found")
#


#actions to perform when arrives the message ccommand/nodeY/sendSolution {solId:<int>, targetNodeId:<str>}         master-->worker(nodeY)
def sendSolution(jConf: bytes) -> None:
    global simulatedNode

    log.print(nodeIdStr+":::sending the solution to the origin worker",'operation')

    #we retrieve {solId:<int>, originNodeId:<str>}
    jsonContent = json.loads(jConf)
    #solId = jsonContent['solId']
    originId = jsonContent['originNodeId']

    #the message solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
    #is published to send the solution chromosome to the origin worker
    solId = optProblem.TournamentSelection().getSolutionId()
    dictPayload = dict()
    solChromosome = optProblem.getSolutionChromosomeById(solId,optimizationConfig.selfId4Worker)

    dictPayload['chromosome']=solChromosome
    dictPayload['senderWorkerId'] = nodeIdStr
    dictPayload['senderSimulatedNode'] = simulatedNode
    sendMessage(topic="solution/"+originId+"", payload=json.dumps(dictPayload), hostname=mqtt_host)

    if solChromosome == None:
        log.print(nodeIdStr+":::ERROR solution id not found: "+str(solId),'worker')
        ##the message solution/nak  {solId:<int>, originNodeId:<str>, targetNodeId:<str>} 			worker(nodeY) --> worker(nodeX)
        #is sent by the worker to notify to the coordinator that the solution is not found
        jsonContent['targetNodeId']=nodeIdStr
        sendMessage(topic="solution/nak", payload=json.dumps(jsonContent), hostname=mqtt_host)
    else:
        ##the message solution/ack  {solId:<int>, originNodeId:<str>, targetNodeId:<str>} 			worker(nodeY) --> worker(nodeX)
        #is sent by the worker to notify to the coordinator that the solution is sent
        jsonContent['targetNodeId']=nodeIdStr
        sendMessage(topic="solution/ack", payload=json.dumps(jsonContent), hostname=mqtt_host)


#actions to perform when arrives the message solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
def solutionRecieved(jConf: bytes) -> None:
    global simulatedNode
    global cloudNode

    log.print(nodeIdStr+":::we receive the solution from other worker to crossover it",'operation')

    #we retrieve {chromosome: <str>}
    jsonContent = json.loads(jConf)
    solChrom = jsonContent['chromosome']
    senderWorkerID = jsonContent['senderWorkerId']
    senderSimulatedNode = jsonContent['senderSimulatedNode']

    childrenOffspring = optProblem.evolveWithRemoteSolution(solChrom)
    #Two alternatives possible for the populaiton in the workers. Join the twoNewChildren to the current subpopulation
    #of the worker, incresing its size, or replace the two worst solutions in the subpopulation with the two new ones.
    #we decided the fist one, and the selection of the solutions to be removed is shifted to the coordinator. Then
    #the worst solutions in the whole population are selected, instead the worst two solutions in the subpopulation
    #The only problem of this solution is that the population sizes in the workers can be different.
    optProblem.joinTwoPopulations(childrenOffspring)

    dictPayload = dict()
    dictPayload['workerId']=nodeIdStr
    setOfSolutions = optProblem.getSolutionsFitnessInJson(childrenOffspring)
    dictPayload['solutions']=setOfSolutions
    #dictPayload['pathLengthIslands'] = 2*nodesDistance(cloudNode,simulatedNode)
    dictPayload['pathLengthFullMigration'] = 2*nodesDistance(senderSimulatedNode,simulatedNode)


    #the two worst solutions in the population are removed. The central populatuion (for experimental porpouse only) need to
    #be updated, so, the ids are sent with the fitness/+/newChildren messaga
    numOfNewSolutions = len(childrenOffspring)
    toRemove = optProblem.removeManyWorstSolutions(numOfNewSolutions)

    dictPayload['solIds2Remove'] = list()
    log.print(nodeIdStr+":::going to remove "+str(toRemove),'operation-details')
    for sol in toRemove:
        #the message command/nodeX/removeSolutions {solIds:[<int>...<int>]}			worker(nodeY) --> coordinator
        #is published to ask the coordinator to remove the solutions from the central control set (for experimentation porpouse only)
        dictPayload['solIds2Remove'].append(sol.getSolutionId())

    sendMessage(topic="fitness/"+nodeIdStr+"/newchildren", payload=json.dumps(dictPayload), hostname=mqtt_host)

    requireSolution2startNewCrossOver()


def stopOptimization(jConf: bytes) -> None:
    global finishCondition
    finishCondition=True


def joinClient(jConf: bytes) -> None:
    global listOfWorkers
    global mappingWorker2Node
    global optProblem
    global thisRepetition

    log.print(":::including new worker", 'operation')
    jsonContent = json.loads(jConf)
    workerId = jsonContent['workerId']
    workerIdStr = str(workerId)
    listOfWorkers.append(workerId)
    mappingWorker2Node[workerId] = optProblem.getInfrastructure().get_ithSmallestCentralityDevice(len(listOfWorkers))

def updateListOfWorkers(jConf: bytes) -> None:
    global listOfWorkers
    global mappingWorker2Node
    global listOfNeighbors
    global neighborDistances
    global i

    while len(listOfWorkers)==0 or len(mappingWorker2Node)==0:
        #print("@"+nodeIdStr)
        pass
    jsonContent = json.loads(jConf)
    listOfWorkers = jsonContent['listOfWorkers']
    mappingWorker2Node = jsonContent['mappingWorker2Node']

   # print(nodeIdStr+"; message "+str(i)+";"+str(len(listOfWorkers))+";"+str(listOfWorkers))

    if experimentationConfig.onlyNeighbors:
        #print("################################" + nodeIdStr, flush=True)
        #print("mappingWorker2Node"+nodeIdStr,flush=True)
        #print(mappingWorker2Node,flush=True)
        #print("listOfWorkers"+nodeIdStr,flush=True)
        #print(listOfWorkers,flush=True)
        neighborDistances = getNeighborsOrderedByDistance(nodeIdStr, listOfWorkers, mappingWorker2Node)
        listOfNeighbors = getNeighbors(listOfWorkers, neighborDistances)
        #print("################################"+nodeIdStr,flush=True)
        #print("nodeIdSrt"+nodeIdStr,flush=True)
        #print(nodeIdStr,flush=True)
        #print("listOfNeighbors"+nodeIdStr)
        #print(listOfNeighbors,flush=True)

def getTopicTargetNode(topic: str) -> str:
    return topic.split("/")[1]

def process_message(mosq: paho.Client, obj, msg: paho.MQTTMessage) -> None:
    global i
    log.print(nodeIdStr+":::getting message number "+str(i),'operation-details')
    log.print(nodeIdStr+":::with topic "+str(msg.topic),'operation-details')
    log.print(nodeIdStr+":::with qos "+str(msg.qos),'operation-details')
    log.print(nodeIdStr+":::with payload "+str(msg.payload),'operation-details')
    i=i+1

    #decode the command through the analysis of the topic

    if msg.topic.startswith("command/") and msg.topic.endswith("/solutionTemplate"):
        targetNode = getTopicTargetNode(msg.topic)
        if targetNode=='all':
            globalInitialization(msg.payload)
        else:
            print("ERROR, the solutionTemplate topic is always used with all is id of the node")
        # if targetNode == nodeIdStr:
        #     initSolutionTemplate(msg.payload)
        # else:
        #     updateListOfWorkers(msg.payload)

#    elif (msg.topic=="command/"+nodeIdStr+"/removeSolutions"):
#        removeSolutions(msg.payload)
    elif (msg.topic=="command/"+nodeIdStr+"/sendSolution"):
        sendSolution(msg.payload)
    elif (msg.topic=="solution/"+nodeIdStr+""):
        solutionRecieved(msg.payload)
    elif (msg.topic=="command/stopOptimization"):
        stopOptimization(msg.payload)
    else:
        log.print(nodeIdStr+":::ERROR-message not understood",'worker')

#call back functon when a message is received
def on_message(mosq: paho.Client, obj, msg: paho.MQTTMessage) -> None:
    proMsg = threading.Thread(target=process_message,args=[mosq, obj, msg])
    proMsg.start()
    # if experimentationConfig.time2SleepInWorker > 0.0:
    #     time.sleep(experimentationConfig.time2SleepInWorker)
    #mosq.publish('pong', 'ack', 0)

#call back functon when a message is sent
def on_publish(mosq, obj, mid):
    pass

if __name__ == '__main__':


    if len(sys.argv)>2:
        repetition = sys.argv[2]
        executionScenario = sys.argv[1]
    else:
        repetition=0
        executionScenario='manually'

    i = 0  # counter for the number of messages

    listOfWorkers = []  # list of all the workers in the system
    mappingWorker2Node = dict()
    neighborDistances = dict()

    #stablish connection to mosquitto server
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    #client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
    mqtt_host="127.0.0.1"
    client.connect(mqtt_host, 1883, 60)


    #getting the id for the worker node based on the mqtt client id
    nodeId =client._client_id
    nodeId=nodeId.replace('paho/','')
    nodeIdStr = 'nodeX'
    nodeIdStr = str(nodeId)

    log = Log(nodeIdStr,nodeIdStr+":::",executionScenario+'-'+str(repetition)+'-workers')

    log.print("worker node started for repetition: "+str(repetition)+" and scenario "+executionScenario,'worker')

    #defining the listh of topic the client is subscribed to
    # wildcards:   + single-level    #multi-level
    client.subscribe("command/+/solutionTemplate", 0)
#    client.subscribe("command/"+nodeIdStr+"/removeSolutions", 0)
    client.subscribe("command/"+nodeIdStr+"/sendSolution", 0)
    client.subscribe("solution/"+nodeIdStr+"", 0)
    client.subscribe("command/stopOptimization",0)



    #the message command/join	{id: <str>}          worker -->coordinator
    #is published to notify to the coordinator that a new worker is available. The coordinator will send to this new worker the solution template.
    dictPayload = dict()
    dictPayload['workerId']=nodeIdStr
    sendMessage(topic="command/join", payload=json.dumps(dictPayload), hostname=mqtt_host)

    finishCondition = False
    #getting into an infinite loop or the finishcondition is reached
    while client.loop() == 0 and not finishCondition:
        pass

    client.disconnect()  # disconnect gracefully
    client.loop_stop()  # stops network loop

    log.print("worker finished", 'worker')