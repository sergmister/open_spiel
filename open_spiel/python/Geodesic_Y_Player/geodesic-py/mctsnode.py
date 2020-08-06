import random
from copy import deepcopy

class Node:
    def __init__(self, gameState, color, parent, move):
        self.gameState, self.color = gameState, color
        self.parent = parent
        self.children = []
        self.move = move

        self.wins = 0
        self.trials = 0

    def expand_node(self):
        if self.move != None:
            self.gameState = deepcopy(self.gameState)
            if self.gameState.findWinner(self.move) != "none":
                return
            self.gameState.processMove(self.move, self.parent.color)
            if self.gameState.findWinner(self.move) != "none":
                return
        color = "black"
        if self.color == "black":
            color = "white"
        else:
            color = "black"
        for i in self.gameState.legalMoves:
            #state = deepcopy(self.gameState)
            #state.processMove(i, self.color)
            nc = Node(self.gameState, color, self, i)
            self.children.append(nc)


    def simulate(self):
        state = deepcopy(self.gameState)
        winner = state.findWinner(self.move)
        color = "white" if self.color == "black" else "black"
        while winner == "none":
            pick = random.choice(state.legalMoves)
            state.processMove(pick, color)
            color = "white" if color == "black" else "black"
            winner = state.findWinner(pick)
        #del self.gameState  use this linet to potentially save memory
        return winner
