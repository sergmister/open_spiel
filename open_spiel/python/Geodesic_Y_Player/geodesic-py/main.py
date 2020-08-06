import tkinter as tk
import cells
import math
import game as gm
import graph
import time
import agent

winnerFlag = "none"
color = "black"
oneAIPlaying = False
humanPlaying = False

# finding graph size

def graphSize(n):
    spaces = 3 * (n ** 2 - n) // 2
    print('   Your board of base ' + str(n) + " has " + str(spaces) + " spaces")
    return graph.generateNSizedGraph(n)

g = 0
n = 5
print('Welcome to Command Line Y!')
"""
while True:
    try:
        n = int(input('Please enter the base size of the board: '))
        if n >= 2:
            break
        if n < 2:
            print('   Error: base must be an integer greater than 1')
    except:
        print('   Error: base must be an integer greater than 1')
"""
g = graphSize(n)

def updateWinnerLabel():
    if winnerFlag != "none":
        startLabel.grid(row=0, column=3)
        startLabel.config(text=winnerFlag.capitalize() + " has won!")

def doAIMove():
    decision = None
    if color == "black":
        decision = bAgent.decisionFunction(game)
        game.processMove(decision, "black")
        cnv.create_polygon(grph["polygons"][decision], fill="blue", outline="black", width=4)
    elif color == "white":
        decision = wAgent.decisionFunction(game)
        game.processMove(decision, "white")
        cnv.create_polygon(grph["polygons"][decision], fill="red", outline="black", width=4)
    cnv.update()

    global winnerFlag
    winnerFlag = game.findWinner(decision)

    updateWinnerLabel()


def doHumanMove(decision):
    game.processMove(decision, color)
    fillColor = "blue" if color == "black" else "red"
    cnv.create_polygon(grph["polygons"][decision], fill=fillColor, outline="black", width=4)

    global winnerFlag
    winnerFlag = game.findWinner(decision)
    updateWinnerLabel()

def playTwoAIs():
    global color
    while winnerFlag == "none":
        time.sleep(0.1)
        doAIMove()
        color = "white" if color == "black" else "black"

def play():
    global game, oneAIPlaying, color, humanPlaying, wAgent, bAgent
    ptb = player1Agent.get().lower()
    ptw = player2Agent.get().lower()

    if ptb != "human": ptb = ptb[:len(ptb)-5]
    if ptw != "human": ptw = ptw[:len(ptw)-5]

    game = gm.Game(g)
    
    if ptb == "human":
        bAgent = agent.Agent("black", "human")
    elif ptb == "negamax":
        bAgent = agent.Agent("black", "negamax")
        bAgent.maxDepth = 0 + 1
    elif ptb == "random":
        bAgent = agent.Agent("black", "random")
    elif ptb == "montecarlo":
        bAgent = agent.Agent("black", "montecarlo")
    elif ptb == "mcts_openspiel":
        bAgent = agent.Agent("black", "MCTS_OpenSpiel")

    if ptw == "human":
        wAgent = agent.Agent("white", "human")
    elif ptw == "negamax":
        wAgent = agent.Agent("white", "negamax")
        wAgent.maxDepth = 0 + 1
    elif ptw == "random":
        wAgent = agent.Agent("white", "random")
    elif ptw == "montecarlo":
        wAgent = agent.Agent("white", "montecarlo")
    elif ptw == "mcts_openspiel":
        wAgent = agent.Agent("white", "MCTS_OpenSpiel")

    global startButton, startLabel
    startButton.grid_forget()
    startLabel.grid_forget()

    if bAgent.type != "human" and wAgent.type != "human":
        playTwoAIs()
    elif bAgent.type != "human" or wAgent.type != "human":
        oneAIPlaying = True
        humanPlaying = True
    else:
        humanPlaying = True


    if bAgent.type != "human" and oneAIPlaying == True:
        doAIMove()
        color = "white"


# GUI SETUP -------------------------------------------------------------------------------------------------

agentTypes = ["Human", "Random (AI)", "Negamax (AI)", "MonteCarlo (AI)", "MCTS_OpenSpiel (AI)"]

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500

grph = cells.getCoordinates(n, WINDOW_WIDTH/2, WINDOW_HEIGHT/2)

window = tk.Tk()

cnv = tk.Canvas(window, bg="white", width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
guiFrame = tk.Frame(window)

player1Agent = tk.StringVar()
player1Agent.set(agentTypes[0])
player1Dropdown = tk.OptionMenu(guiFrame, player1Agent, *agentTypes)
player1Label = tk.Label(guiFrame, text="Player 1")

player2Agent = tk.StringVar()
player2Agent.set(agentTypes[0])
player2Dropdown = tk.OptionMenu(guiFrame, player2Agent, *agentTypes)
player2Label = tk.Label(guiFrame, text="Player 2")

startLabel = tk.Label(guiFrame, text="Start Game")
startButton = tk.Button(guiFrame, text="Play", command=play)

guiFrame.grid_columnconfigure(2, weight=1)
guiFrame.grid_columnconfigure(4, weight=1)

player1Label.config(font="Courier 14 bold")
player2Label.config(font="Courier 14 bold")
startLabel.config(font="Courier 14 bold")

player1Dropdown.config(width=13)
player2Dropdown.config(width=13)

player1Label.grid(row=0, column=0)
player1Dropdown.grid(row=1, column=0)
player2Label.grid(row=0, column=6)
player2Dropdown.grid(row=1, column=6)

startLabel.grid(row=0, column=3)
startButton.grid(row=1, column=3)

for poly in grph["polygons"]:
    cnv.create_polygon(poly, fill="white", outline="black", width=4)

def mouseClick(event):
    global color
    if winnerFlag == "none" and humanPlaying == True:
        shortest = math.inf
        closest = None
        for center in grph["centers"]:
            dist = math.sqrt((event.x - center[0]) ** 2 + (event.y - center[1]) ** 2)
            if dist < shortest: shortest, closest = dist, grph["centers"].index(center)
        if closest in game.legalMoves:
            doHumanMove(closest)
            color = "white" if color == "black" else "black"
            if oneAIPlaying == True and winnerFlag == "none":
                doAIMove()
                color = "white" if color == "black" else "black"


cnv.bind("<Button-1>", mouseClick)

cnv.pack(side="top", fill="x")
guiFrame.pack(side="bottom", fill="both", expand=True)

window.mainloop()
