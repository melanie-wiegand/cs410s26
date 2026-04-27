from typing import Callable
# 1) Generate all possible cube configurations with a binary count

# 2) for each cube, solve the 2D isoline problem for each side of the cube

# # 2.1) find line segments between active edges ex. (E0, E8)
# # 2.2) always place the edge across the high vertex for ambiguous cases

# 3) generate a list of all needed triangles for each cube

# 4.1) output a csv with the selected triangles
# 4.2) output a txt with verbose output to make checking the output easier

#      6-----E6------7
#     /|            /|         
#    E7|           E5|             
#   /  |          /  |         
#  4-----E4------5   |    
#  |  E10        |  E11
#  |   |         |   |
#  |   |         |   |
#  E8  2-----E2--E9--3 
#  |  /          |  /           
#  | E3          | E1
#  |/            |/            
#  0-----E0------1                   


# 209: (0, 3, 10), (0, 10, 11), (0, 5, 11), (0, 4, 5)
# 211: (1, 9, 3), (3, 4, 9), (3, 4, 10), (4, 5, 10), (5, 10, 11)
# 212: (2, 3, 8), (2, 4, 8), (2, 4, 5), (2, 5, 11)
# 213: (0, 4, 5), (0, 5, 11), (0, 2, 11)
# 214: (0, 1, 9), (2, 3, 8), (2, 4, 8), (2, 4, 5), (2, 5, 11)
# 215: (1, 2, 11), (4, 5, 9)
# 216: (1, 2, 5), (2, 5, 10), (4, 5, 10), (4, 8, 10)
# 217: (0, 3, 4), (3, 4, 10), (4, 5, 10), (2, 5, 10), (1, 2, 5)
# 218: (0, 2, 8), (2, 8, 10), (4, 5, 9)

# 220: (1, 3, 4), (3, 4, 8), (1, 4, 5)

# 222: (0, 3, 8), (4, 5, 9)

# 224: (4, 7, 10), (4, 9, 11), (4, 10, 11)

# 226: (0, 4, 7), (0, 1, 10), (0, 7, 10), (1, 10, 11) 
# 227: (4, 7, 8), (1, 3, 10), (1, 10, 11)
# 228: (2, 9, 11), (2, 4, 9), (2, 3, 4), (2, 3, 7)
# 229: (4, 7, 8), (0, 2, 9), (2, 9, 11)
# 230: (1, 2, 11), (0, 3, 4), (3, 4, 7)

# 232: (1, 4, 9), (1, 4, 7), (1, 2, 7), (2, 7, 10)
# 233: (0, 3, 8), (1, 4, 9), (1, 4, 7), (1, 2, 7), (2, 7, 10)
# 234: (0, 2, 4), (2, 4, 7), (2, 7, 10)
# 235: (4, 7, 8), (2, 3, 10)
# 236: (1, 3, 9), (3, 4, 9), (3, 4, 7)
# 237: (0, 1, 9), (4, 7, 8)

# 241: (0, 9, 11), (0, 3, 11), (3, 10, 11)
# 242: (0, 1, 10), (0, 8, 10), (1, 10, 11)

# 244: (2, 11, 9), (2, 3, 9), (3, 8, 9)

# 246: (1, 2, 11), (0, 3, 8)

# 248: (1, 9, 8), (1, 2, 8), (2, 8, 10)
# 249: (0, 1, 9), (2, 3, 10)



FACE_VERTS = {
        0: (0, 1, 5, 4),
        1: (1, 3, 7, 5),
        2: (3, 2, 6, 7),
        3: (2, 0, 4, 6),
        4: (0, 1, 3, 2),
        5: (4, 5, 7, 6)
        }
FACE_EDGES = {
        0: (0, 9, 4, 8),
        1: (1, 11, 5, 9),
        2: (2, 10, 6, 11),
        3: (3, 8, 7, 10),
        4: (0, 1, 2, 3),
        5: (4, 5, 6, 7),
        }
EDGE_VERTS = {
        0: (0, 1),
        1: (1, 3),
        2: (2, 3),
        3: (0, 2),
        4: (4, 5),
        5: (5, 7),
        6: (6, 7),
        7: (4, 6),
        8: (0, 4),
        9: (1, 5),
        10: (2, 6),
        11: (3, 7),
        }


class Triangle:
    def __init__(self, e1:int, e2:int, e3:int) -> None:
        # vertexes of the triangle are composed of active edges in a cube
        self.verts_on_edges = tuple(sorted([e1, e2, e3]))

    def __str__(self) -> str:
        v1, v2, v3 = self.verts_on_edges
        return "Tri(%d, %d, %d)" % (v1, v2, v3)


