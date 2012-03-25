#processor

import Pyro.core

from threading import Thread
from time import sleep

CONST_STATE_STARTING = 1
CONST_STATE_RUNNING = 2
CONST_STATE_EXITING = 3

class ThreadedProcessor(Thread):
    def __init__ (self,proc):
        Thread.__init__(self)
        self.proc = proc
        self.IsRunning = True

    def __del__(self):
        self.stop()

    #threaded method
    def run(self):
        while(self.IsRunning and self.proc.state == CONST_STATE_STARTING):
            print "traffic sim waiting for startup to complete ..."
            sleep(1.0)

        iStep = 0
        CONST_MONITOR_UPDATE_EVERY_STEP = 5
        while(self.IsRunning and self.proc.state == CONST_STATE_RUNNING):
            self._simulateAstep()
            iStep = iStep + 1
            if iStep == CONST_MONITOR_UPDATE_EVERY_STEP:
                iStep = 0
                self._updateMonitor()

    def _sendTraffic(self):
        #xxx TODO
        print "sending traffic ..."

    def _simulateAstep(self):
        print "traffic sim running ..."
        self._sendTraffic()
        sleep(1.0)

    def _updateMonitor(self):
        print "updating the monitor ..."
        self.proc.UpdateMonitor()

    def TryToReceiveTraffic(self, numVehicles):
        #xxx TODO
        return False

    def stop(self):
        self.IsRunning = False

class Processor(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
        self.state = CONST_STATE_STARTING #xxx if deadlock during startup, then try skip straight to RUNNING state
        self._register()
        self.threaded = None
        self.myRegions = [] #the regions that this processor should process
        self.dictPIDtoProxy = dict()
        self.dictRegiontoPID = dict()

    def __del__(self):
        self.unregister()

    def _calculateTargetRegionsPerProc(self):
        numRegionsPerProc = len(self.model.regions) / (1 + len(self.otherPIDs))
        return numRegionsPerProc

    def _getOtherProc(self, otherPID):
        #use the ns to find the other processor
        #for perf, we cache the other processor proxy, to avoid contacting the nameserver repeatedly
        if otherPID not in self.dictPIDtoProxy.iterkeys():
            self.dictPIDtoProxy[otherPID] = Pyro.core.getProxyForURI("PYRONAME://proc" + str(otherPID))
        return self.dictPIDtoProxy[otherPID]

    #give all our regions to the other processors, so they can work on them (as we are exiting)
    def _giveRegionsToOtherProcessors(self):
        print "giving regions to other processors..."
        #xxx TODO

    def _register(self):
        #use the pyro nameserver to locate the broker
        self.broker = Pyro.core.getProxyForURI("PYRONAME://broker")

        #also locate the monitor process:
        self.monitor = Pyro.core.getProxyForURI("PYRONAME://monitor")

        #registerResult = self.broker.register()
        (self.myPID, self.otherPIDs) = self.broker.register()
        print "my PID = " + str(self.myPID)
        print "other active PIDs: "
        for otherPID in self.otherPIDs:
            print str(otherPID) + ", "

        self.model = self.broker.getModel()
        #TODO copy the model locally, for performance - but could introduce data sync issues

        print "retrieved model from broker: "
        print self.model.toString()

    #this processor should have the given number of regions, or less.
    #any extra regions should be returned, so that the calling processor can take them.
    #
    def GiveWork(self, targetNumRegionsPerProc): #returns (regionsGiven, otherPIDregions)
        regionsGiven = []
        iRegion = 1
        for region in self.myRegions:
            if iRegion > targetNumRegionsPerProc:
                #give the region to the other processor:
                regionsGiven.append(region)
            iRegion = iRegion + 1
        #remove the taken regions from myRegions:
        for region in regionsGiven:
            self.myRegions.remove(region)
        #tell the monitor:
        self.monitor.Update(self.myPID, self.myRegions)
        #return regions we are giving to the calling processor + list of this processors regions (to avoid a further call)
        return (regionsGiven, self.myRegions)

    def Run(self):
        self.state = CONST_STATE_RUNNING

    #take work from existing processors.
    def TakeWorkFromOtherProcessors(self):
        targetNumRegionsPerProc = self._calculateTargetRegionsPerProc()
        print "targetNumRegionsPerProc = " + str(targetNumRegionsPerProc)

        #assumption: only one processor joining or leaving at a time!
        if len(self.otherPIDs) == 0:
            #this is the first processor, so just take all the regions
            for region in self.model.regions:
                self.myRegions.append(region)
 
        for otherPID in self.otherPIDs:
            otherProc = self._getOtherProc(otherPID)
            (myNewRegions, otherPIDregions) = otherProc.GiveWork(targetNumRegionsPerProc)
            #update this procs regions:
            self.myRegions = myNewRegions
            #update our map of other procs regions: (so we know where to send traffic for region X)
            self.Update(otherPID, otherPIDregions)
        #finally, tell all the other procs what regions we have taken:
        for otherPID in self.otherPIDs:
            otherProc = self._getOtherProc(otherPID)
            otherProc.Update(self.myPID, self.myRegions)
        #tell the monitor:
        self.monitor.Update(self.myPID, self.myRegions)

    #update our map of PID => Regions (so we know where to send traffic for region X)
    def Update(self, otherPID, otherPIDregions):
        for region in otherPIDregions:
            self.dictRegiontoPID[otherPID] = region

    def UpdateMonitor(self):
        #todo make this more efficient - by just a partial update by region
        self.monitor.UpdateTraffic(self.model)

    def unregister(self):
        self.threaded.stop()
        self.dictPIDtoProxy = dict() #clear refs to other processors
        self.broker.unregister(self.myPID)
        self._giveRegionsToOtherProcessors()

def main():
    proc = Processor()    

    #start a new thread, to perform the traffic algorithm
    threaded = ThreadedProcessor(proc)
    threaded.start()

    #server thread, that processes requests:
    try: #try in order to stop the thread on exception
        proc.threaded = threaded    

        #register this proc, so that other procs can reach it:
        Pyro.core.initServer()
        ns=Pyro.naming.NameServerLocator().getNS()
        daemon=Pyro.core.Daemon()
        daemon.useNameServer(ns)
        #now register with the nameserver, so that other (older + newer) processors can find me
        uri=daemon.connect(proc,"proc" + str(proc.myPID))

        #hook up the new processor: (only AFTER it is registered with nameserver)
        proc.TakeWorkFromOtherProcessors()

        print "Go to running state"

        proc.Run()

        print "processing " + str(proc.myPID) + " is listening ..."
        daemon.requestLoop()
    except:
        threaded.stop()
        proc.unregister()
        pass

if __name__=="__main__":
    main()







