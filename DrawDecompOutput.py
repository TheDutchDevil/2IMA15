import os
from statistics import mean

import matplotlib as sdf
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from pympler.tracker import SummaryTracker
import time
import gc

import PolygonCreator as poly
import PlaneSweep as ps
import RandomizedIncremental as ri
from DataStructures import Vertex, Edge, Direction


def writeLine(line, i):
    if i == 1:
        f.write(str(line) + '\n')
    else:
        f.write(str(line) + " ")


def makeEdgeList(vertices):
    prevVertex = None

    edgesTemp = []

    for text in vertices:
        splitLine = text.split()

        if len(splitLine) == 1 and vertices[0] == text:
            None
        else:
            vertex = Vertex(int(splitLine[0]), int(splitLine[1]))

            if prevVertex is not None:
                edgesTemp.append(Edge(prevVertex, vertex, Direction.Right))

            prevVertex = vertex

    edgesTemp.append(Edge(edgesTemp[len(edgesTemp) - 1].p2, edgesTemp[0].p1, Direction.Right))

    return edgesTemp


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
                 [edge.getStartVertex().y, edge.getEndVertex().y], linestyle="-", linewidth=2,
                 color="r" if tuple[1] else "g")


def readPoints(openfile):
    loc = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(loc, openfile), 'r') as f:
        content = f.readlines()
        f.closed
    return content

def doComp(res, edges):
     for i in range(0, 10):
        start = time.time()

        ri.decompose_basic(edges)

        stop = time.time()

        res[n].append((stop - start) * 1000.0)
        print("took: {}".format((stop - start) * 1000.0))



baseN = 700
'''
for i in range(1,33):
    for j in range(0,3):
        n = baseN*i
        poly.writePoints(poly.makeRectangloid(int(n/4 + 1), int(n/4 + 1), int(n * 1.25), general=2),
                         "testSuite/testSuite{}_{}".format(n, j))



'''
res = {}

gc.enable()

tracker = SummaryTracker()


trackVar = 0

for filename in os.listdir("testsuite"):
    filename = "testsuite/" + filename
    edges = makeEdgeList(readPoints(filename))

    print("Doing file {}".format(filename))

    with open(filename, 'r') as f:
        n = int(f.readline())

    if not n in res:
        res[n] = []

    doComp(res, edges)


    if trackVar % 5 == 0 and not trackVar == 0:
        gc.collect()

    edges.clear()

    trackVar += 1

for finishedN in res:
    print("{} took: {}".format(finishedN, mean(res[finishedN])))

'''
minx = 0
miny = 0
maxx = 10**8
maxy = 10**8

readpol = {}  # Make empty dict
makeDict(readPoints('lines.txt'), readpol)

edges = makeEdgeList(readPoints('test_input_2_on_vert_line.txt'))
randpol = {}
#makeDict(poly.makePolygon(8, 0, 15), randpol)

plt.axes()
plt.ylim([miny, maxy])
plt.xlim([minx, maxx])

#connectPoints(readpol, "r")
# connectPoints(randpol, "b")

vd = ps.decompose(edges)

showDecomp(vd)

plt.show()
'''
