#broker.py

import Pyro.core
import Pyro.naming

class Broker(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		self.nextPID = 0        	
	def register(self): #returns new PID for the client
		return self.getNextPID()
	def getNextPID(self):
		self.nextPID = self.nextPID + 1
		return self.nextPID

def main():
    Pyro.core.initServer()
    ns=Pyro.naming.NameServerLocator().getNS()
    daemon=Pyro.core.Daemon()
    daemon.useNameServer(ns)
    uri=daemon.connect(Broker(),"broker")
    daemon.requestLoop()

if __name__=="__main__":
    main()
