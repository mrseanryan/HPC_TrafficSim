#broker.py

#import Pyro4
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
        otherPIDs = []
        for PID in self.activePIDs:
            otherPIDs.append(PID)
        self.activePIDs.append(newPID)
        return (newPID, otherPIDs)
    def getModel(self):
        return self.model
    def getNextPID(self):
        self.nextPID = self.nextPID + 1
        return self.nextPID

    #to make an object remotable, we need to register it with the pyro daemon
    def registerObjectsWithDaemon(self,daemon):
        daemon.connect(self.model, "model")
        for region in self.model.regions:
            daemon.connect(region)

    def unregister(self, PID):
        print "PID " + str(PID) + " is un-registering"
        self.activePIDs.remove(PID)

def main():
    Pyro.core.initServer()
    ns=Pyro.naming.NameServerLocator().getNS()
    daemon=Pyro.core.Daemon()
    daemon.useNameServer(ns)
    broker = Broker()
    uri=daemon.connect(broker,"broker")

    daemon.connect(broker.model,"model")

    for region in broker.model.regions:
        daemon.connect(region)

    #xxx broker.registerObjectsWithDaemon(daemon)
    print "broker is listening..."
    daemon.requestLoop()

if __name__=="__main__":
    main()

