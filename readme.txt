README
======

HPC Traffic Sim

A traffic simulator, using a grid of computers.
The simulator is loosely based on a Cellular Automata approach, where each section of a road lane,
behaves as a distinct cell within the overall road network.

Dependencies:
=============
- Python 2.7.x
- Python easy install
- pyro:  easy_install pyro

note: pyro 3.11 seems to behave better between Ubuntu (10) <> Windows (7)
  windows: pyro-ns + broker + monitor  (processor error!)
  ubuntu: 1 x processor
  note: start the ubuntu processor last!

env vars:
    export PYRO_LOGLEVEL=DEBUG
    export PYRO_TRACELEVEL=3
    

Unused dependencies:
====================
zeromq (not used in the end):
- zeromq:		http://www.zeromq.org
- Python zeromq:  easy_install pyzmq
- git (for the zeromq samples) - http://code.google.com/p/msysgit/downloads/list?can=3&q=official+Git

