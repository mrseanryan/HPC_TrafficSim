#processor

import Pyro.core

#use the pyro nameserver to locate the broker
broker = Pyro.core.getProxyForURI("PYRONAME://broker")

myPID = broker.register()

print "my PID = " + str(myPID)

#now register with the nameserver, so that newer processors can find me

#take work off the other existing processors

#tell the other processors what regions we are processing

#not needed - tell the other processors that we are ready

#send and receive traffic

#exiting:

#un-register from the broker

#[pyro does this] - un-register from the nameserver

#give my regions to the other processors

#exit

