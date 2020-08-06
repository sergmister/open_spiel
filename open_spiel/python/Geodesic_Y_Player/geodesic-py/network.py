# NetworkX File

import math
import graph
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Network:
    def __init__(self, g):
        self.netw = nx.Graph()
        self.shells = []
        self.labels = {}
        self.graph = g

        # Add nodes, edges, and labels
        self.netw.add_nodes_from(range(len(g)))
        for i in range(len(g)):
            for j in g[i]:
                self.netw.add_edge(i, j)
                self.labels[i] = str(i)

        # Add shells
        N = int((1/6) * (math.sqrt(24 * len(g) + 9) + 3)) # Find N value
        for i in range(1, N):
            lowerBound = graph.getSmallestCellNumber(i + 1)
            upperBound = graph.getSmallestCellNumber(i + 2)
            self.shells.append(range(lowerBound, upperBound))

        self.pos = nx.shell_layout(self.netw, self.shells)

        self.values = self.setSpecialColors(N)

        plt.ion() # Set interactive

    def draw(self, gameNodes):
        plt.clf()
        for i in self.netw.nodes:
            color = gameNodes[i].color if gameNodes[i].color != "empty" else "grey"
            if i in self.values.keys():
                if gameNodes[i].color != "empty":
                    self.values[i] = gameNodes[i].color
                color = self.values[i]
            nds = nx.draw_networkx_nodes(self.netw, self.pos, nodelist=[i], node_color=color)
            nds.set_edgecolor("black")

            fontC = "black"
            if gameNodes[i].color == "black":
                fontC = "white"
            nx.draw_networkx_labels(self.netw, self.pos, {i: i}, font_color=fontC)

        for i in self.netw.edges:
            color = "grey"
            wid = 1.0
            alph = 0.2
            if gameNodes[i[0]].color == gameNodes[i[1]].color and gameNodes[i[0]].color != "empty":
                color = gameNodes[i[0]].color if gameNodes[i[0]].color != "white" else "grey"
                wid = 3.0
                alph = 1.0
            nx.draw_networkx_edges(self.netw, self.pos, edgelist=[i], width=wid, edge_color=color, alpha=alph)
        plt.pause(0.1)
        plt.draw()


    def setSpecialColors(self, N):
        first = graph.getCorner(0, N)
        second = graph.getCorner(1, N)
        third = graph.getCorner(2, N)
        next = graph.getCorner(0, N + 1)

        values = {}
        for i in range(first + 1, second):
            values[i] = "red"
        for i in range(second + 1, third):
            values[i] = "green"
        for i in range(third + 1, next):
            values[i] = "blue"

        values[first] = "gold"
        values[second] = "gold"
        values[third] = "gold"

        return values
