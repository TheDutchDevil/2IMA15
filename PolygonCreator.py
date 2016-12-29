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
		v = str(math.ceil((int(pred[0])+int(succ[0]))/2))+" "+str(math.ceil((int(pred[1])+int(succ[1]))/2))
		l.insert(p, v)
	
	return l

def makeRectangloid(x, y, size, general=0):
#Creates x*y virtual squares of size*size and puts a point randomly in all of the 2x+2y-4 outer ones
	l=[str(2*x+2*y-4)]
	if(general==1):
		xpool1=list(range(0,size))
		xpool2=list(range(size,(x-1)*size))
		xpool3=list(range((x-1)*size,x*size))
		ypool1=list(range(0,size))
		ypool2=list(range(size,(y-1)*size))
		ypool3=list(range((y-1)*size,y*size))
		if(x>size or y>size):
			print("Size too small!")
			return []

	for i in range(1, y, 1):
		ny = random.randrange((i-1)*size,(i)*size)

		if(general==1):
			nx = random.choice(xpool1)
			xpool1.remove(nx)
			if(i==1):
				ypool1.remove(ny)
			else:
				ypool2.remove(ny)
		else:
			nx = random.randrange(0,size)
		
		l.append(str(nx)+" "+str(ny))

	for i in range(1, x, 1):
		nx = random.randrange((i-1)*size,(i)*size)
		
		if(general==1):
			ny = random.choice(ypool3)
			ypool3.remove(ny)
			if(i==1):
				nx = random.choice(xpool1) #Redundant
				xpool1.remove(nx)
			else:
				xpool2.remove(nx)
		else:
			ny = (y-1)*size + random.randrange(0,size)
		l.append(str(nx)+" "+str(ny))

	for i in range(y, 1, -1):
		if(general==1):
			nx = random.choice(xpool3)
			xpool3.remove(nx)
			if(i==y):
				ny = random.choice(ypool3)
				ypool3.remove(ny)
			else:
				while True:
					ny = random.randrange((i-1)*size,(i)*size)
					if(ny in ypool2):
						break
				ypool2.remove(ny)
		else:
			nx =(x-1)*size + random.randrange(0,size)
			ny = random.randrange((i-1)*size,(i)*size)
		l.append(str(nx)+" "+str(ny))

	for i in range(x, 1, -1):
		if(general==1):
			ny = random.choice(ypool1)
			ypool1.remove(ny)
			if(i==x):
				nx = random.choice(xpool3)
				xpool3.remove(nx)
			else:
				while True:
					nx = random.randrange((i-1)*size,(i)*size)
					if(nx in xpool2):
						break
				xpool2.remove(nx)
		else:
			nx = random.randrange((i-1)*size,(i)*size)
			ny = random.randrange(0,size)
		l.append(str(nx)+" "+str(ny))

	#Test for general position:
	'''
	xs=[]
	ys=[]
	for e in l:
		if(len(e.split())>1):
			xs.append(int(e.split()[0]))
			ys.append(int(e.split()[1]))
	xs.sort()
	ys.sort()
	print(xs)
	print(ys)
	'''
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