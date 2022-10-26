#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 09:18:21 2022

@author: carlos
"""


"""

Para arrancar mosquitto

/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf




Subscribed to: 
    
command/join	{id: <str>}          worker -->coordinator    
fitness/nodeX   {idSol: <int>, fitness:{obj1:<float>...,objn:<float>}}		worker(nodeX)-->coordinator
"""



"""
Publishes:
    
command/nodeX/solutionTemplate	{solutionQuantity: <int>, solutionConfig: <dict>}		coordinator  --> worker(nodeX)
command/nodeX/removeSolutions {solIds:[<int>...<int>]}			coordinator-->worker(nodeY)
command/nodeY/sendSolution {solId:<int>, originNodeId:<str>}         master-->worker(nodeY)
"""




import paho.mqtt.client as paho
import paho.mqtt.publish as publish
import time
import threading
import json
from optimizationproblem import OptimizationProblem
from log import Log


#actions to perform when arrives the message command/join	{id: <str>}          worker -->coordinator 
#a new worker notify the coordinator that it started. we include the worker in the list of workers and coordinator send the solution template to the worker
def joinClient(jConf):
    global listOfWorker
    global optProblem
    
    log.print("COORDINATOR-"+coordinatorIdStr+":::including new worker",'operation')
    jsonContent = json.loads(jConf)
    workerId = jsonContent['workerId']
    workerIdStr = str(workerId)
    listOfWorkers.append(workerId)
    
    #the message command/nodeX/solutionTemplate	{solutionQuantity: <int>, solutionConfig: <dict>}		coordinator  --> worker(nodeX) 
    #is published to notify to inform the worker of the solution template and number of solutions
    dictPayload = dict()
    dictPayload['solutionQuantity']=optProblem.numberOfSolutions
    dictPayload['solutionConfig']=optProblem.solutionTemplate
    dictPayload['infrastructure']=optProblem.infrastructure
    #dictPayload['infrastructure']=dict()
    #dictPayload['infrastructure']['Gdistances']=optProblem.infrastructure['Gdistances']
    #dictPayload['infrastructure']['clientNodes'] = optProblem.infrastructure['clientNodes']
    publish.single(topic="command/"+workerIdStr+"/solutionTemplate", payload=json.dumps(dictPayload), hostname=mqtt_host)  



def startNewCrossOver(originWorkerId):
    #we choose a new solution in the global solution and send to its worker the notification to send it to the origin worker

    populationElement = optProblem.TournamentSelection()
    workerIdWithTheSolution = optProblem.getWorkerId(populationElement)
    solutionId = optProblem.getSolutionId(populationElement)

   
    #the message command/nodeY/sendSolution {solId:<int>, originNodeId:<str>}      coordinator --> nodeY
    #is published to ask the worker with the solution to send the whole solution to the origin worker
    dictPayload = dict()
    dictPayload['solId']=solutionId
    dictPayload['originNodeId']=originWorkerId
    publish.single(topic="command/"+workerIdWithTheSolution+"/sendSolution", payload=json.dumps(dictPayload), hostname=mqtt_host)  
 
     #TODO crear una lista de mensajes enviados a workers para que reenvien solucion con el instante de tiempo que se hizo.
     #pasado un tiempo, deberia de eliminarse cancelarse la solicitud y realizar una nueva a otro nodo. llevar un contador de veces que un nodo
     #no responde, y superado un limite, darlo de baja, con sus soluciones correspondientes.



def newWorkerPopulationTopic(jConf):
    log.print("COORDINATOR-"+coordinatorIdStr+":::including new population from a worker",'operation')
    jsonContent = json.loads(jConf)
    originWorkerId=jsonContent['workerId']
    optProblem.joinWithNewWorkerPopulation(originWorkerId, jsonContent['solutions'])
    log.dumpFronts(optProblem.fronts,'dump-population')
    startNewCrossOver(originWorkerId)

def newWorkerChildrenTopic(jConf):
    log.print("COORDINATOR-"+coordinatorIdStr+":::including new children from a worker",'operation')
    jsonContent = json.loads(jConf)
    originWorkerId=jsonContent['workerId']
    toRemove = optProblem.incorporateChildrenInCoordinatorPopulation(originWorkerId, jsonContent['solutions'])

    
    log.print("COORDINATOR-"+coordinatorIdStr+":::going to remove "+str(toRemove),'operation-details')
    for sol in toRemove:
        #the message command/nodeX/removeSolutions {solIds:[<int>...<int>]}			coordinator-->worker(nodeY)
        #is published to ask the worker with the removed solution to remove it
        dictPayload = dict()
        dictPayload['solIds']=list()
        dictPayload['solIds'].append(sol['solutionId'])
        workerIdWithTheSolution = sol['workerId']
        log.print("COORDINATOR-"+coordinatorIdStr+":::removing solution "+str(i),'operation-details')
        log.print("COORDINATOR-"+coordinatorIdStr+":::with topic "+"command/"+workerIdWithTheSolution+"/removeSolutions",'operation-details')
        log.print("COORDINATOR-"+coordinatorIdStr+":::with payload "+json.dumps(dictPayload),'operation-details')
        publish.single(topic="command/"+workerIdWithTheSolution+"/removeSolutions", payload=json.dumps(dictPayload), hostname=mqtt_host)

    log.dumpFronts(optProblem.fronts, 'dump-population')
    startNewCrossOver(originWorkerId)

def process_message(mosq, obj, msg):
    global i
    log.print("COORDINATOR-"+coordinatorIdStr+":::getting message number "+str(i),'mqtt-details')
    log.print("COORDINATOR-"+coordinatorIdStr+":::with topic "+str(msg.topic),'mqtt-details')
    log.print("COORDINATOR-"+coordinatorIdStr+":::with qos "+str(msg.qos),'mqtt-details')
    log.print("COORDINATOR-"+coordinatorIdStr+":::with payload "+str(msg.payload),'mqtt-details')
    i=i+1

    #decode the command through the analysis of the topic
    if (msg.topic=="command/join"):
        joinClient(msg.payload)
    elif (msg.topic.startswith("fitness/")):
        if (msg.topic.endswith("/newpopulation")):
            newWorkerPopulationTopic(msg.payload)
        elif (msg.topic.endswith("/newchildren")):
            newWorkerChildrenTopic(msg.payload)
        else:
            log.print("COORDINATOR-"+coordinatorIdStr+":::ERROR-message not understood",'coordinator')
    else:
        log.print("COORDINATOR-"+coordinatorIdStr+":::ERROR-message not understood",'coordinator')

#call back functon when a message is received
def on_message(mosq, obj, msg):
    proMsg = threading.Thread(target=process_message,args=[mosq, obj, msg])
    proMsg.start()
    time.sleep(0.25)
    #mosq.publish('pong', 'ack', 0)

#call back functon when a message is sent
def on_publish(mosq, obj, mid): 
    pass

i = 0 #counter for the number of messages
listOfWorkers = list() #list of all the workers in the system

if __name__ == '__main__':

    #stablish connection to mosquitto server
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    #client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
    mqtt_host="127.0.0.1"
    client.connect(mqtt_host, 1883, 60)


    #getting the id for the coordinator based on the mqtt client id
    coordinatorId =client._client_id
    coordinatorId=coordinatorId.replace('paho/','')
    coordinatorIdStr=str(coordinatorId)

    log = Log(coordinatorIdStr,coordinatorId+":::")

    log.print("coordinator started",'coordinator')
    
    #defining the listh of topic the client is subscribed to
    client.subscribe("command/join", 0)
    client.subscribe("fitness/#", 0)

    

    #create one solution
    optProblem=OptimizationProblem(log)
#    optProblem=OptimizationProblem()


    #getting into an infinite loop
    while client.loop() == 0:
        pass