class Edge:
    def __init__(self, edge_vertex1:int, edge_vertex2:int) -> None:
        self.vertexes:tuple[int, int] = tuple(sorted([edge_vertex1, edge_vertex2]))

    def __eq__(self, other):
        x1, x2 = self.vertexes
        y1, y2 = other.vertexes
        return x1 == y1 and x2 == y2 # vertexes should already be sorted

    def __str__(self) -> str:
        x1, x2 = self.vertexes
        return "E(%d, %d)" % (x1, x2)


class Cube:
    def __init__(self, shape:str) -> None:
        self.vertexes:list[bool] = [False]*8
        for i in range(8):
            # index 0 in the array should be the least significant bit in the string, but that is at index 7
            if shape[7 - i] == '1':
                self.vertexes[i] = True
        self.edges:list[bool] = [False]*12
        # edge is active in solution if only one of its vertexes are high
        self.edges[0] = self.vertexes[0] ^ self.vertexes[1]
        self.edges[1] = self.vertexes[1] ^ self.vertexes[3]
        self.edges[2] = self.vertexes[2] ^ self.vertexes[3]
        self.edges[3] = self.vertexes[0] ^ self.vertexes[2]
        self.edges[4] = self.vertexes[4] ^ self.vertexes[5]
        self.edges[5] = self.vertexes[5] ^ self.vertexes[7]
        self.edges[6] = self.vertexes[6] ^ self.vertexes[7]
        self.edges[7] = self.vertexes[4] ^ self.vertexes[6]
        self.edges[8] = self.vertexes[0] ^ self.vertexes[4]
        self.edges[9] = self.vertexes[1] ^ self.vertexes[5]
        self.edges[10] = self.vertexes[2] ^ self.vertexes[6]
        self.edges[11] = self.vertexes[3] ^ self.vertexes[7]

    def __eq__(self, other):
        # cubes are equal if they have the same vertex settings
        for i in range(8):
            if self.vertexes[i] != other.vertexes[i]:
                return False
        return True

    def copy(self):
        s = ['1' if c else '0' for c in self.vertexes]
        return Cube(''.join(s))

    def get_shape(self):
        return ''.join(reversed(['1' if c else '0' for c in self.vertexes]))

    def get_shape_int(self):
        value:int = 0
        for p, b in enumerate(self.vertexes):
            if b:
                value += 2**p
        return value


def get_isolines_for_face(face:int, cube:Cube) -> list[Edge]:
    # find the active edges in the face
    found = 0
    edges = [-1, -1, -1, -1]
    for edge in FACE_EDGES[face]:
        if cube.edges[edge]:
            edges[found] = edge
            found += 1

    if found == 2: # single line case
        return [Edge(*edges[:2])]
    elif found == 4: # case == 4 ambiguous case
        # find the 2 vertexes that are active
        active_verts = []
        for vert in FACE_VERTS[face]:
            if cube.vertexes[vert]:
                active_verts.append(vert)
        # select edge pairs so that each pair share an active vertex
        selected_edges:list[Edge] = []
        for av in active_verts:
            edge_vertexes:list[int] = []
            for e in edges:
                if av in EDGE_VERTS[e]:
                    edge_vertexes.append(e)
            # add edge constructed along the active vertex
            selected_edges.append(Edge(*edge_vertexes))
        return selected_edges
    # no isoline for one or less active edges or 3 lines since that should not happen
    else: # found <= 1 or found == 3
        if found == 3: print("ERROR found 3 active edges on a face")
        return []


def edges_to_triangle(e1:Edge, e2:Edge, e3:Edge) -> Triangle|None:
    # creates a triangle from 3 edges, given that there are only 3 vertexes
    v1, v2 = e1.vertexes
    v3, v4 = e2.vertexes
    v5, v6 = e3.vertexes
    # remove duplicates
    d = list(set([v1, v2, v3, v4, v5, v6]))
    if len(d) == 3:
        # create the triangle
        return Triangle(d[0], d[1], d[2])
    else:
        return None


