
#
# This program currently only actually connects some given list of points
#

import os
import matplotlib as sdf
import matplotlib.pyplot as plt
import matplotlib.colors as colors
def writeLine(line, i):
    if i==1:
        f.write(str(line)+'\n')
    else:
        f.write(str(line)+" ")

def makeDict(cont, dest): #Reads all lines from 'cont' and fits them into dict 'dest'
	mx=0
	counter=0
	for text in cont:
			l=text.split()
			if(len(l)==1) and (cont[0]==text):
				mx=int(l[0])
			elif(len(l)>1): #Avoids reading empty lines
				if(counter<mx):
					dest[counter]=[l[0], l[1]]
					counter+=1
	if(counter<mx):
		print("Not enough points!")
		dest.clear() #Don't return anything if points are insufficient

def connectPoints(p): #Connects all points in p and plots them
	for i in points:
		if(i<len(points)-1):
			n=i+1 #Finds the next point, loops back around to 0
		else:
			n=0
		plt.plot([points[i][0], points[n][0]], [points[i][1], points[n][1]], linestyle='-', linewidth=2)
		plt.plot(points[i][0], points[i][1],'ro')
		plt.plot(points[n][0], points[n][1],'ro') #Points and lines use MATLAB syntax

loc = 'E:\\test\\' #Change as needed, remember to put \\ at the end
openfile='lines.txt'
f= open(os.path.join(loc+openfile), 'r')
content=f.readlines()
f.closed

points={} #Make empty dict
makeDict(content,points)


plt.axes()
plt.ylim([0,12])
plt.xlim([0,12])

connectPoints(points)

plt.show()