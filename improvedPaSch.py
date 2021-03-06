import math
from consistentHash import ConsistentHash
from GLOBAL import *

class ImprovedPaSch:
    # workers: Worker[], functions : Function[], packages : Package[]
    def __init__(self,hashworkers, workers, functions, packages):
        
        self.consitentHash = ConsistentHash(hashworkers) #so now updates in hash are part of pasch so no worries
        
        self.salt = salt
        self.threshold = threshold

        self.workers = workers
        self.functions = functions
        self.packages = packages
        self.totalRequests = 0
        self.cacheHits1 = 0
        self.cacheHits2 = 0
        self.cacheMiss = 0

        self.LEASTLOADEDCALLS = 0

    def getCacheHitAndMissDetails(self):
        return {"totalRequests":self.totalRequests,"cacheHits1":self.cacheHits1,"cacheHits2":self.cacheHits2,"cacheMiss":self.cacheMiss, "LEASTLOADEDCALLS":self.LEASTLOADEDCALLS}

    def getLoad(self, worker_id, timestamp):
        workerNodes = self.workers

        index = self.getIndexInWorkersArray(worker_id) #here self.workers == workerNodes hence ok

        #here we will need to clear all the functions that have been executed at this worker.runningFunction and update the 
        #worker.currentLoad as well which is just len(worker.runningFunction)
        workerNodes[index].updateRuningFunctionsList(timestamp)
        self.workers = workerNodes
        return workerNodes[index].currentLoad


    def getLeastLoadedWorker(self,timestamp):
            self.LEASTLOADEDCALLS += 1
            #uses all keys in consistent Hash and gets min loaded
            min_worker_id =""
            min_worker_id_load = math.inf
            for i in range(0,len(self.workers)) :
                curr_load = self.getLoad(self.workers[i].worker_id,timestamp)
                if(min_worker_id_load > curr_load) :
                    min_worker_id_load = curr_load
                    min_worker_id = self.workers[i].worker_id
            
            return min_worker_id

    def getWorkerDetails(self,timestamp):
        oldWorkerNodes = self.workers
        workerNodes = self.updateStaleWorkerData(oldWorkerNodes,timestamp)
        
        workerDetails = []

        for i in range(0,len(workerNodes)) :
            workerDetails.append({"worker_id:":workerNodes[i].worker_id,
            "threshold":workerNodes[i].threshold,
            "currentLoad":workerNodes[i].currentLoad,
            "runningFunctions":workerNodes[i].runningFunctions,
            "lastExecutedTime":workerNodes[i].lastExecutedTime,
            })
        
        self.workers = workerNodes

        return workerDetails

    def updateStaleWorkerData(self,workerNodes,timestamp):
        
        for i in range(0,len(workerNodes)) :
            #updates current Load
            workerNodes[i].currentLoad = self.getLoad(workerNodes[i].worker_id,timestamp)
            # updates runningFunctions -> they are updated automatically when getLoad is called
            # DO :updates lastExecutedTime
            # {pid,time}
            newLastExecutedTime = {}
            for key in workerNodes[i].lastExecutedTime :
                if(workerNodes[i].lastExecutedTime[key] + cacheCleanTime > timestamp) :
                    #time to remove cached pkg is yet to come hence keep them as they are in the map
                    newLastExecutedTime[key] = workerNodes[i].lastExecutedTime[key]
                    # print(key,"is previously run at", workerNodes[i].lastExecutedTime[key] )
                    # print("its included in new list as well")
            
            workerNodes[i].lastExecutedTime.clear()
            workerNodes[i].lastExecutedTime.update(newLastExecutedTime)
            # print("for worker_id",workerNodes[i].worker_id,"it has",workerNodes[i].lastExecutedTime)

        return workerNodes

    def getIndexInWorkersArray(self,worker_id):
        for i in range(0,len(self.workers)) :
            # print(self.workers[i])
            if(self.workers[i].worker_id == worker_id):
                return i

    def getIndexInFunctionsArray(self,function_id):
        for i in range(0,len(self.functions)) :
            if(self.functions[i].function_id == function_id):
                return i

    def getIndexInPackagesArray(self,package_id):
        for i in range(0,len(self.packages)) :
            if(self.packages[i].package_id == package_id):
                return i

    def addWorker(self,worker) :
        print("previous workers in total were :",len(self.workers))
        # print(worker)
        workerNodes = self.workers
        workerNodes.append(worker)
        self.workers = workerNodes #added in PasCh
        self.consitentHash.addWorker(worker.worker_id) #added in Consistent hash
        print("total workers are now :",len(self.workers))
    
    def removeWorker(self,worker_id) :
        print("previous workers in total were :",len(self.workers))
        workerNodes = self.workers
        newWorkerNodes = []
        for x in workerNodes:
            if(x.worker_id != worker_id) :
                newWorkerNodes.append(x)
        
        self.workers = newWorkerNodes #added in PasCh
        self.consitentHash.removeWorker(worker_id) #added in Consistent hash
        print("total workers are now :",len(self.workers))

    def assignWorker(self,function_id,timestamp):
        
        old_workerNodes = self.workers
        workerNodes = self.updateStaleWorkerData(old_workerNodes, timestamp)
        self.totalRequests = self.totalRequests + 1

        # if(len(workerNodes) == 0):
        #     return {"there are no worker nodes", None}

        function_object = self.functions[self.getIndexInFunctionsArray(function_id)]

        err, pkg0, pkg1 = function_object.getLargestPackage()
        # print("Pasch 143: ",err,pkg0,pkg1)
        if(err!= "") :
            print("No packages in function : ",function_id," to run !!!\n")
        
        elif(pkg1 == None) : # POWER OF 2
            # print("Only 1 package !!!!!!")
            pkg = pkg0

            package_object = self.packages[self.getIndexInPackagesArray(pkg)]

            # selectedWorker1,selectedWorker2 -> worker_id
            err1,selectedWorker1 = self.consitentHash.getWorker(pkg)
            err2,selectedWorker2 = self.consitentHash.getWorker(pkg+self.salt)
            # print("Selected workers for function,",function_id,"are :",selectedWorker1,selectedWorker2)

            load_1 = self.getLoad(selectedWorker1,timestamp)
            load_2 = self.getLoad(selectedWorker2,timestamp)
            # print("load1 :",load_1)
            # print("load2 :",load_2)

            #chooses the least loaded among 2 chosen worker nodes
            chosen_power_of_two_node = selectedWorker1
            if(load_1>load_2):
                chosen_power_of_two_node=selectedWorker2

            chosen_node_to_run = chosen_power_of_two_node   
            index_of_chosen_node_to_run = self.getIndexInWorkersArray(chosen_node_to_run) 

            if(self.getLoad(chosen_power_of_two_node,timestamp) >= self.threshold ):
                chosen_node_to_run = self.getLeastLoadedWorker(timestamp) # returns worker_id
                index_of_chosen_node_to_run=self.getIndexInWorkersArray(chosen_node_to_run)
            
            # DO: what if least loaded is also crossing threshold ??

            # all clear till here


            # increase its currentLoad, update caached packages, after all that update the workers array in Pasch
            # self.workerId = worker_id , self.threshold = threshold, self.currentLoad = 0
            # self.cachedPackages = [], self.lastExecutedTime = {}

            # calculate if biggest package was hit or missed

            finalTimeOfFunctionExecution = timestamp + function_object.function_size

            if(self.workers[index_of_chosen_node_to_run].lastExecutedTime.get(pkg) == None) :
                # first time caching pkg
                # print("First time importing on node :",self.workers[index_of_chosen_node_to_run].worker_id,"package: ",pkg)
                #hence totalTimeOfFunctionExecution remains same
                self.cacheMiss = self.cacheMiss + 1
            elif(self.workers[index_of_chosen_node_to_run].lastExecutedTime[pkg] + cacheCleanTime > timestamp) :
                # print("CACHE HIT ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :", pkg)
                #as cache is hit, we will remove largest packag's time from time of execution
                finalTimeOfFunctionExecution -= package_object.package_size
                self.cacheHits1 = self.cacheHits1 + 1
            else :
                # print("CACHE missed !!!! ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :",pkg)
                self.cacheMiss = self.cacheMiss + 1
            #DO : add the new function to execute in the worker.runningFunction list depending on cache hit or missed
            workerNodes[index_of_chosen_node_to_run].runningFunctions.append({"finish_time":finalTimeOfFunctionExecution,
                                                                            "function_id":function_object.function_id})
            
            #updating load
            workerNodes[index_of_chosen_node_to_run].currentLoad = len(workerNodes[index_of_chosen_node_to_run].runningFunctions)

            #updating the cache executed time for all imported packages including the biggest package
            # packages_imported contains array of package_id
            packages_imported = self.functions[self.getIndexInFunctionsArray(function_id)].function_imports 
            for i in range(0,len(packages_imported)):
                workerNodes[index_of_chosen_node_to_run].lastExecutedTime[packages_imported[i]] = timestamp

        
            #updating the changes in object
            self.workers = workerNodes

            return {"",workerNodes[index_of_chosen_node_to_run].worker_id}

        else : # POWER OF 3
            # print(">= 2 package !!!!!!")
            package_object0 = self.packages[self.getIndexInPackagesArray(pkg0)]
            package_object1 = self.packages[self.getIndexInPackagesArray(pkg1)]

            # selectedWorker1,selectedWorker2 -> worker_id
            err1,selectedWorker1 = self.consitentHash.getWorker(pkg0)
            err2,selectedWorker2 = self.consitentHash.getWorker(pkg1)
            err3,selectedWorker3 = self.consitentHash.getWorker(pkg0+self.salt)
            # print("Selected workers for function,",function_id,"are :",selectedWorker1,selectedWorker2,selectedWorker3)

            load_1 = self.getLoad(selectedWorker1,timestamp)
            load_2 = self.getLoad(selectedWorker2,timestamp)
            load_3 = self.getLoad(selectedWorker3,timestamp)
            
            # print("load1 :",load_1)
            # print("load2 :",load_2)
            # print("load3 :",load_3)

            #chooses the least loaded among 2 chosen worker nodes
            chosen_power_of_three_node = selectedWorker1
            chosen_node_load = load_1

            if(load_1>load_2):
                chosen_power_of_three_node=selectedWorker2
                chosen_node_load = load_2
            if(chosen_node_load>load_3):
                chosen_power_of_three_node=selectedWorker3
                chosen_node_load = load_3
            
            # print("chosen_power_OF_3:",chosen_power_of_three_node)
            
            chosen_node_to_run = chosen_power_of_three_node
            index_of_chosen_node_to_run = self.getIndexInWorkersArray(chosen_node_to_run) 

            if(self.getLoad(chosen_power_of_three_node,timestamp) >= self.threshold ):
                chosen_node_to_run = self.getLeastLoadedWorker(timestamp) # returns worker_id
                index_of_chosen_node_to_run=self.getIndexInWorkersArray(chosen_node_to_run)
            
            # DO: what if least loaded is also crossing threshold ??

            #DO : calculate finalTimeOfFunctionExecution assumptions for power of 3
            finalTimeOfFunctionExecution = timestamp + function_object.function_size

            if(self.workers[index_of_chosen_node_to_run].lastExecutedTime.get(pkg0) == None) :
                
                # print("First time importing on node :",self.workers[index_of_chosen_node_to_run].worker_id,"package: ",pkg0)
                if(self.workers[index_of_chosen_node_to_run].lastExecutedTime.get(pkg1) == None) :
                    
                    # print("First time importing on node :",self.workers[index_of_chosen_node_to_run].worker_id,"package: ",pkg1)
                    self.cacheMiss = self.cacheMiss + 1 # both cache missed but both are imported first time 

                elif(self.workers[index_of_chosen_node_to_run].lastExecutedTime[pkg1] + cacheCleanTime > timestamp) :
                    # print("CACHE HIT ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :", pkg1)
                    
                    # ONLY CONSIDERING P1
                    finalTimeOfFunctionExecution -= package_object1.package_size
                    self.cacheHits2 = self.cacheHits2 + 1
                    
                else :
                    # print("CACHE missed !!!! ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :",pkg1)
                    self.cacheMiss = self.cacheMiss + 1
                    
            elif(self.workers[index_of_chosen_node_to_run].lastExecutedTime[pkg0] + cacheCleanTime > timestamp) :
                # print("CACHE HIT ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :", pkg0)
                
                #as cache is hit for p0, we need not to see for p1 
                finalTimeOfFunctionExecution -= package_object0.package_size
                self.cacheHits1 = self.cacheHits1 + 1

            else :
                # print("CACHE missed !!!! ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :",pkg0)
                
                if(self.workers[index_of_chosen_node_to_run].lastExecutedTime.get(pkg1) == None) :
                    # first time caching pkg
                    # print("First time importing on node :",self.workers[index_of_chosen_node_to_run].worker_id,"package: ",pkg1)
                    self.cacheMiss = self.cacheMiss + 1 # both cache missed but both are imported first time 

                elif(self.workers[index_of_chosen_node_to_run].lastExecutedTime[pkg1] + cacheCleanTime > timestamp) :
                    # print("CACHE HIT ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :", pkg1)
                    #as cache is hit, we will remove largest packag's time from time of execution
                    finalTimeOfFunctionExecution -= package_object1.package_size
                    
                    self.cacheHits2 = self.cacheHits2 + 1
                else :
                    # print("CACHE missed !!!! ON NODE :",self.workers[index_of_chosen_node_to_run].worker_id, "for package :",pkg1)
                    self.cacheMiss = self.cacheMiss + 1

            # DO : add the new function to execute in the worker.runningFunction list depending on cache hit or missed
            workerNodes[index_of_chosen_node_to_run].runningFunctions.append({"finish_time":finalTimeOfFunctionExecution,
                                                                            "function_id":function_object.function_id})
            
            #updating load
            workerNodes[index_of_chosen_node_to_run].currentLoad = len(workerNodes[index_of_chosen_node_to_run].runningFunctions)

            # updating the cache executed time for all imported packages including the biggest package
            # packages_imported contains array of package_id
            packages_imported = self.functions[self.getIndexInFunctionsArray(function_id)].function_imports 
            for i in range(0,len(packages_imported)):
                workerNodes[index_of_chosen_node_to_run].lastExecutedTime[packages_imported[i]] = timestamp

        
            #updating the changes in object
            self.workers = workerNodes
            # print({"",workerNodes[index_of_chosen_node_to_run].worker_id})
            return {"",workerNodes[index_of_chosen_node_to_run].worker_id}






