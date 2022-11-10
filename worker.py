#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 09:18:45 2022

@author: carlos
"""
import sys

import optimizationConfig

"""
Subscribed to: 
    
command/nodeX/solutionTemplate	{solutionQuantity: <int>, solutionNumLines: <int>, solutionNumRows: <int>}		coordinator  --> worker(nodeX)
command/nodeX/removeSolutions {solIds:[<int>...<int>]}			coordinator-->worker(nodeY)
command/nodeY/sendSolution {solId:<int>, originNodeId:<str>}         master-->worker(nodeY)
solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
command/stopOptimization {}
"""



"""
Publishes:

    
command/join	{id: <str>}          worker -->coordinator    
fitness/nodeX   {idSol: <int>, fitness:{obj1:<float>...,objn:<float>}}		worker(nodeX)-->coordinator
solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
"""


import paho.mqtt.client as paho
import paho.mqtt.publish as publish
import time
import threading
import json
from solution import Solution
from optimizationproblem import OptimizationProblem
from log import Log


#actions to perform when arrives the message command/nodeX/solutionTemplate	{solutionQuantity: <int>, solutionConfig: <dict>}		coordinator  --> worker(nodeX)
#this message is recieved as answer of the command to notify to the coordinator that a new worker (this one) is started. Then the coordinator send to new worker the template
#of the solutions. Once recieved, the worker should start to create its population with random solutions. Once it finished, the worker sends the fitness
#of the new solutions to the coordinator 
def initSolutionTemplate(jConf: bytes) -> None:
    log.print(nodeIdStr+":::defining the solution template",'operation')
    global optProblem
    
    #we retrieve the size of the population and the solution template
    jsonContent = json.loads(jConf)
    numberOfSolutionsInWorkers = jsonContent['solutionQuantity']
    solutionConfig = jsonContent['solutionConfig']
    infrastructure = jsonContent['infrastructure']
    randomseed = jsonContent['randomseed']
    
    optProblem = OptimizationProblem(log,randomseed,numberOfSolutionsInWorkers,solutionConfig,infrastructure)
#    optProblem = OptimizationProblem(numberOfSolutionsInWorkers,solutionConfig,infrastructure)
    

    
    dictPayload = dict()
    dictPayload['workerId']=nodeIdStr
    setOfSolutions = optProblem.getPopulationFitnessInJson()
    dictPayload['solutions']=setOfSolutions
    
        
    log.print(nodeIdStr+":::sending set of solution's fitnesses",'operation')
    log.print(nodeIdStr+":::with topic "+"fitness/"+nodeIdStr+"/newpopulation",'operation-details')
    log.print(nodeIdStr+":::with payload "+json.dumps(dictPayload),'operation-details')
    publish.single(topic="fitness/"+nodeIdStr+"/newpopulation", payload=json.dumps(dictPayload), hostname=mqtt_host)
    
    
#actions to perform when arrives the message command/nodeX/removeSolutions {solIds:[<int>...<int>]}			coordinator-->worker(nodeY)
def removeSolutions(jConf: bytes) -> None:
    log.print(nodeIdStr+":::removing solutions",'operation')

    #we retrieve {solIds:[<int>...<int>]}	
    jsonContent = json.loads(jConf)
    solIds = jsonContent['solIds']

    for idSol in solIds:
        if optProblem.removeOneWorstSolutionById(idSol,optimizationConfig.selfId4Worker)==False:
            log.print(nodeIdStr+":::ERROR removing solution, solution not found")
 
    
 
#actions to perform when arrives the message ccommand/nodeY/sendSolution {solId:<int>, targetNodeId:<str>}         master-->worker(nodeY)
def sendSolution(jConf: bytes) -> None:
    log.print(nodeIdStr+":::sending the solution to the origin worker",'operation')
    
    #we retrieve {solId:<int>, originNodeId:<str>} 
    jsonContent = json.loads(jConf)
    solId = jsonContent['solId']
    originId = jsonContent['originNodeId']

    #the message solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
    #is published to send the solution chromosome to the origin worker 
    dictPayload = dict()
    solChromosome = optProblem.getSolutionChromosomeById(solId,optimizationConfig.selfId4Worker)
    dictPayload['chromosome']=solChromosome
    publish.single(topic="solution/"+originId+"", payload=json.dumps(dictPayload), hostname=mqtt_host)
        
    if solChromosome == None:
        log.print(nodeIdStr+":::ERROR solution id not found: "+str(solId),'worker')
        ##the message solution/nak  {solId:<int>, originNodeId:<str>, targetNodeId:<str>} 			worker(nodeY) --> worker(nodeX)
        #is sent by the worker to notify to the coordinator that the solution is not found
        jsonContent['targetNodeId']=nodeIdStr
        publish.single(topic="solution/nak", payload=json.dumps(jsonContent), hostname=mqtt_host)
    else:
        ##the message solution/ack  {solId:<int>, originNodeId:<str>, targetNodeId:<str>} 			worker(nodeY) --> worker(nodeX)
        #is sent by the worker to notify to the coordinator that the solution is sent
        jsonContent['targetNodeId']=nodeIdStr
        publish.single(topic="solution/ack", payload=json.dumps(jsonContent), hostname=mqtt_host)

    
#actions to perform when arrives the message solution/nodeX  {chromosome: <str>}			worker(nodeY) --> worker(nodeX)
def solutionRecieved(jConf: bytes) -> None:
    log.print(nodeIdStr+":::we receive the solution from other worker to crossover it",'operation')

    #we retrieve {chromosome: <str>}	
    jsonContent = json.loads(jConf)
    solChrom = jsonContent['chromosome']
    
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

    publish.single(topic="fitness/"+nodeIdStr+"/newchildren", payload=json.dumps(dictPayload), hostname=mqtt_host)


def stopOptimization(jConf: bytes) -> None:
    global finishCondition
    finishCondition=True

def process_message(mosq: paho.Client, obj, msg: paho.MQTTMessage) -> None:
    global i
    log.print(nodeIdStr+":::getting message number "+str(i),'operation-details')
    log.print(nodeIdStr+":::with topic "+str(msg.topic),'operation-details')
    log.print(nodeIdStr+":::with qos "+str(msg.qos),'operation-details')
    log.print(nodeIdStr+":::with payload "+str(msg.payload),'operation-details')
    i=i+1

    #decode the command through the analysis of the topic
    if (msg.topic=="command/"+nodeIdStr+"/solutionTemplate"):
        initSolutionTemplate(msg.payload)
    elif (msg.topic=="command/"+nodeIdStr+"/removeSolutions"):
        removeSolutions(msg.payload)
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
    #time.sleep(0.25)
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
    client.subscribe("command/"+nodeIdStr+"/solutionTemplate", 0)
    client.subscribe("command/"+nodeIdStr+"/removeSolutions", 0)
    client.subscribe("command/"+nodeIdStr+"/sendSolution", 0)
    client.subscribe("solution/"+nodeIdStr+"", 0)
    client.subscribe("command/stopOptimization",0)

    

    #the message command/join	{id: <str>}          worker -->coordinator   
    #is published to notify to the coordinator that a new worker is available. The coordinator will send to this new worker the solution template.
    dictPayload = dict()
    dictPayload['workerId']=nodeIdStr
    publish.single(topic="command/join", payload=json.dumps(dictPayload), hostname=mqtt_host)

    finishCondition = False
    #getting into an infinite loop or the finishcondition is reached
    while client.loop() == 0 and not finishCondition:
        pass

    client.disconnect()  # disconnect gracefully
    client.loop_stop()  # stops network loop

    log.print("worker finished", 'worker')