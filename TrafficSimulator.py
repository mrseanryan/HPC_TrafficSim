#the actual Traffic simulation algorithm
#
#uses Cellular Automata approach to simulating traffic as distinct cells that have simple properties.
#the properties are all updated at each step of the simulation.

class TrafficSimulator:
    def __init__(self, proc):
        self.iStep = 0
        self.proc = proc

    def SimulateAstep(self):
        CONST_MONITOR_UPDATE_EVERY_STEP = 5
        self.iStep = self.iStep + 1
        self._simulateAstep()
        if self.iStep == CONST_MONITOR_UPDATE_EVERY_STEP:
            self.iStep = 0
            self._updateMonitor()

    def _sendTraffic(self):
        #xxx TODO
        print "sending traffic ..."

    def _simulateAstep(self):
        print "traffic sim running ..."
        self._sendTraffic()

    def _updateMonitor(self):
        print "updating the monitor ..."
        self.proc.UpdateMonitor()

    def TryToReceiveTraffic(self, numVehicles):
        #xxx TODO
        return False

