import game as gm
import random
import math
import mctsnode
from copy import deepcopy
from open_spiel.python.examples.mcts_agent import MCTS

class Agent:
    def __init__(self, color, type):
        self.color = color
        self.type = type

        self.decisionFunction = None
        if self.type == "random":
            self.decisionFunction = self.random
        elif self.type == "negamax":
            self.decisionFunction = self.minimax
        elif self.type == "human":
            self.decisionFunction = self.human
        elif self.type == "montecarlo":
            self.decisionFunction = self.mcts
        elif self.type == "MCTS_OpenSpiel":
            self.mctsAgent = MCTS(rollout_count=1, max_simulations=2000)
            self.decisionFunction = self.mcts_openspiel

        self.maxDepth = 4
        self.maxTrials = 2000
    
    def mcts_openspiel(self, gameState):

        if self.color == "black" and len(gameState.wMoves) > 0:
            self.mctsAgent.OPPONENTmove(gameState.wMoves[len(gameState.wMoves) - 1])
        if self.color == "white" and len(gameState.bMoves) > 0:
            self.mctsAgent.OPPONENTmove(gameState.bMoves[len(gameState.bMoves) - 1])

        action = self.mctsAgent.AGENTmove()
        return action

    def random(self, gameState):
        # Pick random move
        pick = random.randint(0, len(gameState.legalMoves) - 1)
        pick = gameState.legalMoves[pick]
        return gameState.nodes[pick].id

    def human(self, gameState):
        # Controlled by human
        pass

    def minimax(self, gameState):
        bestMove = self.negamax(gameState, self.maxDepth, -math.inf, math.inf, self.color, None)
        return bestMove
    def negamax(self, gameState, depth, alpha, beta, color, move):
        if move != None:
            initialVal = self.evaluateGameState(gameState, color, move)
            if math.isinf(initialVal) or depth == 0:
                return initialVal

        value = -math.inf
        bestMove = gameState.legalMoves[0]
        for i in gameState.legalMoves:
            currentGameState = deepcopy(gameState)
            currentGameState.processMove(i, color)

            oppositeColor = "white" if color == "black" else "black"
            oppositeVal = self.negamax(currentGameState, depth - 1, -beta, -alpha, oppositeColor, i)
            childVal = -oppositeVal
            bestMove = i if childVal > value else bestMove
            value = max(value, childVal)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        if depth == self.maxDepth:
            return bestMove
        return value

    def evaluateGameState(self, gameState, color, move):
        winner = gameState.findWinner(move)
        if winner == color:
            return math.inf
        elif winner == "none":
            score = 0
            for i in gameState.nodes:
                score += len(i.circuitNeighbors[color])
            return score
        return -math.inf



    def mcts(self, gameState):
        root = mctsnode.Node(deepcopy(gameState), self.color, None, None)
        root.expand_node()

        trials = 0
        while trials < self.maxTrials:
            # Selection and Expansion
            pick = root
            while len(pick.children) > 0:
                bestScore, bestChild = 0, pick.children[0]
                for child in pick.children:
                    res = 0.5
                    if child.trials != 0:
                        res = child.wins / child.trials * math.sqrt(4 * math.log(pick.trials) / child.trials)
                    if res > bestScore:
                        bestScore = res
                        bestChild = child
                pick = bestChild
                #pick = random.choice(pick.children)
            pick.expand_node()

            # Simulation
            winner = pick.simulate()

            # Backpropagation
            while pick.parent is not None:
                pick.trials += 1
                if winner != pick.color:
                    pick.wins += 1
                pick = pick.parent
            trials += 1
            pick.trials += 1

        bestWinPercentage, bestMove = 0, gameState.legalMoves[0]
        for child in root.children:
            winpercent = child.wins / child.trials if child.trials != 0 else 0
            print(child.wins, child.trials)
            if winpercent > bestWinPercentage:
                bestMove, bestWinPercentage = child.move, winpercent
        return bestMove
