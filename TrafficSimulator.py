#the actual Traffic simulation algorithm
#
#uses Cellular Automata approach to simulating traffic as distinct cells that have simple properties.
#the properties are all updated at each step of the simulation.

import random

CONST_SENDING_RATIO = 0.02


class TrafficSimulator:
    def __init__(self, proc):
        self.iStep = 0
        self.proc = proc
        self.dictRouteToNumVehicles = dict()

    def SimulateAstep(self):
        CONST_MONITOR_UPDATE_EVERY_STEP = 5
        self.iStep = self.iStep + 1
        self._simulateAstep()
        self._updateModel()
        if self.iStep == CONST_MONITOR_UPDATE_EVERY_STEP:
            self.iStep = 0
            self._updateMonitor()

    def _TrySendTraffic(self, fromRegion):
        print "sending traffic ..."
        #try to send traffic from given region, to its neighbours:
        neighbours = self.proc.model.GetNeighbours(fromRegion.regionName)
        for neighbourName in neighbours:
            route = fromRegion.regionName + "=>" + neighbourName
            
            neighbour = None
            for region in self.proc.model.GetRegions():
                if region.regionName == neighbourName:
                    neighbour = region
                    break
            if neighbour == None:
                raise Exception("could not find neighbour " + neighbourName)

            #see are we already sending vehicles on this route:
            numVehiclesToSend = 0
            if route in self.dictRouteToNumVehicles.iterkeys():
                numVehiclesToSend = self.dictRouteToNumVehicles[route]
            if numVehiclesToSend == 0:
                numVehiclesToSend = random.randrange(float(fromRegion.capacity) * CONST_SENDING_RATIO)
            if not neighbour.TryAcceptVehicles(fromRegion, numVehiclesToSend):
                #we will try again next step
                self.dictRouteToNumVehicles[route] = numVehiclesToSend
            else:
                self.dictRouteToNumVehicles[route] = 0
                print "sent " + str(numVehiclesToSend) + " vehicles on route " + route

    def _simulateAstep(self):
        print "traffic sim running ..."
        for region in self.proc.myRegions:
            region.ConsumeVehicles()
            self._TrySendTraffic(region)

    #the model is remotable, but the regions are serialized.
    #so we need to update the model's regions.
    #TODO - find a way to also remote the regions ...
    #using daemon.connect() caused an access error
    def _updateModel(self):
        print "updating model ..."

    def _updateMonitor(self):
        print "updating the monitor ..."
        self.proc.UpdateMonitor()



