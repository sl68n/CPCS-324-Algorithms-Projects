import heapq
import time
import random
from abc import ABC, abstractmethod
import networkx as nx
import matplotlib.pyplot as plt


# ====== Base classes: Vertex / Edge and subclasses Junction / Pipe ======

class Vertex(ABC):
    def __init__(self, label: str):
        self.label = label
        self.adj = []  # list of outgoing edges


class Edge(ABC):
    def __init__(self, u: Vertex, v: Vertex, weight: int):
        self.u = u
        self.v = v
        self.weight = weight


class Junction(Vertex):
    """Represents a junction in the pipe network."""
    pass


class Pipe(Edge):
    """Represents a pipe (edge) between two junctions."""
    pass


# ====== Graph class (Follows UML) ======

class Graph:
    def __init__(self):
        self.vertices = []       # list of Junction objects
        self.vertex_map = {}     # label -> Junction
        # self.edges is not explicitly in UML,
        # but adj lists in Vertex cover it.

    def get_vertex(self, label: str) -> Junction:
        """Gets or creates a Junction."""
        if label not in self.vertex_map:
            vertex = Junction(label)
            self.vertices.append(vertex)
            self.vertex_map[label] = vertex
        return self.vertex_map[label]

    def add_edge(self, u_label: str, v_label: str, w: int) -> None:
        """Adds a Pipe (edge) between two Junctions, per the UML diagram."""
        u = self.get_vertex(u_label)
        v = self.get_vertex(v_label)
        
        # Create a Pipe object
        edge = Pipe(u, v, w)
        u.adj.append(edge)
        # Create the reverse edge for the undirected graph
        reverse_edge = Pipe(v, u, w)
        v.adj.append(reverse_edge)

    def readFromFile(self, filename: str) -> None:
        """
        Reads graph from file (as per UML).
        File format (as per project instructions):
        First line: n m
        Next m lines: u v w
        """
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Read n and m from the first line
        try:
            first_line = lines[0].split()
            n = int(first_line[0])
            m = int(first_line[1])
        except Exception as e:
            print(f"Error: Could not read n and m from first line of {filename}.")
            print("Expected format: n m")
            return

        # Read m edges from the following lines
        # Start from index 1 (the second line)
        for i in range(1, m + 1):
            try:
                parts = lines[i].split()
                u, v, w = parts[0], parts[1], int(parts[2])
                # add_edge will automatically create Junctions
                self.add_edge(u, v, w)
            except IndexError:
                print(f"Warning: File missing edge data on line {i+1}. Expected {m} edges.")
            except Exception as e:
                print(f"Error reading edge on line {i+1}: {e}")

        # Verify number of vertices
        if len(self.vertices) != n:
           print(f"Warning: File specified {n} vertices, but {len(self.vertices)} were found.")


# ====== Union-Find for Kruskal ======

class UnionFind:
    def __init__(self, labels):
        self.parent = {label: label for label in labels}
        self.rank = {label: 0 for label in labels}

    def find(self, label: str) -> str:
        if self.parent[label] != label:
            self.parent[label] = self.find(self.parent[label])
        return self.parent[label]

    def union(self, label1: str, label2: str) -> bool:
        p1 = self.find(label1)
        p2 = self.find(label2)
        if p1 == p2:
            return False
        if self.rank[p1] < self.rank[p2]:
            self.parent[p1] = p2
        elif self.rank[p1] > self.rank[p2]:
            self.parent[p2] = p1
        else:
            self.parent[p2] = p1
            self.rank[p1] += 1
        return True


# ====== Abstract MST algorithm base class ======

class MstAlgorithm(ABC):
    def __init__(self):
        # Per UML: result: List (of edges)
        self.result = None

    @abstractmethod
    def findMST(self, g: Graph) -> list:
        """Per UML: findMST(g: Graph): List"""
        pass

    def totalWeight(self) -> int:
        if self.result is None:
            raise ValueError("MST not computed")
        return sum(e.weight for e in self.result)


# ====== Prim (with Min-Heap) ======

class PrimAlg(MstAlgorithm):
    def findMST(self, g: Graph) -> list:
        if not g.vertices:
            self.result = []
            return self.result

        start = g.vertices[0]
        # Use label for visited set
        visited = set([start.label]) 
        min_heap = []
        counter = 0  # tie-breaker for heap

        for edge in start.adj:
            heapq.heappush(min_heap, (edge.weight, counter, start, edge.v))
            counter += 1

        mst = []
        while min_heap and len(visited) < len(g.vertices):
            w, _, u, v = heapq.heappop(min_heap)
            if v.label in visited:
                continue
            visited.add(v.label)
            mst.append(Pipe(u, v, w)) # Create a Pipe for the MST
            for edge in v.adj:
                if edge.v.label not in visited:
                    heapq.heappush(min_heap, (edge.weight, counter, v, edge.v))
                    counter += 1

        self.result = mst
        return mst


# ====== Kruskal ======

