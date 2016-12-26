import os
import matplotlib as sdf
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import PolygonCreator as poly
import PlaneSweep as ps


def writeLine(line, i):
    if i == 1:
        f.write(str(line) + '\n')
    else:
        f.write(str(line) + " ")


def makeDict(cont, dest):  # Reads all lines from 'cont' and fits them into dict 'dest'
    mx = 0
    counter = 0
    for text in cont:
        l = text.split()
        if (len(l) == 1) and (cont[0] == text):
            mx = int(l[0])
        elif len(l) > 1:  # Avoids reading empty lines
            if counter < mx:
                dest[counter] = [l[0], l[1]]
                counter += 1
    if (counter < mx):
        print("Not enough points!")
        dest.clear()  # Don't return anything if points are insufficient


def connectPoints(p, c):  # Connects all points in p and plots them in color c
    for i in p:
        if (i < len(p) - 1):
            n = i + 1  # Finds the next point, loops back around to 0
        else:
            n = 0
        plt.plot([p[i][0], p[n][0]], [p[i][1], p[n][1]], linestyle='-', linewidth=2, color=c)
        plt.plot(p[i][0], p[i][1], c + "o")
        plt.plot(p[n][0], p[n][1], c + "o")  # Points and lines use MATLAB syntax

def showDecomp(p):
    for tuple in p.edges:
        edge = tuple[0]
        plt.plot([edge.getStartVertex().x, edge.getEndVertex().x],
                 [edge.getStartVertex().y, edge.getEndVertex().y], linestyle="-", linewidth = 2, color="r" if tuple[1] else "g")



def readPoints(openfile):
    loc = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(loc, openfile), 'r') as f:
        content = f.readlines()
        f.closed
    return content


minx = 0
miny = 0
maxx = 15
maxy = 15

readpol = {}  # Make empty dict
makeDict(readPoints('lines.txt'), readpol)

randpol = {}
makeDict(poly.makePolygon(8, 0, 15), randpol)

plt.axes()
plt.ylim([miny, maxy])
plt.xlim([minx, maxx])

#connectPoints(readpol, "r")
# connectPoints(randpol, "b")

vd = ps.decompose(readpol)

showDecomp(vd)

plt.show()
