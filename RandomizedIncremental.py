"""
A module containing functions and classes related to the randomized incremental algorithm
that creates a trapezoidal deconstruction of a simple polygon.
"""
from math import floor, sqrt, log
from random import shuffle
import IncrementalDataStructure as ds
import VerticalDecomposition as vd

def randomize(collection):
    """
    Returns a new collection containing the same data as the provided collection,
    but in a random order.
    """
    # Copy the collection first to keep the old order intact.
    c_collection = list(collection)
    shuffle(c_collection)

    return c_collection

def to_output(original_edges, trapezoids):
    """Converts the trapezoidal decomposition to the output structure."""
    decomp = vd.VerticalDecomposition()

    trapezoids = sorted(set(trapezoids), key=lambda t: t.leftp.x)

    for i in range(0, len(trapezoids)):
        trapezoid = trapezoids[i]
        print("[{}] {}".format(i, trapezoid), end='')

        for edge in trapezoid.edges():
            if edge in original_edges:
                decomp.addEdge(edge)
            else:
                decomp.addVertEdge(edge)

    return decomp

def decompose_basic(edges):
    """
    Runs the basic randomized incremental algorithm on the provided collection of edges.
    Returns the vertical decomposition.
    """
    r = ds.BoundingBox.around_edges(edges)
    edges = randomize(edges)

    print(edges)

    d = ds.TrapezoidSearchStructure.from_bounding_box(r)

    for edge in edges:

        if edge.is_vertical():
            raise ValueError("Vertical edges are not supported. Edge: {}".format(edge))

        t_new = ds.TrapezoidalDecomposition.insert(d, edge)
        ds.TrapezoidSearchStructure.insert(t_new, edge)

    return [l.trapezoid() for l in d.get_leafs()]

def N(h):
    return 2**(h**2)

'''
def decompose_improved(edges):

    r = ds.BoundingBox.around_edges(edges)
    edges = randomize(edges)

    print(edges)

    d = ds.TrapezoidSearchStructure.from_bounding_box(r)

    for h in range(0, floor(sqrt(log(len(edges))))):
        for i in range(N(h-1) + 1, N(h)):
             
'''