class KruskalAlg(MstAlgorithm):
    def findMST(self, g: Graph) -> list:
        edges = []
        seen = set()
        for vertex in g.vertices:
            for edge in vertex.adj:
                # Use min/max label to create a unique key
                u_lab = min(edge.u.label, edge.v.label)
                v_lab = max(edge.u.label, edge.v.label)
                key = (u_lab, v_lab)
                if key not in seen:
                    seen.add(key)
                    edges.append(edge)

        edges.sort(key=lambda e: e.weight)
        uf = UnionFind([v.label for v in g.vertices])
        mst = []
        for edge in edges:
            if uf.union(edge.u.label, edge.v.label):
                mst.append(edge)
            if len(mst) == len(g.vertices) - 1:
                break

        self.result = mst
        return mst


# ====== Generate random connected graph (Requirement 2) ======

def make_graph(n: int, m: int) -> Graph:
    """
    Generate a random connected, undirected graph with
    n vertices and m edges, with integer weights in [1, 100].
    """
    if m < n - 1:
        raise ValueError("Number of edges must be at least n-1 for a connected graph")

    g = Graph()
    labels = [f"J{i + 1}" for i in range(n)]
    for label in labels:
        g.get_vertex(label) # Pre-populate all Junctions

    uf = UnionFind(labels)
    existing_edges = set()
    tree_edges = 0
    
    # First: build a tree with (n-1) edges to guarantee connectivity
    while tree_edges < n - 1:
        u_idx = random.randint(0, n - 1)
        v_idx = random.randint(0, n - 1)
        if u_idx == v_idx:
            continue
        
        u = labels[u_idx]
        v = labels[v_idx]
        
        if uf.find(u) == uf.find(v):
            continue # Already connected
            
        uf.union(u, v)
        w = random.randint(1, 100)
        g.add_edge(u, v, w)
        key = tuple(sorted((u, v)))
        existing_edges.add(key)
        tree_edges += 1

    # Then: add remaining edges (avoiding duplicates)
    remaining = m - (n - 1)
    added = 0
    while added < remaining:
        u_idx = random.randint(0, n - 1)
        v_idx = random.randint(0, n - 1)
        if u_idx == v_idx:
            continue
        
        u_label = labels[u_idx]
        v_label = labels[v_idx]
        key = tuple(sorted((u_label, v_label)))

        # Check if this edge already exists
        if key in existing_edges:
            continue
            
        w = random.randint(1, 100)
        g.add_edge(u_label, v_label, w)
        existing_edges.add(key)
        added += 1

    return g


# ====== Helper: print MST ======

def print_mst(title: str, algo: MstAlgorithm):
    """Helper function to print MST in the required format."""
    print(title)
    # Get edges and total from the algorithm object
    edges = algo.result
    total = algo.totalWeight()
    for e in edges:
        print(f"{e.u.label} — {e.v.label} : {e.weight}")
    print(f"Total = {total}")


# ====== Main ======

if __name__ == "__main__":
    
    print("--- Requirement 1: MST from File ---")
    prim_edges_for_plot = []
    try:
        # Create Graph and call readFromFile (UML compliant)
        g = Graph()
        g.readFromFile("graph.txt")
        
        if g.vertices: # Only run if graph was loaded successfully
            prim = PrimAlg()
            prim.findMST(g)
            print_mst("MST (Min-Heap Prim):", prim)
            prim_edges_for_plot = prim.result # Save for plot
            
            print() # Add a newline
            
            kruskal = KruskalAlg()
            kruskal.findMST(g)
            print_mst("MST (Kruskal):", kruskal)
            
            # --- Added: Visualization for Req 1 ---
            # This plots the MST from Prim's
            print("\nVisualizing MST for Requirement 1...")
            G_nx = nx.Graph()
            for e in prim_edges_for_plot:
                G_nx.add_edge(e.u.label, e.v.label, weight=e.weight)
            nx.draw(G_nx, with_labels=True, font_weight='bold')
            plt.show()
            # ----------------------------------------
            
        else:
            print("Graph is empty. Halting.")
            
    except FileNotFoundError:
        print("Error: 'graph.txt' not found.")
        print("Please create 'graph.txt' in the same folder.")
    except Exception as e:
        print(f"An error occurred: {e}")


    print("\n--- Requirement 2: Experimental Comparison ---")
    sizes = [
        (1000, 10000), (1000, 15000), (1000, 25000),
        (5000, 15000), (5000, 25000),
        (10000, 15000), (10000, 25000),
    ]

    print(f"{'n (Verts)':<10} | {'m (Edges)':<10} | {'Prim Time (ms)':<15} | {'Kruskal Time (ms)':<17}")
    print("-" * 60)

    for n, m in sizes:
        g_rand = make_graph(n, m)

        # Time Prim's
        prim_alg = PrimAlg()
        start = time.perf_counter()
        prim_alg.findMST(g_rand)
        prim_time = (time.perf_counter() - start) * 1000

        # Time Kruskal's
        krus_alg = KruskalAlg()
        start = time.perf_counter()
        krus_alg.findMST(g_rand)
        krus_time = (time.perf_counter() - start) * 1000

        print(f"{n:<10} | {m:<10} | {prim_time:<15.2f} | {krus_time:<17.2f}")