"""
A module containing functions and classes related to the randomized incremental algorithm
that creates a trapezoidal deconstruction of a simple polygon.
"""
from enum import Enum
from random import shuffle
from DataStructures import Direction, Vertex, Edge
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

class Node:
    """A generic node."""
    def __init__(self, data):
        self._parent = None
        self.data = data

    def __repr__(self):
        return "_[{}]".format(self.data)

    def parent(self):
        """
        Returns the parent of this node in the structure.
        If this node has no parent, then None is returned.
        """
        return self._parent

class XNode(Node):
    """A x-node that contains a vertex."""
    def __init__(self, vertex):
        super().__init__(vertex)

    def __repr__(self):
        return "X[{}]".format(self.data)

    def vertex(self):
        """Returns the vertex that is the data of this node."""
        return self.data

class YNode(Node):
    """A y-node that contains an edge."""
    def __init__(self, edge):
        super().__init__(edge)

    def __repr__(self):
        return "Y[{}]".format(self.data)

    def edge(self):
        """Returns the edge that is the data of this node."""
        return self.data

class TrapezoidLeaf(Node):
    """A trapezoid leaf that contains a trapezoid."""
    def __init__(self, trapezoid):
        super().__init__(trapezoid)

    def __repr__(self):
        return "T[{}]".format(self.data)

    def trapezoid(self):
        """Returns the trapezoid that is the data of this node."""
        return self.data

class TrapezoidSearchStructure:
    """A DAG for which the leaves are nodes of the type TrapezoidLeaf."""
    def __init__(self, root, left=None, right=None):
        self.root = root
        self.left = left
        self.right = right

        # Override the parents.
        self.root._parent = None

        if isinstance(self.root, TrapezoidLeaf):
            self.root.trapezoid()._nodes.append(self)

        if self.left is not None:
            self.left.root._parent = self
        if self.right is not None:
            self.right.root._parent = self

    @staticmethod
    def from_bounding_box(bounding_box):
        """Initializes the trapezoid search structure from the given bounding box."""
        return TrapezoidSearchStructure(TrapezoidLeaf(bounding_box))

    @staticmethod
    def insert(new_trapezoids, edge):
        """
        Inserts the new trapezoids after the insertion of the specified edge.
        Returns a new search structure if the complete search structure has changed.
        Otherwise the existing search structure is altered.
        """
        for trapezoid in new_trapezoids:
            t_nodes = trapezoid.original.ref_nodes()

            for t_node in t_nodes:
                tss = trapezoid.as_search_structure(edge)
                t_node.replace(tss)

    def point_location_query(self, vertex):
        """
        Runs a point location query on the tree with the specified vertex.
        Returns the TrapezoidLeafs in which it ends.
        """
        node = self.root
        matches = set()

        if isinstance(node, XNode):
            if vertex.x == node.vertex().x:
                matches |= self.get_left().point_location_query(vertex) \
                    | self.get_right().point_location_query(vertex)
            if vertex.x < node.vertex().x:
                matches |= self.get_left().point_location_query(vertex)
            else:
                matches |= self.get_right().point_location_query(vertex)
        elif isinstance(node, YNode):
            if vertex.lies_on(node.edge()):
                matches |= self.get_left().point_location_query(vertex) \
                    | self.get_right().point_location_query(vertex)
            if vertex.liesAbove(node.edge()):
                matches |= self.get_right().point_location_query(vertex)
            else:
                matches |= self.get_left().point_location_query(vertex)
        elif isinstance(node, TrapezoidLeaf):
            matches.add(node)
        else:
            raise ValueError("The unkown node {} was encountered.".format(node))

        return matches

    def get_left(self):
        """
        Returns the left child of the current node.
        Tthrows an LookupError if there is no left child.
        """
        if self.left is None:
            raise LookupError("No left child exists for {}.".format(self.root))
        return self.left

    def get_right(self):
        """
        Returns the right child of the current node.
        Throws an LookupError if there is no right child.
        """
        if self.right is None:
            raise LookupError("No right child exists for {}.".format(self.root))
        return self.right

    def replace_left(self, tree):
        """Replaces the left child of this (sub-)tree."""
        if self.left is not None:
            self.left.root._parent = None

        self.left = tree
        self.left.root._parent = self

    def replace_right(self, tree):
        """Replaces the right child of this (sub-)tree."""
        if self.right is not None:
            self.right.root._parent = None

        self.right = tree
        self.right.root._parent = self

    def replace_child(self, child, tree):
        """
        Replaces the specified child of this node with the specified sub-tree.
        Throws an exception if the child does not exist on this node.
        """
        if self.left is not None and self.left.root == child:
            self.replace_left(tree)
        elif self.right is not None and self.right.root == child:
            self.replace_right(tree)
        else:
            raise ValueError("The child {} does not exist.".format(child))

    def replace(self, tss):
        """Replaces this search structure with the provided one."""
        if isinstance(self.root, TrapezoidLeaf):
            self.root.trapezoid()._nodes.remove(self)

        tss.root._parent = self.root._parent
        self.root._parent = None
        self.root = tss.root

        self.replace_left(tss.left)
        self.replace_right(tss.right)

    def get_leafs(self):
        """Returns all leaves of the search structure."""
        leafs = set()

        if isinstance(self.root, TrapezoidLeaf):
            leafs.add(self.root)
        else:
            if self.left is not None:
                leafs = self.left.get_leafs().union(leafs)
            if self.right is not None:
                leafs = self.right.get_leafs().union(leafs)

        return leafs

    def get_edges(self):
        """Returns the edges of the search structure."""
        edges = set()

        leaves = self.get_leafs()

        # print the trapezoids.
        for i in range(0, len(leaves)):
            print("[{}] {}".format(i, list(leaves)[i]), end='')

        for leave in leaves:
            t_edges = leave.trapezoid().edges()

            for edge in t_edges:
                edges.add(edge)

        return edges

