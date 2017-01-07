"""
A module containing functions and classes related to the randomized incremental algorithm
that creates a trapezoidal deconstruction of a simple polygon.
"""
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

def to_output(original_edges, tss):
    """Converts the trapezoidal decomposition to the output structure."""
    decomp = vd.VerticalDecomposition()

    leaves = tss.get_leafs()
    trapezoids = map(lambda l: l.trapezoid(), leaves)
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
        t_new = ds.TrapezoidalDecomposition.insert(d, edge)
        ds.TrapezoidSearchStructure.insert(t_new, edge)

    return to_output(edges, d)
