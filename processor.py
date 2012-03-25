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

		while(self.IsRunning and self.proc.state == CONST_STATE_RUNNING):
			_simulateAstep()

	def _sendTraffic(self):
		#xxx TODO
		print "sending traffic ..."

	def _simulateAstep(self):
		print "traffic sim running ..."
		self._sendTraffic()
		sleep(1.0)

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
		self.otherPIDproxies = dict()

	def __del__(self):
		self.unregister()

	def _calculateTargetRegionsPerProc(self):
		#xxx TODO
		return 1

	def _getOtherProc(self, otherPID):
		#use the ns to find the other processor
		#for perf, we cache the other processor proxy, to avoid contacting the nameserver repeatedly
		if otherPID not in self.otherPIDproxies.iterkeys():
			self.otherPIDproxies[otherPID] = Pyro.core.getProxyForURI("PYRONAME://proc" + str(otherPID))
		return self.otherPIDproxies[otherPID]

	#give all our regions to the other processors, so they can work on them (as we are exiting)
	def _giveRegionsToOtherProcessors(self):
		#xxx TODO
		print "giving regions to other processors..."

	def _register(self):
		#use the pyro nameserver to locate the broker
		self.broker = Pyro.core.getProxyForURI("PYRONAME://broker")

		#registerResult = self.broker.register()
		(self.myPID, self.otherPIDs) = self.broker.register()
		print "my PID = " + str(self.myPID)
		print "other active PIDs: "
		for otherPID in self.otherPIDs:
			print str(otherPID) + ", "

	 	self.model = self.broker.getModel()
		#TODO copy the model locally, for performance

		print "retrieved model from broker: "
		print self.model.toString()

	#this processor should have the given number of regions, or less.
	#any extra regions should be returned, so that the calling processor can take them.
	#
	#note: return variables are named to suit the client!
	def TakeWork(self, targetNumRegionsPerProc): #returns (myNewRegions, otherPIDregions)
		#xxx TODO
		raise Exception("not impl!")

	#take work from existing processors.
	#xxx - might need to move this to the thread ?
	def TakeWorkFromOtherProcessors(self):
		targetNumRegionsPerProc = self._calculateTargetRegionsPerProc()
		for otherPID in self.otherPIDs:
			otherProc = self._getOtherProc(otherPID)
			(myNewRegions, otherPIDregions) = otherProc.TakeWork(targetNumRegionsPerProc)
			#update this procs regions:
			self.myRegions.append(myNewRegions)
			#update our map of other procs regions: (so we know where to send traffic for region X)
			self.Update(otherPID, otherPIDregions)
		#finally, tell all the other procs what regions we have taken:
		for otherPID in self.otherPIDs:
			otherProc = self._getOtherProc(otherPID)
			otherProc.Update(self.myPID, self.myRegions)

	#update our map of PID => Regions (so we know where to send traffic for region X)
	def Update(self, otherPID, otherPIDregions):
		raise Exception("TODO xxx")

	def unregister(self):
		self.threaded.stop()
		self.otherPIDproxies = dict() #clear refs to other processors
		self.broker.unregister(self.myPID)
		self._giveRegionsToOtherProcessors()

def main():
	proc = Processor()	

	#start a new thread, to perform the traffic algorithm
	threaded = ThreadedProcessor(proc)
	threaded.start()

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

	#server thread, that processes requests:
	try:
		print "processing " + str(proc.myPID) + " is listening ..."
		daemon.requestLoop()
	except:
		#threaded.stop()
		proc.unregister()
		pass

if __name__=="__main__":
    main()







