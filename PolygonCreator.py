import random
import string
import math
#import numpy as np

def makeTestPolygon(n, min, max):
#Creates n amount of points in between <min>,<min> and <max>,<max>. Extremely unlikely to be simple, should not be used for anything but testing.
	l=[str(n)]
	for i in range(n):
		l.append(str(random.randrange(min,max))+" "+str(random.randrange(min,max)))
	return l

def makeChallengePolygon(n, inrad, outrad, pierce=0, red=0):
#Creates a challenge (double quarter circle shark teeth) polygon with 4*<n>+2+red points that are on circles with radius inrad and outrad with the origin as its center
#Extra parameter piercedetermines howmuch the inner and outer teeth overlap (may cause overlap i.e. non-simple polygon!)
#Extra parameter red adds a number of redundant vertices at the end
	l=[str(4*n+2+red)]
	for i in range(0, n+1, 1):
		a = i*(math.pi*0.5/n)
		l.append(str(math.ceil(math.cos(a)*(inrad+outrad)/(2+pierce)))+" "+str(math.ceil(math.sin(a)*(inrad+outrad)/(2+pierce))))
		l.append(str(math.ceil(math.cos(a)*outrad))+" "+str(math.ceil(math.sin(a)*outrad)))

	for i in range(n, -1, -1):
		a = (i+0.5)*(math.pi*0.5/n)
		l.append(str(math.ceil(math.cos(a)*(inrad+outrad)/(2-pierce)))+" "+str(math.ceil(math.sin(a)*(inrad+outrad)/(2-pierce))))
		l.append(str(math.ceil(math.cos(a)*inrad))+" "+str(math.ceil(math.sin(a)*inrad)))
	
	for i in range(red):
		p = random.randrange(2,len(l)-1)
		pred = l[p-1].split()
		succ = l[p].split()
		print(pred)
		print(succ)
		v = str(math.ceil((int(pred[0])+int(succ[0]))/2))+" "+str(math.ceil((int(pred[1])+int(succ[1]))/2))
		print(v)
		l.insert(p, v)
	
	return l


def writePoints(poly): #Writes a list poly at [output]_#####.txt with # some random characters. Could technically overwrite an older one I guess, but not likely
	loc = 'E:\\2IMA15\\' #Change as needed, remember to put \\ at the end
	output='polygon' 
	stuff = "".join(random.choice(string.hexdigits) for _ in range(5)) #Random suffix
	print("Saving "+loc+output+"_"+stuff+".txt ...")

	with open(loc+output+"_"+stuff+".txt", 'w') as f:
		for i in poly:
			f.write(str(i)+"\n")
		f.closed