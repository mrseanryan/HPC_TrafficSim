#monitor process - allows us to monitor the grid

import Pyro.core
import Pyro.naming

class Monitor(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
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

    def UpdateTraffic(self, model):
        self._updateDisplay()

    def _updateDisplay(self):
        #TODO make a web server
        #maybe use HTML5 to draw ?  or else Google maps...
        print "________________________"
        #build a reverse lookup, so we can print by regions:
        dictRegionToPID = dict()
        for PID in self.dictPIDtoRegions.iterkeys():
            regions = self.dictPIDtoRegions[PID]            
            for region in regions:
                dictRegionToPID[region] = PID

        for region in dictRegionToPID.iterkeys():
            print region.regionName + " - proc" + str(dictRegionToPID[region])


def main():
    mon = Monitor()    

    #NOT threading the monitor - simpler + more efficient to just have processors push their updates

    Pyro.core.initServer()
    ns=Pyro.naming.NameServerLocator().getNS()
    daemon=Pyro.core.Daemon()
    daemon.useNameServer(ns)
    uri=daemon.connect(mon,"monitor")
    print "monitor is listening..."
    daemon.requestLoop()

if __name__=="__main__":
    main()