class Trapezoid:
    """A trapezoid defined by two vertices and two edges."""
    def __init__(self, leftp, rightp, top, bottom, neighbors_left, neighbors_right):
        self._nodes = []
        self.leftp = leftp
        self.rightp = rightp
        self.top = top
        self.bottom = bottom
        self.neighbors_left = neighbors_left
        self.neighbors_right = neighbors_right

    def __repr__(self):
        return "\u0394[lp {}, rp {}, top {}, btm {}]" \
            .format(self.leftp, self.rightp, self.top, self.bottom)

    def __hash__(self):
        return 13 * (hash(self.leftp) + hash(self.rightp) + hash(self.top) + hash(self.bottom))

    def __eq__(self, other):
        return self.leftp == other.leftp and self.rightp == other.rightp and \
            self.top == other.top and self.bottom == other.bottom

    def __neq__(self, other):
        return not self == other

    def ref_nodes(self):
        """
        Returns the reference to the nodes that contains this trapezoid.
        """
        return list(self._nodes)

    def top_left(self):
        """Returns the left top vertex of the trapezoid."""
        # Find the y-value on the top edge.
        x_left = self.leftp.x
        y_top = self.top.getCorrespondingYValue(x_left)

        if y_top is None:
            raise ValueError('The top edge is vertical.')

        return Vertex(x_left, y_top)

    def top_right(self):
        """Returns the right top vertex of the trapezoid."""
        # Find the y-value on the top edge.
        x_right = self.rightp.x
        y_top = self.top.getCorrespondingYValue(x_right)

        if y_top is None:
            raise ValueError('The top edge is vertical.')

        return Vertex(x_right, y_top)

    def bottom_left(self):
        """Returns the bottom left vertex of the trapezoid."""
        # Find the y-value on the bototm edge.
        x_left = self.leftp.x
        y_bottom = self.bottom.getCorrespondingYValue(x_left)

        if y_bottom is None:
            raise ValueError('The bottom edge is vertical.')

        return Vertex(x_left, y_bottom)

    def bottom_right(self):
        """Returns the bottom right vertex of the trapezoid."""
        # Find the y-value on the bottom edge.
        x_right = self.rightp.x
        y_bottom = self.bottom.getCorrespondingYValue(x_right)

        if y_bottom is None:
            raise ValueError('The bottom edge is vertical.')

        return Vertex(x_right, y_bottom)

    def left(self):
        """Returns the left edge of the trapezoid."""
        top_l = self.top_left()
        bottom_l = self.bottom_left()

        if top_l == bottom_l:
            # The trapezoid does not have a left edge if the vertices are equal.
            return None
        else:
            return Edge(bottom_l, top_l, Direction.Undefined)

    def right(self):
        """Returns the right edge of the trapezoid."""
        top_r = self.top_right()
        bottom_r = self.bottom_right()

        if top_r == bottom_r:
            # The trapezoid does not have a right edge if the vertices are equal.
            return None
        else:
            return Edge(top_r, bottom_r, Direction.Undefined)

    def edges(self):
        """Returns all edges of this trapezoid."""
        result = [self.top, self.bottom]

        left_edge = self.left()
        if left_edge is not None:
            result.append(left_edge)

        right_edge = self.right()
        if right_edge is not None:
            result.append(right_edge)

        return result

    def top_segment(self):
        """Returns the (paritial) top edge of the trapezoid."""
        top_l = self.top_left()
        top_r = self.top_right()

        return Edge(top_l, top_r, self.top.insideOn)

    def bottom_segment(self):
        """Returns the (paritial) bottom edge of the trapezoid."""
        bottom_l = self.bottom_left()
        bottom_r = self.bottom_right()

        return Edge(bottom_r, bottom_l, self.bottom.insideOn)

    def get_number_of_intersections(self, edge):
        """Returns the number of intersections that the provided edge has with this trapezoid."""
        p1_con = self.contains_vertex(edge.p1)
        p2_con = self.contains_vertex(edge.p2)

        if p1_con and p2_con:
            # The trapezoid contains the whole edge.
            return 0
        if p1_con or p2_con:
            # The trapezoid contains one vertex.
            return 1

        top = self.top_segment()
        right = self.right()
        bottom = self.bottom_segment()
        left = self.left()

        top_left = top.getStartVertex()
        top_right = top.getEndVertex()
        bottom_left = bottom.getStartVertex()
        bottom_right = bottom.getEndVertex()

        top_left_int = top_left.lies_on(edge)
        top_right_int = top_right.lies_on(edge)
        bottom_left_int = False if left is None else bottom_left.lies_on(edge)
        bottom_right_int = False if right is None else bottom_right.lies_on(edge)

        vertex_ints = top_left_int + top_right_int + bottom_left_int + bottom_right_int

        if vertex_ints == 2:
            return 2

        top_int = top.intersects(edge)
        right_int = False if right is None else right.intersects(edge)
        bottom_int = bottom.intersects(edge)
        left_int = False if left is None else left.intersects(edge)

        return (top_int + right_int + bottom_int + left_int) - vertex_ints

    def is_intersected_by(self, edge):
        """Returns true if the provided edge intersects this trapezoid."""
        return self.top_segment().intersects(edge) or \
            self.bottom_segment().intersects(edge) or \
            (self.left() is not None and self.left().intersects(edge)) or \
            (self.right() is not None and self.right().intersects(edge))

    def contains_vertex(self, vertex):
        """Returns tue if this trapezoids strictly contains the provided vertex."""
        return self.leftp.x < vertex.x and vertex.x < self.rightp.x and \
            vertex.lies_below(self.top) and vertex.liesAbove(self.bottom)

    def vertex_on_edge(self, vertex):
        """Returns true if the provided vertex lies on an edge of this trapezoid."""
        left = self.left()
        right = self.right()

        return (left is not None and vertex.lies_on(left)) or \
               (right is not None and vertex.lies_on(right)) or \
               vertex.lies_on(self.top_segment()) or \
               vertex.lies_on(self.bottom_segment())

    def split(self, edge):
        """Splits this trapezoid over the specified edge."""
        nr_of_intersections = self.get_number_of_intersections(edge)

        if nr_of_intersections == 0:
            if self.contains_vertex(edge.getStartVertex()) and \
                    self.contains_vertex(edge.getEndVertex()):
                # The trapezoid contains the whole edge.
                # First, define the most left and most right trapezoid.
                t_l = Trapezoid( \
                    leftp=self.leftp, \
                    rightp=edge.getStartVertex(), \
                    top=self.top, \
                    bottom=self.bottom, \
                    neighbors_left=list(self.neighbors_left), \
                    neighbors_right=[])

                # Update the neighbors of the original trapezoid.
                for neighbor in t_l.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(t_l)

                t_r = Trapezoid( \
                    leftp=edge.getEndVertex(), \
                    rightp=self.rightp, \
                    top=self.top, \
                    bottom=self.bottom, \
                    neighbors_left=[], \
                    neighbors_right=list(self.neighbors_right))

                # Update the neighbors of the original trapezoid.
                for neighbor in t_r.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(t_r)

                # Next, define the trapezoids split by the edge.
                t_t = Trapezoid( \
                    leftp=edge.getStartVertex(), \
                    rightp=edge.getEndVertex(), \
                    top=self.top, \
                    bottom=edge, \
                    neighbors_left=[t_l], \
                    neighbors_right=[t_r])
                t_b = Trapezoid( \
                    leftp=edge.getStartVertex(), \
                    rightp=edge.getEndVertex(), \
                    top=edge,
                    bottom=self.bottom,
                    neighbors_left=[t_l],
                    neighbors_right=[t_r])

                # Define the neighbors of the most left and right trapezoid.
                t_l.neighbors_right = [t_t, t_b]
                t_r.neighbors_left = [t_t, t_b]

                return TrapezoidSplit( \
                    original=self, \
                    splits=[
                        TrapezoidEdgeSplit(t_l, TrapezoidEdgeSplitType.Left),
                        TrapezoidEdgeSplit(t_r, TrapezoidEdgeSplitType.Right),
                        TrapezoidEdgeSplit(t_t, TrapezoidEdgeSplitType.Top),
                        TrapezoidEdgeSplit(t_b, TrapezoidEdgeSplitType.Bottom)
                    ])
            else:
                # This trapezoid has nothing to do with this edge.
                return None
        elif nr_of_intersections == 1:
            # One of the edge its vertices lies in this trapezoid. Split this trapezoid vertically.
            if self.contains_vertex(edge.getStartVertex()):
                # Vertically split this trapezoid such that there is an empty trapezoid.
                # e.g. does not contain a vertex of the edge.
                empty_trapezoid = Trapezoid( \
                    leftp=self.leftp, \
                    rightp=edge.getStartVertex(), \
                    top=self.top, \
                    bottom=self.bottom, \
                    neighbors_left=list(self.neighbors_left), \
                    neighbors_right=[])

                # Replace the split trapezoid in its neighbors.
                for neighbor in empty_trapezoid.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(empty_trapezoid)

                # Construct the other trapezoid resulting from the vertical split.
                # This trapezoid is to be split horizontally. (Note the recursive call.)
                horizontal_split = \
                    Trapezoid( \
                        leftp=edge.getStartVertex(), \
                        rightp=self.rightp, \
                        top=self.top, \
                        bottom=self.bottom, \
                        neighbors_left=[empty_trapezoid], \
                        neighbors_right=list(self.neighbors_right))

                # Set the right neighbor of the empty trapezoid to this new trapezoid.
                empty_trapezoid.neighbors_right = [horizontal_split]

                # Replace the split trapezoid in its neighbors.
                for neighbor in horizontal_split.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(horizontal_split)

                horizontal_splits = horizontal_split.split(edge).splits

                return TrapezoidSplit( \
                    original=self, \
                    splits=[TrapezoidEdgeSplit(empty_trapezoid, TrapezoidEdgeSplitType.Left)] \
                        + horizontal_splits)
            elif self.contains_vertex(edge.getEndVertex()):
                # Vertically split this trapezoid such that there is an empty trapezoid.
                # e.g. does not contain a vertex of the edge.
                empty_trapezoid = Trapezoid( \
                    leftp=edge.getEndVertex(), \
                    rightp=self.rightp, \
                    top=self.top, \
                    bottom=self.bottom, \
                    neighbors_left=[], \
                    neighbors_right=list(self.neighbors_right))

                # Replace the split trapezoid in its neighbors.
                for neighbor in empty_trapezoid.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(empty_trapezoid)

                # Construct the other trapezoid resulting from the vertical split.
                horizontal_split = \
                    Trapezoid( \
                        leftp=self.leftp, \
                        rightp=edge.getEndVertex(), \
                        top=self.top, \
                        bottom=self.bottom, \
                        neighbors_left=list(self.neighbors_left), \
                        neighbors_right=[empty_trapezoid])

                # Set the left neighbor of the empty trapezoid to this new trapezoid.
                empty_trapezoid.neighbors_left = [horizontal_split]

                # Replace the split trapezoid in its neighbors.
                for neighbor in horizontal_split.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(horizontal_split)

                # This trapezoid is to be split horizontally. (Note the recursive call.)
                horizontal_splits = horizontal_split.split(edge).splits

                return TrapezoidSplit( \
                    original=self, \
                    splits=[TrapezoidEdgeSplit(empty_trapezoid, TrapezoidEdgeSplitType.Right)] \
                        + horizontal_splits)
            else:
                # There is only an intersection with an vertex, do nothing.
                return None
        else:
            # The edge crosses this whole trapezoid. Split this trapezoid horizontally.
            # First determine the left- and right vertex of the top and bottom trapezoid.
            if self.leftp.liesAbove(edge):
                leftp_t = self.leftp
                leftp_b = Vertex(self.leftp.x, self.bottom.getCorrespondingYValue(self.leftp.x))
            else:
                leftp_t = Vertex(self.leftp.x, self.top.getCorrespondingYValue(self.leftp.x))
                leftp_b = self.leftp

            if self.rightp.liesAbove(edge):
                rightp_t = self.rightp
                rightp_b = Vertex(self.rightp.x, self.bottom.getCorrespondingYValue(self.rightp.x))
            else:
                rightp_t = Vertex(self.rightp.x, self.top.getCorrespondingYValue(self.rightp.x))
                rightp_b = self.rightp

            # Next, determine the left- and right vertex of the intersecting edge.
            leftp_edge = Vertex(self.leftp.x, edge.getCorrespondingYValue(self.leftp.x))
            rightp_edge = Vertex(self.rightp.x, edge.getCorrespondingYValue(self.rightp.x))

            # Give preference to an actually existing vertex.
            # If the vertex on the intersecting edge is not a fake,
            # while the one determined above is, override it.
            if leftp_edge.isVertexOf(edge):
                if not leftp_t.isVertexOf(self.top):
                    leftp_t = leftp_edge
                if not leftp_b.isVertexOf(self.bottom):
                    leftp_b = leftp_edge
            if rightp_edge.isVertexOf(edge):
                if not rightp_t.isVertexOf(self.top):
                    rightp_t = rightp_edge
                if not rightp_b.isVertexOf(self.bottom):
                    rightp_b = rightp_edge

            t_top = Trapezoid(leftp_t, rightp_t, self.top, edge, [], [])
            t_bottom = Trapezoid(leftp_b, rightp_b, edge, self.bottom, [], [])

            # Determine the neighbors of these new trapezoids.
            for neighbor in self.neighbors_left:
                # Remove this split trapezoid from its left neighbors.
                neighbor.neighbors_right.remove(self)

                # If the trapezoid lies both above and below the new edge.
                if edge.lies_above(neighbor.bottom) and neighbor.top.lies_above(edge):
                    t_top.neighbors_left.append(neighbor)
                    t_bottom.neighbors_left.append(neighbor)

                    neighbor.neighbors_right.append(t_top)
                    neighbor.neighbors_right.append(t_bottom)
                else:
                    if neighbor.rightp == t_top.leftp or \
                            neighbor.top == t_top.top or \
                            neighbor.bottom == t_top.bottom or \
                            neighbor.bottom.lies_above(edge):

                        neighbor.neighbors_right.append(t_top)
                        t_top.neighbors_left.append(neighbor)

                    if neighbor.rightp == t_bottom.leftp or \
                            neighbor.top == t_bottom.top or \
                            neighbor.bottom == t_bottom.bottom or \
                            edge.lies_above(neighbor.top):

                        neighbor.neighbors_right.append(t_bottom)
                        t_bottom.neighbors_left.append(neighbor)

            for neighbor in self.neighbors_right:
                # Remove this split trapezoid from its right neighbors.
                neighbor.neighbors_left.remove(self)

                # If the trapezoid lies both above and below the new edge.
                if edge.lies_above(neighbor.bottom) and neighbor.top.lies_above(edge):
                    t_top.neighbors_right.append(neighbor)
                    t_bottom.neighbors_right.append(neighbor)

                    neighbor.neighbors_left.append(t_top)
                    neighbor.neighbors_left.append(t_bottom)
                else:
                    if neighbor.leftp == t_top.rightp or \
                            neighbor.top == t_top.top or \
                            neighbor.bottom == t_top.bottom or \
                            neighbor.bottom.lies_above(edge):

                        neighbor.neighbors_left.append(t_top)
                        t_top.neighbors_right.append(neighbor)

                    if neighbor.leftp == t_bottom.rightp or \
                            neighbor.top == t_bottom.top or \
                            neighbor.bottom == t_bottom.bottom or \
                            edge.lies_above(neighbor.top):

                        neighbor.neighbors_left.append(t_bottom)
                        t_bottom.neighbors_right.append(neighbor)

            return TrapezoidSplit( \
                original=self, \
                splits=[
                    TrapezoidEdgeSplit(t_top, TrapezoidEdgeSplitType.Top),
                    TrapezoidEdgeSplit(t_bottom, TrapezoidEdgeSplitType.Bottom)
                ])

    @staticmethod
    def split_all(trapezoids, edge):
        """
        Splits all provided trapezoids over the specified edge.
        Returns a collection of splitted trapezoids.
        """
        result = []

        for trapezoid in trapezoids:
            splitted = trapezoid.split(edge)

            if splitted is not None:
                result.append(splitted)

        return result

