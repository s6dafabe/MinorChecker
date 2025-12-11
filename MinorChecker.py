import argparse
import pickle

import networkx as nx
from pysat.formula import IDPool
from pysat.solvers import Cadical195
import pysat.card as card
import time
from pathlib import Path

class MinorChecker:
    def __init__(self, graph:nx.Graph,k):
        self.graph:nx.Graph = graph
        self.n = self.graph.number_of_nodes()
        self.k = k
        self.has_run = False
        self.cadical = Cadical195()
        self.satisfiable = False
        self.pool = IDPool()

        for i in range(self.k):
            for v in self.graph.nodes():
                self.pool.id((v,i))
            for v in self.graph.nodes():
                for o in range(self.n):
                    self.pool.id((v, o, i))
            for j in range(self.k):
                for u, v in graph.edges():
                    self.pool.id((u, v, i, j))
        self.runtime = 0
    def run(self):
        start = time.time()
        # Constraining orders
        for i in range(self.k):
            #There must be one root for every partition
            self.cadical.append_formula(card.CardEnc.equals(
                [self.pool.id((v,0,i)) for v in self.graph.nodes()], vpool=self.pool))
            for v in self.graph.nodes():
                for o in range(self.n):
                    pass
                    # v can only be assigned to order o in i if it is assigned to i
                    self.cadical.add_clause([-self.pool.id((v,o,i)),self.pool.id((v,i))])
                # v can only be assigned to exactly one order
                self.cadical.append_formula(
                    card.CardEnc.atmost([self.pool.id((v,o,i)) for o in range(self.n)], vpool=self.pool))
                self.cadical.add_clause([self.pool.id((v,o,i)) for o in range(self.n)]+[-self.pool.id((v,i))])

        # Each vertex assigned to at most one partition
        for v in self.graph.nodes():
            pass
            self.cadical.append_formula(card.CardEnc.atmost([self.pool.id((v,i)) for i in range(self.k)],vpool=self.pool))

        #Connectivity constraints
        for i in range(self.k):
            for v in self.graph.nodes():
                for o in range(1,self.n):
                    pass
                    # Vertex v can only be assigned to i in order of o if it has a neighbor assigned to i in order o-1
                    self.cadical.add_clause([-self.pool.id((v,o,i))]+
                                            [self.pool.id((w,o-1,i)) for w in self.graph.neighbors(v)]
                                            )
            #Contact constraints
            for j in range(self.k):
                #Contact between partition i and j over edge u, v only if u->i and v->j
                for u, v in self.graph.edges():
                    self.cadical.add_clause([self.pool.id((u,i)),-self.pool.id((u,v,i,j))])
                    self.cadical.add_clause([self.pool.id((v, j)), -self.pool.id((u, v, i, j))])
                if i >= j: continue
                self.cadical.add_clause(
                    sum(([self.pool.id((u,v,i,j)),self.pool.id((u,v,j,i))] for u,v in self.graph.edges()),start = [])
                )


        self.satisfiable = self.cadical.solve()
        self.has_run = True
        self.runtime = time.time()-start

    def get_solution(self):
        if not self.has_run:
            raise RuntimeError("Algorithm has not run yet")
        if not self.satisfiable:
            print("No solution found")
            return []
        else:
            print("Solution found")
            sol = [-1]*self.graph.number_of_nodes()
            for v in self.graph.nodes():
                for i in range(self.k):
                    if self.cadical.get_model()[self.pool.id((v,i))-1]> 0:
                        sol[v] = i
            assert(check_solution(sol,self.graph,self.k))
            return sol

    def contains_minor(self):
        if not self.has_run:
            raise RuntimeError("Algorithm has not run yet")
        return self.satisfiable
    def get_runtime(self):
        if not self.has_run:
            raise RuntimeError("Algorithm has not run yet")
        return self.runtime

def check_solution(solution,graph:nx.Graph,k):
    partition_map = [[] for _ in range(k)]
    for v,i in enumerate(solution):
        if solution[v] < 0: continue
        partition_map[i].append(v)
    for i,part in enumerate(partition_map):
        if len(part) == 0: return False
        subgraph = nx.subgraph(graph,part)
        if not nx.is_connected(subgraph): return False
        adj_partitions = set()
        for w in nx.node_boundary(graph,part):
            adj_partitions.add(solution[w])
        if len(adj_partitions) < k-1: return False
    return True
def read_dimacs(path):
    """
    Reads a DIMACS-format graph file and returns a NetworkX Graph.
    Supports lines like:
      c comment...
      p edge <num_nodes> <num_edges>
      e u v
    """
    G = nx.Graph()

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            # Skip empty and comment/problem lines
            if not line or line.startswith("c") or line.startswith("p"):
                continue

            if line.startswith("e"):
                # Format: e u v
                _, u, v = line.split()
                G.add_edge(int(u)-1, int(v)-1)

    return G

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads a graph file and the size k of the minor")
    parser.add_argument("graph", type=str,
                        help="File of the input graph. Either a graph in DIMACS format or a .pkl file of a networkx graph")
    parser.add_argument("k", type=int, help="The size k of the minor")

    args = parser.parse_args()
    graph_path = Path(args.graph)

    nx_graph = nx.Graph()
    if graph_path.suffix in [".pkl",".pickle"]:
        with open(graph_path, "rb") as f:
            nx_graph = pickle.load(f)
    else:
        nx_graph = read_dimacs(graph_path)

    minor_checker = MinorChecker(nx_graph,args.k)
    minor_checker.run()
    print(f"Contains minor: {minor_checker.contains_minor()}")
    if minor_checker.contains_minor():
        print(f"Assignment: {minor_checker.get_solution()}")







