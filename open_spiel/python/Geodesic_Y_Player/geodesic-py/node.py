# node class
from graph import getEdge
import math

class Node:
    def __init__(self, key, graph):
        self.id = key
        self.color = "empty"
        self.neighbors = graph[key]
        self.parent = self.id

        self.circuitNeighbors = { "black": self.neighbors[:], "white": self.neighbors[:] }
        N = int((1/6) * (math.sqrt(24 * len(graph) + 9) + 3)) # Find N value, base size
        self.edges = getEdge(self.id, N)

    def updateCircuitNeighbors(self, nd):
        oppositeColor = "white" if nd.color == "black" else "black"
        self.circuitNeighbors[nd.color].remove(nd.id)
        for i in nd.circuitNeighbors[nd.color]:
            if i == self.id: continue
            if i not in self.circuitNeighbors[nd.color]:
                self.circuitNeighbors[nd.color].append(i)

        self.circuitNeighbors[oppositeColor].remove(nd.id)

