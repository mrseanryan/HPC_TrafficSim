#model the regions, and their connections

import csv

class Region:
	def __init__(self):
		self.regionName = ""
		self.lattitude = ""
		self.longitude = ""
		self.capacity = 0

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

		return regions

	def toString(self):
		return self.regionName + " at " + self.lattitude + " " + self.longitude + " - capacity = " + str(self.capacity) + " vehicles."

class RegionModel:
	
	def __init__(self, regions):
		self.regions = regions
		self.dictRegionToNeighbours = dict()

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
		print "regions in the model:"		
		for region in self.regions:
			print region.toString()
		print "connections:"
		for cxnStart in self.dictRegionToNeighbours.iterkeys():
			strMessage = cxnStart + " => "
			strMessage = strMessage + ",".join(self.dictRegionToNeighbours[cxnStart]) 
			print strMessage				

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







