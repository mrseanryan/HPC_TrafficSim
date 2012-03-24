#broker.py

import Pyro.core
import Pyro.naming

from region import *

class Broker(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		self.nextPID = 0        
		self.model = RegionModel.Load("regions.csv", "region_connections.csv")
		self.activePIDs = []
	def register(self): #returns new PID for the client, otherPIDs
		newPID = self.getNextPID()
		print "registering new PID " + str(newPID)
		self.activePIDs.append(newPID)
		return (newPID, self.activePIDs)
		#return newPID	
	def getModel(self):
		return self.model
	def getNextPID(self):
		self.nextPID = self.nextPID + 1
		return self.nextPID

	def unregister(self, PID):
		print "PID " + str(PID) + " is un-registering"
		self.activePIDs.remove(PID)

def main():
    Pyro.core.initServer()
    ns=Pyro.naming.NameServerLocator().getNS()
    daemon=Pyro.core.Daemon()
    daemon.useNameServer(ns)
    uri=daemon.connect(Broker(),"broker")
    print "broker is listening..."
    daemon.requestLoop()

if __name__=="__main__":
    main()