class BoundingBox(Trapezoid):
    """Represents a bounding box around a set of vertices."""
    def __init__(self, top_left, bottom_right, top, bottom):
        super().__init__(top_left, bottom_right, top, bottom, [], [])

    def __repr__(self):
        return "{}|\u203E _|{}".format(self.leftp, self.rightp)

    @staticmethod
    def around_vertices(vertices, padding=2):
        """Constructs a bounding box around the provided list of vertices.

        Arguments:
        vertices -- the list of vertices around which a bounding box is to be constructed.
        padding -- the padding between the bounding box and outer vertices (default 10).
        """
        if vertices == []:
            x_left = 0
            x_right = 0
            y_top = 0
            y_bottom = 0
        else:
            x_left = vertices[0].x
            x_right = vertices[0].x
            y_top = vertices[0].y
            y_bottom = vertices[0].y

            del vertices[0]

            for vertex in vertices:
                if vertex.x < x_left:
                    x_left = vertex.x
                if vertex.x > x_right:
                    x_right = vertex.x

                if vertex.y > y_top:
                    y_top = vertex.y
                if vertex.y < y_bottom:
                    y_bottom = vertex.y

        top_left = Vertex(x_left - padding, y_top + padding)
        bottom_right = Vertex(x_right + padding, y_bottom - padding)

        top = Edge(top_left, Vertex(bottom_right.x, top_left.y), Direction.Undefined)
        bottom = Edge(bottom_right, Vertex(top_left.x, bottom_right.y), Direction.Undefined)

        return BoundingBox(top_left, bottom_right, top, bottom)

    @staticmethod
    def around_edges(edges, padding=2):
        """Constructs a bounding box around the provided list of edges.

        Arguments:
        edges -- the list of edges around which a bounding box is to be constructed.
        padding -- the least between the bounding box and edges (default 10).
        """
        vertices = []

        for edge in edges:
            vertices.append(edge.getStartVertex())
            vertices.append(edge.getEndVertex())

        return BoundingBox.around_vertices(vertices, padding)

