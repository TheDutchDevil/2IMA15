"""
A module containing functions and classes related to the randomized incremental algorithm
that creates a trapezoidal deconstruction of a simple polygon.
"""
import math as math
from math import floor, sqrt
from random import shuffle
from DataStructures import Vertex, Edge, Direction
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

def log(value):
    """Returns the result of the logarithm of the provided value with base 2."""
    return math.log(value, 2)

def N(h):
    return 2**(h**2)

def trace(edges, ss_d):
    vert_map = {}

    if len(edges) == 0:
        return vert_map

    # First find an initial trapezoid by doing a point location query.
    vertex = edges[0].p1
    t_leafs = list(ss_d.point_location_query(vertex))

    # If multiple trapezoids are returned pick the correct one.
    if len(t_leafs) == 1:
        t_prev = t_leafs[0].trapezoid()
    else:
        # Find the correct trapezoid.
        for t_leaf in t_leafs:
            if edges[0].p1.x < edges[0].p2.x and t_leaf.trapezoid().bottom.p1 == vertex:
                t_prev = t_leaf.trapezoid()
                break
            if edges[0].p1.x > edges[0].p2.x and t_leaf.trapezoid().top.p1 == vertex:
                t_prev = t_leaf.trapezoid()
                break

        # If no trapezoid is found, then take the first.
        t_prev = t_leafs[0].trapezoid()

    # Add the initial vertex to the mapping.
    vert_map[vertex] = t_prev.ref_nodes()[0]

    # Set the previous edge.
    edge_prev = edges[0]

    for i in range(1, len(edges)):
        edge_cur = edges[i]
        vertex = edge_cur.p1

        if not t_prev.contains_vertex(vertex):
            if t_prev.top == edge_cur:
                for neighbor_right in t_prev.neighbors_right:
                    for above in neighbor_right.neighbors_left:
                        if above.bottom == t_prev.top:
                            t_prev = above
                            break
            elif t_prev.bottom == edge_cur:
                for neighbor_left in t_prev.neighbors_left:
                    for below in neighbor_left.neighbors_right:
                        if below.top == t_prev.bottom:
                            t_prev = below
                            break
            elif t_prev.left().intersects(edge_prev):
                neighbors = list(t_prev.neighbors_left)

                while len(neighbors) > 0:
                    neighbor = neighbors.pop()

                    if neighbor.contains_vertex(vertex) or vertex.lies_on(neighbor.right()):
                        t_prev = neighbor
                        break

                    if neighbor.left().intersects(edge_prev):
                        neighbors = list(neighbor.neighbors_left)
            elif t_prev.right().intersects(edge_prev):
                neighbors = list(t_prev.neighbors_right)

                while len(neighbors) > 0:
                    neighbor = neighbors.pop()

                    if neighbor.contains_vertex(vertex) or vertex.lies_on(neighbor.left()):
                        t_prev = neighbor
                        break

                    if neighbor.right().intersects(edge_prev):
                        neighbors = list(neighbor.neighbors_right)

        vert_map[vertex] = t_prev.ref_nodes()[0]
        edge_prev = edge_cur

    return vert_map

def decompose_improved(edges):

    r = ds.BoundingBox.around_edges(edges)
    #edges_rand = randomize(edges)
    edges_rand = [Edge(Vertex(6, 9), Vertex(10, 6), Direction.Undefined), Edge(Vertex(5, 6), Vertex(2, 8), Direction.Undefined), Edge(Vertex(1, 4), Vertex(4, 4), Direction.Undefined), Edge(Vertex(2, 8), Vertex(6, 9), Direction.Undefined), Edge(Vertex(4, 4), Vertex(5, 6), Direction.Undefined), Edge(Vertex(3, 1), Vertex(1, 4), Direction.Undefined), Edge(Vertex(10, 6), Vertex(11, 2), Direction.Undefined), Edge(Vertex(7, 1), Vertex(3, 1), Direction.Undefined), Edge(Vertex(9, 3), Vertex(8, 5), Direction.Undefined), Edge(Vertex(8, 5), Vertex(7, 1), Direction.Undefined), Edge(Vertex(11, 2), Vertex(9, 3), Direction.Undefined)]

    print(edges_rand)

    d = ds.TrapezoidSearchStructure.from_bounding_box(r)

    # Create D1 and T1.
    t_new = ds.TrapezoidalDecomposition.insert(d, edges_rand[0])
    ds.TrapezoidSearchStructure.insert(t_new, edges_rand[0])

    # Trace the vertices to their trapezoids.
    vertex_trace = trace(edges, d)

    # Calculate the number of loops in which a new trace is determined.
    nr_of_loops = floor(sqrt(log(len(edges))))

    for h in range(0, nr_of_loops):
        for i in range(N(h), N(h + 1)):
            _decompose_improved_insert(vertex_trace, edges_rand[i])

        vertex_trace = trace(edges, d)

    for i in range(nr_of_loops + 1, len(edges)):
        _decompose_improved_insert(vertex_trace, edges_rand[i])

    return [l.trapezoid() for l in d.get_leafs()]

def _decompose_improved_insert(vertex_trace, edge):
    """Inserts the provided edge into the structures D and T using the provided trace."""
    if edge.p1 == Vertex(2, 8):
        print("Found")

    if edge.is_vertical():
        raise ValueError("Vertical edges are not supported. Edge: {}".format(edge))

    d_sub = vertex_trace[edge.getStartVertex()]
    t_new = ds.TrapezoidalDecomposition.insert(d_sub, edge)
    ds.TrapezoidSearchStructure.insert(t_new, edge)
