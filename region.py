#model the regions, and their connections

import csv
import os
import Pyro.core
import random

CONST_CONSUME_RATIO = 0.10

class Region(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)

        self.regionName = ""
        self.lattitude = ""
        self.longitude = ""
        self.capacity = 0
        self.numVehicles = 0
        self.dictFromRegionToVehicles = dict() #used to print waiting traffic from regions to this region

    def ConsumeVehicles(self):
        numVehiclesToConsume = random.randrange(float(self.capacity) * CONST_CONSUME_RATIO)
        #reduce our vehicle count, but avoid going negative:
        if self.numVehicles >= numVehiclesToConsume:
            #self.lattitude = "x"
            print self.regionName + "xxx numVehicles before: " + str(self.numVehicles)
            self.numVehicles = self.numVehicles - numVehiclesToConsume
            print self.regionName + "xxx numVehicles after: " + str(self.numVehicles)
            print self.toString()
        else:
            self.numVehicles = 0

    def TryAcceptVehicles(self, fromRegion, numVehiclesToReceive):

        #return False #xxx        
        #import pdb
        #pdb.set_trace()
        if self.numVehicles + numVehiclesToReceive <= self.capacity:
            self.numVehicles = self.numVehicles + numVehiclesToReceive
            self.dictFromRegionToVehicles[fromRegion] = 0
            return True
        else:
            self.dictFromRegionToVehicles[fromRegion] = numVehiclesToReceive
            return False

    @staticmethod
    def Load(csvFilepath):
        print "Loading regions from file " + csvFilepath + " ..."

        reader = csv.reader(open(csvFilepath, "rb"))
        regions = []
        for row in reader:
            if len(row) == 0:
                continue
            region = Region()
            region.regionName = row[0].strip()
            #skip comment line:
            if region.regionName[0] == '#':
                continue
            region.lattitude = row[1].strip()
            region.longitude = row[2].strip()
            region.capacity = row[3].strip()
            regions.append(region)
            region.numVehicles = float(region.capacity) - random.randrange(float(region.capacity) * CONST_CONSUME_RATIO)

        return regions

    def toString(self):
        regionStr = self.regionName + " at " + self.lattitude + " " + self.longitude + " - " + str(self.numVehicles) + " vehicles of capacity = " + str(self.capacity) + " " + self._getPercentFullStr() + "% full"
        regionStr = regionStr + os.linesep
        #show any waiting traffic:
        for regionFrom in self.dictFromRegionToVehicles.iterkeys():
            regionStr = regionStr + "\t\t" + regionFrom.regionName + " (" + str(self.dictFromRegionToVehicles[regionFrom]) + ") =>"
            regionStr = regionStr + os.linesep

        return regionStr

    def _getPercentFullStr(self):
        return str(float(self.numVehicles) / float(self.capacity))

class RegionModel(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
    
    def __init__(self, regions):
        Pyro.core.ObjBase.__init__(self)
        print "RegionModel() *-*-*-*-*-*-*-*-*-*-*-*-"
        self.regions = regions
        self.dictRegionToNeighbours = dict()


    #needed to get remote access to the Region objects
    def GetNeighbours(self, regionName):
        return self.dictRegionToNeighbours[regionName]

    #needed to get remote access to the Region objects
    def GetRegions(self):
        regionProxies = []
        for region in self.regions:
            regionProxies.append(region.getAttrProxy())
        return regionProxies
        #return self.regions

    @staticmethod
    def Load(csvPathRegions, csvPathRegionConnections):
        regions = Region.Load(csvPathRegions)
        model = RegionModel(regions)
        model._loadConnections(csvPathRegionConnections)
        return model

    def _loadConnections(self, csvFilepath):
        print "Loading connections from file " + csvFilepath + " ..."
        reader = csv.reader(open(csvFilepath, "rb"))
        regions = []
        for row in reader:
            if len(row) == 0:
                continue
            cxnStart = row[0].strip()
            #skip comment line:
            if cxnStart[0] == '#':
                continue
            if len(cxnStart) == 0:
                continue
            cxnEnd = row[1].strip()
            self._addConnection(cxnStart, cxnEnd)
            #also add in the opposite direction:
            self._addConnection(cxnEnd, cxnStart)

    def _addConnection(self, cxnStart, cxnEnd):
        if cxnStart not in self.dictRegionToNeighbours.iterkeys():
            self.dictRegionToNeighbours[cxnStart] = []
        self.dictRegionToNeighbours[cxnStart].append(cxnEnd)

    def toString(self):
        strMessage = "regions in the model:" + os.linesep
        for region in self.regions:
            strMessage = strMessage + region.toString() + os.linesep
        strMessage = strMessage + "connections:" + os.linesep
        for cxnStart in self.dictRegionToNeighbours.iterkeys():
            strMessage = strMessage + cxnStart + " => "
            strMessage = strMessage + ",".join(self.dictRegionToNeighbours[cxnStart]) 
            strMessage = strMessage + os.linesep
        return strMessage

def main():
    print "__________________________________________________________________"
    print "running unit test for Region class ..."
    regions = Region.Load("regions.csv")
    for region in regions:
        print region.toString()

    print "__________________________________________________________________"
    print "running unit test for RegionModel class ..."
    model = RegionModel.Load("regions.csv", "region_connections.csv")
    print model.toString()

if __name__=="__main__":
    main()