class TrapezoidEdgeSplitType(Enum):
    """Defines the different type of trapezoidal splits due to an edge."""
    Left = 1, """This trapezoid is the left part of the original trapezoid after the split."""
    Right = 2, """This trapezoid is the right part of the original trapezoid after the split."""
    Top = 3, """This trapezoid is the top part of the original trapezoid after the split."""
    Bottom = 4, """This trapezoid is the bottom part of the original trapezoid after the split."""

class TrapezoidSplit:
    """
    This class represents an original trapezoid along with sub-trapezoids that
    were created due to the split of this original trapezoid.
    """
    def __init__(self, original, splits):
        self.original = original
        self.splits = splits

        # TODO: Would be nicer to define the 4 splits and make None if not applicable.

    def left_split(self):
        """Returns the left split of this trapezoid split or None if there isn't any."""
        for split in self.splits:
            if split.split_type == TrapezoidEdgeSplitType.Left:
                return split

        return None

    def top_split(self):
        """Returns the top split of this trapezoid split or None if there isn't any."""
        for split in self.splits:
            if split.split_type == TrapezoidEdgeSplitType.Top:
                return split

        return None

    def right_split(self):
        """Returns the right split of this trapezoid split or None if there isn't any."""
        for split in self.splits:
            if split.split_type == TrapezoidEdgeSplitType.Right:
                return split

        return None

    def bottom_split(self):
        """Returns the bottom split of this trapezoid split or None if there isn't any."""
        for split in self.splits:
            if split.split_type == TrapezoidEdgeSplitType.Bottom:
                return split

        return None

    def has_left_split(self):
        """Returns true if this trapezoid split has a left split. Otherwise false."""
        return self.left_split() is not None

    def has_right_split(self):
        """Returns true if this trapezoid split has a right split. Otherwise false."""
        return self.right_split() is not None

    def as_search_structure(self, edge):
        """Returns the search structure for this trapezoid split."""
        t_top = self.top_split().new
        t_bottom = self.bottom_split().new

        sub_tree = TrapezoidSearchStructure( \
            root=YNode(edge), \
            left=TrapezoidSearchStructure(TrapezoidLeaf(t_bottom)), \
            right=TrapezoidSearchStructure(TrapezoidLeaf(t_top)))

        if self.has_left_split() and self.has_right_split():
            t_left = self.left_split().new
            t_right = self.right_split().new

            return TrapezoidSearchStructure( \
                root=XNode(edge.getStartVertex()), \
                left=TrapezoidSearchStructure(TrapezoidLeaf(t_left)), \
                right=TrapezoidSearchStructure( \
                    root=XNode(edge.getEndVertex()), \
                    left=sub_tree, \
                    right=TrapezoidSearchStructure(TrapezoidLeaf(t_right))))
        elif self.has_left_split():
            t_left = self.left_split().new

            return TrapezoidSearchStructure( \
                root=XNode(edge.getStartVertex()), \
                left=TrapezoidSearchStructure(TrapezoidLeaf(t_left)), \
                right=sub_tree)
        elif self.has_right_split():
            t_right = self.right_split().new

            return TrapezoidSearchStructure( \
                root=XNode(edge.getEndVertex()), \
                left=sub_tree, \
                right=TrapezoidSearchStructure(TrapezoidLeaf(t_right)))
        else:
            return sub_tree

    @staticmethod
    def merge(trapezoid_splits):
        """
        Merges the provided splitted trapezoids. Note that the provided collection is changed.
        """
        # Keep track of the top merge process.
        t_top = None
        t_top_merging = []

        # Keep track of the bottom merge process.
        t_bottom = None
        t_bottom_merging = []

        for t_split in trapezoid_splits:
            for split in t_split.splits:
                if split.split_type is TrapezoidEdgeSplitType.Top:
                    # This is the top of an origianl trapezoid.
                    if t_top is not None:
                        # If a top is already saved, try to merge it.
                        merged = t_top.merge_if_possible(split)

                        if merged is not None:
                            # If the merge succeeded, then continue.
                            t_top = TrapezoidEdgeSplit(merged, TrapezoidEdgeSplitType.Top)
                            t_top_merging.append(split)
                        else:
                            # The merge has failed, process accummulated trapezoids.
                            for merging in t_top_merging:
                                merging.new = t_top.new

                            # Re-initialize the top merge data.
                            t_top = split
                            t_top_merging = [split]
                    else:
                        # There is no top yet, initialize.
                        t_top = split
                        t_top_merging = [split]
                elif split.split_type is TrapezoidEdgeSplitType.Bottom:
                    # This is the bottom of an origianl trapezoid.
                    if t_bottom is not None:
                        # If a bottom is already saved, try to merge it.
                        merged = t_bottom.merge_if_possible(split)

                        if merged is not None:
                            # If the merge succeeded, then continue.
                            t_bottom = TrapezoidEdgeSplit(merged, TrapezoidEdgeSplitType.Bottom)
                            t_bottom_merging.append(split)
                        else:
                            # The merge has failed, process accummulated trapezoids.
                            for merging in t_bottom_merging:
                                merging.new = t_bottom.new

                            # Re-initialize the bottom merge data.
                            t_bottom = split
                            t_bottom_merging = [split]
                    else:
                        # There is no bottom yet, initialize.
                        t_bottom = split
                        t_bottom_merging = [split]

        # Process any merge that is still going on.
        for merging in t_top_merging:
            merging.new = t_top.new

        for merging in t_bottom_merging:
            merging.new = t_bottom.new

