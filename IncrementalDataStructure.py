"""
Contains the data structure that can be used for an incremental trapezoidal decomposition.
It is for instance used by the randomized incremental algorithm.
"""
from DataStructures import Direction, Vertex, Edge

class Node:
    """A generic node."""
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "_[{}]".format(self.data)

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

        if isinstance(self.root, TrapezoidLeaf):
            self.root.trapezoid()._node = self

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
            t_node = trapezoid.original.ref_node()

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
            if vertex.x <= node.vertex().x:
                matches |= self.left.point_location_query(vertex)
            else:
                matches |= self.right.point_location_query(vertex)
        elif isinstance(node, YNode):
            if vertex.lies_on(node.edge()):
                matches |= self.left.point_location_query(vertex) \
                    | self.right.point_location_query(vertex)
            if vertex.liesAbove(node.edge()):
                matches |= self.right.point_location_query(vertex)
            else:
                matches |= self.left.point_location_query(vertex)
        elif isinstance(node, TrapezoidLeaf):
            matches.add(node)
        else:
            raise ValueError("The unkown node {} was encountered.".format(node))

        return matches

    def replace_left(self, tree):
        """Replaces the left child of this (sub-)tree."""
        self.left = tree

    def replace_right(self, tree):
        """Replaces the right child of this (sub-)tree."""
        self.right = tree

    def replace(self, tss):
        """Replaces this search structure with the provided one."""
        if isinstance(self.root, TrapezoidLeaf):
            self.root.trapezoid()._node = None
        if isinstance(tss.root, TrapezoidLeaf):
            tss.root.trapezoid()._node = self

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

