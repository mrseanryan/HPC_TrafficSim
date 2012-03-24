#processor

import Pyro.core

from threading import Thread
from time import sleep

class ThreadedProcessor(Thread):
	def __init__ (self,proc):
		Thread.__init__(self)
		self.proc = proc
		self.IsRunning = True

	def __del__(self):
		self.stop()

	#threaded method
	def run(self):
		while(self.IsRunning):
			print "simulating traffic..."
			sleep(1.0)

	def stop(self):
		self.IsRunning = False

class Processor(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		self._register()
		self.threaded = None

	def __del__(self):
		self.unregister()

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
		#todo copy the model locally, for performance

		print "retrieved model from broker: "
		print self.model.toString()

	def unregister(self):
		self.threaded.IsRunning = False
		self.broker.unregister(self.myPID)

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
	#now register with the nameserver, so that newer processors can find me
	uri=daemon.connect(proc,"proc" + str(proc.myPID))

	#server thread, that processes requests:
	try:
		print "processing " + str(proc.myPID) + " is listening ..."
		daemon.requestLoop()
	except:
		threaded.stop()
		pass

if __name__=="__main__":
    main()



#take work off the other existing processors

#tell the other processors what regions we are processing

#not needed - tell the other processors that we are ready

#send and receive traffic

#exiting:

#un-register from the broker

#[pyro does this] - un-register from the nameserver

#give my regions to the other processors

#exit









