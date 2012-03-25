#monitor process - allows us to monitor the grid

import Pyro.core
import Pyro.naming

class Monitor(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)

        #todo - make this be dictRegionToPID
        self.dictPIDtoRegions = dict()

    def Update(self, PID, myRegions):
        #update the other PIDs:
        for otherPID in self.dictPIDtoRegions.iterkeys():
            otherRegions = self.dictPIDtoRegions[otherPID]
            for region in myRegions:
                if region in otherRegions:
                    otherRegions.remove(region)
        self.dictPIDtoRegions[PID] = myRegions
        
        self._updateDisplay()

    def UpdateTrafficModel(self):
        self._updateDisplay()

    def _updateDisplay(self):
        #TODO make a web server
        #maybe use HTML5 to draw ?  or else Google maps...
        print "________________________"

        #show which processor owns what regions:
        for PID in self.dictPIDtoRegions:
            strMessage = "proc" + str(PID) + " processing regions: "
            for region in self.dictPIDtoRegions[PID]:
                strMessage = strMessage + region.regionName + ", "
            print strMessage

        #show model state: (traffic details)
        print self.model.toString()

def main():
    mon = Monitor()    

    #NOT threading the monitor - simpler + more efficient to just have processors push their updates

    try:
        Pyro.core.initServer()
        ns=Pyro.naming.NameServerLocator().getNS()
        daemon=Pyro.core.Daemon()
        daemon.useNameServer(ns)
        uri=daemon.connect(mon,"monitor")

        mon.model = Pyro.core.getProxyForURI("PYRONAME://model")

        print "monitor is listening..."
        daemon.requestLoop()
    except:
        daemon.disconnect(mon)    
        pass

if __name__=="__main__":
    main()