class Trapezoid:
    """A trapezoid defined by two vertices and two edges."""
    def __init__(self, leftp, rightp, top, bottom, neighbors_left, neighbors_right):
        self._node = TrapezoidSearchStructure(TrapezoidLeaf(self))
        self.leftp = leftp
        self.rightp = rightp
        self.top = top
        self.bottom = bottom
        self.neighbors_left = neighbors_left
        self.neighbors_right = neighbors_right

    def __repr__(self):
        return "/\{{lp {}, rp {}, top [{}], btm [{}]}} ({})" \
            .format(self.leftp, self.rightp, self.top, self.bottom, id(self))

    def __hash__(self):
        return 13 * (hash(self.leftp) + hash(self.rightp) + hash(self.top) + hash(self.bottom))

    def __eq__(self, other):
        return self.leftp == other.leftp and self.rightp == other.rightp and \
            self.top == other.top and self.bottom == other.bottom

    def __neq__(self, other):
        return not self == other

    def ref_node(self):
        """
        Returns the reference to the nodes that contains this trapezoid.
        """
        return self._node

    def top_left(self):
        """Returns the left top vertex of the trapezoid."""
        # Find the y-value on the top edge.
        x_left = self.leftp.x

        if x_left < self.top.getStartVertex().x or self.top.getEndVertex().x < x_left:
            raise ValueError('The left point lies outside the top edge.')

        y_top = self.top.getCorrespondingYValue(x_left)

        if y_top is None:
            raise ValueError('The top edge is vertical.')

        return Vertex(x_left, y_top)

    def top_right(self):
        """Returns the right top vertex of the trapezoid."""
        # Find the y-value on the top edge.
        x_right = self.rightp.x

        if x_right < self.top.getStartVertex().x or self.top.getEndVertex().x < x_right:
            raise ValueError('The right point lies outside the top edge.')

        y_top = self.top.getCorrespondingYValue(x_right)

        if y_top is None:
            raise ValueError('The top edge is vertical.')

        return Vertex(x_right, y_top)

    def bottom_left(self):
        """Returns the bottom left vertex of the trapezoid."""
        # Find the y-value on the bototm edge.
        x_left = self.leftp.x

        if x_left < self.bottom.getStartVertex().x or self.bottom.getEndVertex().x < x_left:
            raise ValueError('The left point lies outside the bottom edge.')

        y_bottom = self.bottom.getCorrespondingYValue(x_left)

        if y_bottom is None:
            raise ValueError('The bottom edge is vertical.')

        return Vertex(x_left, y_bottom)

    def bottom_right(self):
        """Returns the bottom right vertex of the trapezoid."""
        # Find the y-value on the bottom edge.
        x_right = self.rightp.x

        if x_right < self.bottom.getStartVertex().x or self.bottom.getEndVertex().x < x_right:
            raise ValueError('The right point lies outside the bottom edge.')

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
        bottom_left_int = left is not None and top_left != bottom_left and bottom_left.lies_on(edge)
        bottom_right_int = right is not None and top_right != bottom_right and bottom_right.lies_on(edge)

        # Determine the number of vertex intersections.
        vertex_ints = top_left_int + top_right_int + bottom_left_int + bottom_right_int

        if vertex_ints == 2:
            # There are two vertex intersections. There cannot be any more.
            return 2

        # Determine the edge intersections.
        top_int = top.intersects(edge)
        right_int = False if right is None else right.intersects(edge)
        bottom_int = bottom.intersects(edge)
        left_int = False if left is None else left.intersects(edge)

        # There are two intersections opposite of each other.
        if (right_int and left_int) or (top_int and bottom_int):
            return 2
        elif right_int and (top_left_int or bottom_left_int):
            return 2
        elif left_int and (top_right_int or bottom_right_int):
            return 2
        elif top_int and (bottom_left_int or bottom_right_int):
            return 2
        elif bottom_int and (top_left_int or top_right_int):
            return 2

        # Subtract the vertex intersections as these are also included in the edge intersections.
        return (top_int + right_int + bottom_int + left_int) - vertex_ints

    def is_intersected_by(self, edge):
        """Returns true if the provided edge intersects this trapezoid."""
        return self.get_number_of_intersections(edge) > 0

    def contains_vertex(self, vertex):
        """Returns tue if this trapezoids strictly contains the provided vertex."""
        return self.leftp.x < vertex.x and vertex.x < self.rightp.x and \
            vertex.lies_below(self.top) and vertex.liesAbove(self.bottom)

    def split(self, edge):
        """Splits this trapezoid over the specified edge."""
        nr_of_intersections = self.get_number_of_intersections(edge)

        if nr_of_intersections == 0:
            if self.contains_vertex(edge.getStartVertex()) and \
                    self.contains_vertex(edge.getEndVertex()):
                # The trapezoid contains the whole edge.
                # First, define the most left and most right trapezoid.
                t_l = Trapezoid(
                    leftp=self.leftp,
                    rightp=edge.getStartVertex(),
                    top=self.top,
                    bottom=self.bottom,
                    neighbors_left=list(self.neighbors_left),
                    neighbors_right=[])

                # Update the neighbors of the original trapezoid.
                for neighbor in t_l.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(t_l)

                t_r = Trapezoid(
                    leftp=edge.getEndVertex(),
                    rightp=self.rightp,
                    top=self.top,
                    bottom=self.bottom,
                    neighbors_left=[],
                    neighbors_right=list(self.neighbors_right))

                # Update the neighbors of the original trapezoid.
                for neighbor in t_r.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(t_r)

                # Next, define the trapezoids split by the edge.
                t_t = Trapezoid(
                    leftp=edge.getStartVertex(),
                    rightp=edge.getEndVertex(),
                    top=self.top,
                    bottom=edge,
                    neighbors_left=[t_l],
                    neighbors_right=[t_r])
                t_b = Trapezoid(
                    leftp=edge.getStartVertex(),
                    rightp=edge.getEndVertex(),
                    top=edge,
                    bottom=self.bottom,
                    neighbors_left=[t_l],
                    neighbors_right=[t_r])

                # Define the neighbors of the most left and right trapezoid.
                t_l.neighbors_right = [t_t, t_b]
                t_r.neighbors_left = [t_t, t_b]

                return TrapezoidSplit(
                    original=self,
                    top=t_t,
                    bottom=t_b,
                    left=t_l,
                    right=t_r)
            else:
                # This trapezoid has nothing to do with this edge.
                return None
        elif nr_of_intersections == 1:
            # One of the edge its vertices lies in this trapezoid. Split this trapezoid vertically.
            if self.contains_vertex(edge.getStartVertex()):
                # Vertically split this trapezoid such that there is an empty trapezoid.
                # e.g. does not contain a vertex of the edge.
                empty_trapezoid = Trapezoid(
                    leftp=self.leftp,
                    rightp=edge.getStartVertex(),
                    top=self.top,
                    bottom=self.bottom,
                    neighbors_left=list(self.neighbors_left),
                    neighbors_right=[])

                # Replace the split trapezoid in its neighbors.
                for neighbor in empty_trapezoid.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(empty_trapezoid)

                # Construct the other trapezoid resulting from the vertical split.
                # This trapezoid is to be split horizontally. (Note the recursive call.)
                horizontal_split = Trapezoid(
                    leftp=edge.getStartVertex(),
                    rightp=self.rightp,
                    top=self.top,
                    bottom=self.bottom,
                    neighbors_left=[empty_trapezoid],
                    neighbors_right=list(self.neighbors_right))

                # Set the right neighbor of the empty trapezoid to this new trapezoid.
                empty_trapezoid.neighbors_right = [horizontal_split]

                # Replace the split trapezoid in its neighbors.
                for neighbor in horizontal_split.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(horizontal_split)

                horizontal_splits = horizontal_split.split(edge)

                return TrapezoidSplit(
                    original=self,
                    top=horizontal_splits.top,
                    bottom=horizontal_splits.bottom,
                    left=empty_trapezoid)
            elif self.contains_vertex(edge.getEndVertex()):
                # Vertically split this trapezoid such that there is an empty trapezoid.
                # e.g. does not contain a vertex of the edge.
                empty_trapezoid = Trapezoid(
                    leftp=edge.getEndVertex(),
                    rightp=self.rightp,
                    top=self.top,
                    bottom=self.bottom,
                    neighbors_left=[],
                    neighbors_right=list(self.neighbors_right))

                # Replace the split trapezoid in its neighbors.
                for neighbor in empty_trapezoid.neighbors_right:
                    neighbor.neighbors_left.remove(self)
                    neighbor.neighbors_left.append(empty_trapezoid)

                # Construct the other trapezoid resulting from the vertical split.
                horizontal_split = Trapezoid(
                    leftp=self.leftp,
                    rightp=edge.getEndVertex(),
                    top=self.top,
                    bottom=self.bottom,
                    neighbors_left=list(self.neighbors_left),
                    neighbors_right=[empty_trapezoid])

                # Set the left neighbor of the empty trapezoid to this new trapezoid.
                empty_trapezoid.neighbors_left = [horizontal_split]

                # Replace the split trapezoid in its neighbors.
                for neighbor in horizontal_split.neighbors_left:
                    neighbor.neighbors_right.remove(self)
                    neighbor.neighbors_right.append(horizontal_split)

                # This trapezoid is to be split horizontally. (Note the recursive call.)
                horizontal_splits = horizontal_split.split(edge)

                return TrapezoidSplit(
                    original=self,
                    top=horizontal_splits.top,
                    bottom=horizontal_splits.bottom,
                    right=empty_trapezoid)
            else:
                # There is only an intersection with an vertex, do nothing.
                return None
        else:
            # The edge crosses this whole trapezoid. Split this trapezoid horizontally.
            # First determine the left- and right vertex of the top and bottom trapezoid.
            if self.leftp.isVertexOf(edge):
                leftp_t = self.leftp
                leftp_b = self.leftp
            if self.leftp.liesAbove(edge):
                leftp_t = self.leftp
                leftp_b = Vertex(self.leftp.x, self.bottom.getCorrespondingYValue(self.leftp.x))
            else:
                leftp_t = Vertex(self.leftp.x, self.top.getCorrespondingYValue(self.leftp.x))
                leftp_b = self.leftp

            if self.rightp.isVertexOf(edge):
                rightp_t = self.rightp
                rightp_b = self.rightp
            elif self.rightp.liesAbove(edge):
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

            return TrapezoidSplit(
                original=self,
                top=t_top,
                bottom=t_bottom)

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

    def can_merge(self, other):
        """
        Returns true if this trapezoid can be merged with the other trapezoid.
        Otherwise false is returned.
        """
        # They both need to have the same top and bottom edge.
        if self.top == other.top and self.bottom == other.bottom:
            # Check that they trapezoids are each others only neighbors.
            if len(self.neighbors_left) == 1 and other in self.neighbors_left and \
                    len(other.neighbors_right) == 1 and self in other.neighbors_right:
                # Verify whether the edge between them if fake.
                return (not self.top_left().isVertexOf(self.top)) and \
                    (not self.bottom_left().isVertexOf(self.bottom))
            elif len(self.neighbors_right) == 1 and other in self.neighbors_right and \
                    len(other.neighbors_left) == 1 and self in other.neighbors_left:
                # Verify whether the edge between them if fake.
                return (not self.top_right().isVertexOf(self.top)) and \
                    (not self.bottom_right().isVertexOf(self.bottom))

        return False

    def merge(self, other):
        """
        Merges this trapezoid with the provided trapezoid if possible.
        If the merge was performed, then the merged trapezoid is returned.
        Otherwise None is returned.
        """
        if self.can_merge(other):
            if other in self.neighbors_left:
                t_left = other
                t_right = self
            else:
                t_left = self
                t_right = other

            # Note that the top and bottom edge are the same for both trapezoids.
            merged = Trapezoid(
                leftp=t_left.leftp,
                rightp=t_right.rightp,
                top=self.top,
                bottom=self.bottom,
                neighbors_left=list(t_left.neighbors_left),
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

class TrapezoidSplit:
    """
    This class represents an original trapezoid along with sub-trapezoids that
    were created due to the split of this original trapezoid.
    """
    def __init__(self, original, top, bottom, left=None, right=None):
        self.original = original
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def as_search_structure(self, edge):
        """Returns the search structure for this trapezoid split."""
        sub_tree = TrapezoidSearchStructure(
            root=YNode(edge),
            left=self.bottom.ref_node(),
            right=self.top.ref_node())

        if self.right is not None:
            sub_tree = TrapezoidSearchStructure(
                root=XNode(edge.getEndVertex()),
                left=sub_tree,
                right=self.right.ref_node())

        if self.left is not None:
            sub_tree = TrapezoidSearchStructure(
                root=XNode(edge.getStartVertex()),
                left=self.left.ref_node(),
                right=sub_tree)

        return sub_tree

    @staticmethod
    def merge(trapezoid_splits):
        """
        Merges the provided splitted trapezoids. Note that the provided collection is changed.
        """
        if len(trapezoid_splits) < 1:
            return

        # Keep track of the top merge process.
        t_top = trapezoid_splits[0].top
        t_top_merging = [trapezoid_splits[0]]

        # Keep track of the bottom merge process.
        t_bottom = trapezoid_splits[0].bottom
        t_bottom_merging = [trapezoid_splits[0]]

        # Inline functions to process the accumulated merge data.
        def save_top_merges():
            """Processes the accummulated top trapezoid merges."""
            for merging in t_top_merging:
                merging.top = t_top

        def save_bottom_merges():
            """Processes the accumulated bottom trapezoid merges."""
            for merging in t_bottom_merging:
                merging.bottom = t_bottom

        # Process each trapezoidal split.
        for i in range(1, len(trapezoid_splits)):
            cur_split = trapezoid_splits[i]

            if t_top.can_merge(cur_split.top):
                t_top = t_top.merge(cur_split.top)
                t_top_merging.append(cur_split)
            else:
                save_top_merges()

                # Re-initialize the top merge data.
                t_top = cur_split.top
                t_top_merging = [cur_split]

            if t_bottom.can_merge(cur_split.bottom):
                t_bottom = t_bottom.merge(cur_split.bottom)
                t_bottom_merging.append(cur_split)
            else:
                save_bottom_merges()

                # Re-initialize the bottom merge data.
                t_bottom = cur_split.bottom
                t_bottom_merging = [cur_split]

        # Process any merge that is still going on.
        save_top_merges()
        save_bottom_merges()

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
        intersections = list()
        neighbors = list(left_start)

        for neighbor in neighbors:
            for neighbor2 in neighbors:
                if neighbor2 in neighbor.neighbors_right:
                    neighbors.remove(neighbor2)

        for neighbor in neighbors:
            if neighbor.is_intersected_by(edge) or neighbor.contains_vertex(edge.getStartVertex()):
                intersections.append(neighbor)

                neighbors_right = sorted(neighbor.neighbors_right, key=lambda n: n.top.getStartVertex().x)

                for neighbor_right in neighbors_right:
                    if neighbor_right not in neighbors:
                        neighbors.append(neighbor_right)

        return list(intersections)

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
        int_trapezoids = [int_t.trapezoid() for int_t in int_trapezoid_leaves]

        t_intersections = TrapezoidalDecomposition.find_intersections(int_trapezoids, edge)

        # Split these intersecting trapezoids.
        t_splitted = Trapezoid.split_all(t_intersections, edge)

        # Try to merge the splitted trapezoids by moving over them.
        TrapezoidSplit.merge(t_splitted)

        return t_splitted

"""Debug function"""
def contains_trapezoid_with_leftp(t_splitted, vertex):
    for trapezoid in t_splitted:
        leftps = [trapezoid.top.leftp, trapezoid.bottom.leftp]

        if trapezoid.left is not None:
            leftps.append(trapezoid.left.leftp)
        if trapezoid.right is not None:
            leftps.append(trapezoid.right.leftp)

        if vertex in leftps:
            return True

    return False
