from enum import IntEnum
from bintrees import avltree
from DataStructures import Vertex, StatusKey, Direction
from DataStructures import Edge
from VerticalDecomposition import VerticalDecomposition


def decompose(edges):
    # Build event queue

    evtQ = builEventQueue(edges)
    printEventQueue(evtQ)

    # empty status

    status = avltree.AVLTree()

    # start processing events

    vd = VerticalDecomposition()

    while len(evtQ) > 1:
        evtT = evtQ.pop_min()

        edgePoints = {}

        if len(evtT[1]) > 2:
            print("Degenerate case, multiple vertices on a vertical line!!!111!!!!1!!1!")

        for evt in evtT[1]:

            realX = evt.cord

            realY = evt.edge.pointAtEdge(realX).y

            edgePoints[realY] = evt.edge

            if evt.type == EventType.Insert:
                status.insert(evt.edge.statusKeyForEdge(), evt.edge)
                vd.addEdge(evt.edge)
            if evt.type == EventType.Removal:
                status.remove(evt.edge.statusKeyForEdge())

        attemptAddEdges(status, realX, edgePoints, vd)

        print("Total status size is {}".format(len(status)))

    # build deco

    return vd


def attemptAddEdges(status, realX, edgePoints, vd):
    upper = None
    lower = None

    for key in edgePoints:
        edge = edgePoints[key]
        status.insert(edge.statusKeyForEdge(), edge)

    for dKey in edgePoints:

        edge = edgePoints[dKey]

        key = edge.statusKeyForEdge()

        try:
            upper = status.succ_item(key)
        except KeyError:
            None

        try:
            lower = status.prev_item(key)
        except KeyError:
            None

        if upper is not None and ((upper[1].isLeftToRight() and upper[1].insideOn == Direction.Right) or
                                      (upper[1].isRightToLeft() and upper[1].insideOn == Direction.Left)):
            vd.addVertEdge(Edge(edge.pointAtEdge(realX), upper[1].pointAtEdge(realX), Direction.Both))

        if lower is not None and ((lower[1].isRightToLeft() and lower[1].insideOn == Direction.Right) or
                                      (lower[1].isLeftToRight() and lower[1].insideOn == Direction.Left)):
            vd.addVertEdge(Edge(edge.pointAtEdge(realX), lower[1].pointAtEdge(realX), Direction.Both))


def builEventQueue(edges):
    tree = avltree.AVLTree()

    events = []

    for edge in edges:
        if edge.p1.x < edge.p2.x:
            events.append(Event(edge, EventType.Insert, edge.p1.x))
            events.append(Event(edge, EventType.Removal, edge.p2.x))
        else:
            events.append(Event(edge, EventType.Removal, edge.p1.x))
            events.append(Event(edge, EventType.Insert, edge.p2.x))

    events = sorted(events, key=lambda evt: (evt.cord, evt.type))

    cord = -1
    evts = []

    for evt in events:
        if evt.cord == cord:
            evts.append(evt)
        else:
            if len(evts) > 0:
                tree.insert(cord, evts)

            evts = []

            cord = evt.cord

            evts.append(evt)

    tree.insert(cord, evts)

    return tree


def printEventQueue(tree):
    ceil = -1

    while len(tree) > 0:
        try:
            tuple = tree.ceiling_item(ceil + 0.01)
            evts = tuple[1]

            for evt in evts:
                if evt.type == EventType.Insert:
                    print("Insert at x: {} of edge {}".format(evt.cord, repr(evt.edge)))
                else:
                    print("Removal at x: {} of edge {}".format(evt.cord, repr(evt.edge)))

            ceil = tuple[0]
        except KeyError:
            break


class Event:
    def __init__(self, edge, type, cord):
        self.edge = edge
        self.type = type
        self.cord = cord


class EventType(IntEnum):
    Insert = 2
    Removal = 1
    Nothing = 3