def find_triangles(cube:Cube, _writer:Callable[str, None]) -> None:
    # calculates the set of triangles for the given cube
    # get the edges for each face
    edges:list[Edge] = []
    for i in range(6):
        edges += get_isolines_for_face(i, cube)

    # remove duplicate edges
    tmp = []
    for e in edges:
        nomatch = True
        for n in tmp:
            if e == n:
                nomatch = False
                break
        if nomatch:
            tmp.append(e)
    # update edges with new trimmed list
    edges = tmp

    if len(edges) < 3:
        # no isosurface
        _writer("CASE %s (%d) Found no triangles\n" % (cube.get_shape(), cube.get_shape_int()))
    elif len(edges) == 3:
        # easy case, one triangle
        result = edges_to_triangle(*edges)
        if result is not None:
            _writer("CASE %s (%d): %s\n" % (cube.get_shape(), cube.get_shape_int(), str(result)))
        else:
            output = [str(s) for s in edges]
            _writer("CASE %s (%d) Found non-triangle 3 edges: %s\n" % (cube.get_shape(), cube.get_shape_int(), str(output)))
    else:
        # TODO other cases not fully implemented
        output = [str(s) for s in edges]
        # look for disjont triangles and quads
        result, remaining = find_disjont_tri_and_quad(edges)
        if len(result) > 0:
            found_tri = [str(s) for s in result]
            # check if all edges were used
            if remaining > 0:
                # inconclusive
                _writer("CASE %s (%d) Not Implemented, found edges: %s\n" % (cube.get_shape(), cube.get_shape_int(), str(output)))
            else:
                _writer("CASE %s (%d): %s\n" % (cube.get_shape(), cube.get_shape_int(), str(found_tri)))
        else:
            _writer("CASE %s (%d) Not Implemented, found edges: %s\n" % (cube.get_shape(), cube.get_shape_int(), str(output)))


def find_disjont_tri_and_quad(edges:list[Edge]) -> tuple[list[Triangle], int]:
    # finds all disjont triangles and quads in the given edge list
    # build a list of all unique vertexes
    all_verts = []
    for e in edges:
        v1, v2 = e.vertexes
        all_verts.append(v1)
        all_verts.append(v2)
    # remove duplicates
    all_verts = list(set(all_verts))

    # start by building a graph of vertex connections
    nodes:dict[int, list[int]] = {}
    for e in edges:
        v:list[int] = list(e.vertexes) # len == 2
        # add or append v2 as a connection for v1
        # and add or append v1 as a connection for v2
        for i in range(2):
            if v[i] in nodes.keys():
                nodes[v[i]].append(v[(i + 1)%2])
            else:
                nodes[v[i]] = [v[(i + 1)%2]]
    # check the graph only has two connections per node, this is the case for disjont shapes
    for node in nodes.keys():
        if len(nodes[node]) != 2:
            return [], len(all_verts)
    # check if graph contains loops of 3 or 4 vertexes
    # look for triangles
    visited = []
    found:list[Triangle] = []
    for root in nodes.keys():
        if root in visited:
            continue # skip vertexes we have already seen
        v1, v2 = nodes[root]
        # if root is part of a triangle, then root, v1, v2 will be the only vertexes
        # so v1 should have connections only to root and v2
        #          
        #    root    
        #    / \     
        #   /   \    
        #  v1---v2 
        #
        v3, v4 = nodes[v1]
        t = v3 if v4 == root else v4
        if v2 == t:
            found.append(Triangle(root, v1, v2))
            visited.append(root)
            visited.append(v1)
            visited.append(v2)
    # look for quads
    for root in nodes.keys():
        if root in visited:
            continue # skip vertexes we have already seen
        v1, v2 = sorted(nodes[root])
        # if root is part of a quad, both its connections should connect to a 4th node
        #          
        #    root    
        #    / \     
        #   /   \    
        #  v1   v2 
        #   \   /  
        #    \ /   
        #     n*   
        #          
        # skip visited vertexes
        if v1 in visited or v2 in visited:
            continue
        f1, f2 = sorted(nodes[v1])
        g1, g2 = sorted(nodes[v2])
        # select the next two nodes that are not the return path to the root node
        # they should be the same node if this is a quad
        n1 = f2 if f1 == root else f1
        n2 = g2 if g1 == root else g1
        if n1 == n2:
            # print(nodes)
            # print("f1:%d, f2:%d, g1:%d, g2:%d" % (f1, f2, g1, g2))
            # print("root:%d, v1:%d, v2:%d, n1:%d, n2:%d" % (root, v1, v2, n1, n2))
            # found quad, triangulate and add to result
            found.append(Triangle(root, v1, n1))
            found.append(Triangle(root, v2, n1))
            visited.append(root)
            visited.append(v1)
            visited.append(v2)
            visited.append(n1)
    # return triangle list
    return found, len(all_verts) - len(visited)



if __name__ == "__main__":
    # binary count
    limit:int = 8
    cubes:list[Cube] = []

    # build all possible blocks
    for i in range(0, pow(2, limit)):
        s:str = bin(i)[2:].zfill(limit)
        # new block with shape given by s
        cubes.append(Cube(s))

    with open("output.txt", "w") as f:
        for cube in cubes:
            find_triangles(cube, f.write)