class TrapezoidEdgeSplit:
    """
    This class represents the split of a trapezoid that. The split type of this class
    indicates which part of the original trapezoid the sub-trapezoid represents.
    """
    def __init__(self, new, split_type):
        self.new = new
        self.split_type = split_type

    def can_merge(self, trapezoid_split):
        """
        Returns true if this trapezoid split can be merged with the specified trapezoid split.
        Otherwise false is returned.
        """
        t_self = self.new
        t_other = trapezoid_split.new

        # They both need to have the same top and bottom edge.
        if t_self.top == t_other.top and t_self.bottom == t_other.bottom:
            # Check that they trapezoids are each others only neighbors.
            if len(t_self.neighbors_left) == 1 and t_other in t_self.neighbors_left and \
                    len(t_other.neighbors_right) == 1 and t_self in t_other.neighbors_right:
                # Verify whether the edge between them if fake.
                return (not t_self.top_left().isVertexOf(t_self.top)) and \
                    (not t_self.bottom_left().isVertexOf(t_self.bottom))
            elif len(t_self.neighbors_right) == 1 and t_other in t_self.neighbors_right and \
                    len(t_other.neighbors_left) == 1 and t_self in t_other.neighbors_left:
                # Verify whether the edge between them if fake.
                return (not t_self.top_right().isVertexOf(t_self.top)) and \
                    (not t_self.bottom_right().isVertexOf(t_self.bottom))

        return False

    def merge_if_possible(self, trapezoid_split):
        """
        Merges this trapezoid with the provided trapezoid if possible.
        If the merge was performed, then the merged trapezoid is returned.
        Otherwise None is returned.
        """
        if self.can_merge(trapezoid_split):
            if trapezoid_split.new in self.new.neighbors_left:
                t_left = trapezoid_split.new
                t_right = self.new
            else:
                t_left = self.new
                t_right = trapezoid_split.new

            # Note that the top and bottom edge are the same for both trapezoids.
            merged = Trapezoid( \
                leftp=t_left.leftp, \
                rightp=t_right.rightp, \
                top=self.new.top, \
                bottom=self.new.bottom, \
                neighbors_left=list(t_left.neighbors_left), \
                neighbors_right=list(t_right.neighbors_right))

            # Update the neighbors after the merge.
            for neighbor_left in merged.neighbors_left:
                neighbor_left.neighbors_right.remove(t_left)
                neighbor_left.neighbors_right.append(merged)

            for neighbor_right in merged.neighbors_right:
                neighbor_right.neighbors_left.remove(t_right)
                neighbor_right.neighbors_left.append(merged)

            return merged
        else:
            return None

