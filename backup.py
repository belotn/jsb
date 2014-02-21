import xml.etree.ElementTree as ET
import importlib
import sys
import os
if len(sys.argv) > 1: 
	xmlfile	= sys.argv[1]
else:
	xmlfile = os.path.normpath( os.getcwd() + "/backup.xml")

print(xmlfile)
tree = ET.parse(xmlfile)
root = tree.getroot()

modIncluded = []

configuration = root.find('configuration')

if configuration.findall('lib'):
	for inc in configuration.findall('lib'):
		modIncluded.append ( importlib.import_module(inc.text ) )

		
def FindFunction(name):
	for mod in modIncluded:
		if name in dir(mod):
			return mod.__dict__[name]

backups = root.find('backups')
sources = root.find('sources')
destination = root.find('destinations')


for bck in backups:
	source = bck.get('source')
	dest = bck.get('destination')
	nodeSource = sources.find("source[@name='" + source + "']")
	nodeDestination = destination.find("destination[@name='" + dest + "']")
	fun = FindFunction("Source_" + nodeSource.get('type').capitalize())
	file = fun(nodeSource,configuration)
	fun=FindFunction("Destination_" + nodeDestination.get('type').capitalize())
	fun(file, nodeDestination,configuration)
	
	

		
	