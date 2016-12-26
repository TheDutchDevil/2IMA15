from enum import IntEnum
from bintrees import avltree
from DataStructures import Vertex, StatusKey
from DataStructures import Edge
from VerticalDecomposition import VerticalDecomposition


def decompose(edges):
    # Build event queue

    edgesRaw = list(edges.values())
    edgesProcessed = []

    for i in range(1, len(edgesRaw), 1):
        p1 = Vertex(int(edgesRaw[i - 1][0]), int(edgesRaw[i - 1][1]))
        p2 = Vertex(int(edgesRaw[i][0]), int(edgesRaw[i][1]))

        edgesProcessed.append(Edge(p1, p2))

    p1 = Vertex(int(edgesRaw[0][0]), int(edgesRaw[0][1]))
    p2 = Vertex(int(edgesRaw[len(edgesRaw) - 1][0]), int(edgesRaw[len(edgesRaw) - 1][1]))

    edgesProcessed.append(Edge(p1, p2))

    evtQ = builEventQueue(edgesProcessed)
    printEventQueue(evtQ)

    # empty status

    status = avltree.AVLTree()

    # start processing events

    vd = VerticalDecomposition()

    while len(evtQ) > 1:
        evtT = evtQ.pop_min()

        drewDecompEdge = False

        for evt in evtT[1]:

            realX = evt.cord

            if not drewDecompEdge and evt.type == EventType.Insert:

                upper = None
                lower = None

                try:
                    upper = status.ceiling_item(StatusKey(evt.edge.pointAtEdge(realX).y, 0))
                except KeyError:
                    None

                try:
                    lower = status.floor_item(StatusKey(evt.edge.pointAtEdge(realX).y, 0))
                except KeyError:
                    None

                if upper != None:
                    vd.addVertEdge(Edge(evt.edge.pointAtEdge(realX), upper[1].pointAtEdge(realX)))

                if lower != None:
                    vd.addVertEdge(Edge(evt.edge.pointAtEdge(realX), lower[1].pointAtEdge(realX)))

            if evt.type == EventType.Insert:
                status.insert(evt.edge.statusKeyForEdge(), evt.edge)
                vd.addEdge(evt.edge)
            if evt.type == EventType.Removal:
                status.remove(evt.edge.statusKeyForEdge())



        print("Total status size is {}".format(len(status)))

    # build deco

    return vd


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
                if type == EventType.Insert:
                    tree.insert(cord, evts)
                else:
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