class TrapezoidalDecomposition:
    """Contains the functions related to the trapezoidal decomposition of a simple polygon."""
    @staticmethod
    def find_intersections(left_start, edge):
        """
        Returns the intersected trapezoids by the specified edge. This also includes the
        provided trapezoid.

        Arguments:
        left_start -- The most left trapezoid that is intersected by the edge.
        edge -- The edge for which the trapezoidal intersections are to be determined.
        """
        intersections = list(left_start)
        neighbors = list(left_start)

        for neighbor in neighbors:
            for neighbor2 in neighbors:
                if neighbor2 in neighbor.neighbors_right:
                    neighbors.remove(neighbor2)

        for neighbor in neighbors:
            if neighbor.is_intersected_by(edge):
                intersections.append(neighbor)

                for neighbor_right in neighbor.neighbors_right:
                    if neighbor_right not in neighbors:
                        neighbors.append(neighbor_right)

        return list(set(intersections))

    @staticmethod
    def insert(ss_d, edge):
        """
        Inserts the provided edge into the trapezoidal decomposition.
        Returns a tuple (old, new)
            in which 'new' are the trapezoids which have replaced the 'old' trapezoids.

        Arguments
        ss_d -- The search structure that belongs to the trapezoidal decomposition.
        edge -- The edge that is to be inserted.
        """
        # First, determine the trapezoids intersecting with the provided edge.
        int_trapezoid_leaves = ss_d.point_location_query(edge.getStartVertex())

        # Get the trapezoids from the leaves.
        int_trapezoids = []
        for int_trapezoid_leave in int_trapezoid_leaves:
            int_trapezoids.append(int_trapezoid_leave.trapezoid())

        t_intersections = TrapezoidalDecomposition.find_intersections(int_trapezoids, edge)

        # Split these intersecting trapezoids.
        t_splitted = Trapezoid.split_all(t_intersections, edge)

        # Try to merge the splitted trapezoids by moving over them.
        TrapezoidSplit.merge(t_splitted)

        return t_splitted

def to_output(original_edges, d):
    """Converts the trapezoidal decomposition to the output structure."""
    decomp = vd.VerticalDecomposition()

    edges = d.get_edges()

    for edge in edges:
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
    r = BoundingBox.around_edges(edges)
    edges = randomize(edges)

    d = TrapezoidSearchStructure.from_bounding_box(r)

    for edge in edges:
        t_new = TrapezoidalDecomposition.insert(d, edge)
        TrapezoidSearchStructure.insert(t_new, edge)

    return to_output(edges, d)
