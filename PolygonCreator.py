import random
import string
import numpy as np

def makePolygon(size, min, max):
	l=[str(size)]
	for i in range(size):
		l.append(str(random.randrange(min,max))+" "+str(random.randrange(min,max)))
	return l


def writePoints(poly): #writes a list poly at [output]_#####.txt with # some random characters. Could technically overwrite an older one I guess, but not likely
	loc = 'E:\\2IMA15\\' #Change as needed, remember to put \\ at the end
	output='polygon' 
	stuff = "".join(random.choice(string.hexdigits) for _ in range(5)) #Random suffix
	print("Saving "+loc+output+"_"+stuff+".txt ...")

	with open(loc+output+"_"+stuff+".txt", 'w') as f:
		for i in poly:
			f.write(str(i)+"\n")
		f.closed