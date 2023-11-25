# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        score = 0
        currentPos = currentGameState.getPacmanPosition()
        #check the next move will not be into a square where a ghost is
        for ghostState in newGhostStates:
            if manhattanDistance(newPos, ghostState.getPosition()) == 0:      
                score = -50
            else:
                score = score - manhattanDistance(ghostState.getPosition(), newPos)
        
        #incentivise the pacman not to stop as we lose score with time
        if action == 'Stop':
            score = score - 30
        
        #find the closest food
        closestFood = (100,100)
        for food in newFood.asList():
            if (manhattanDistance(newPos, food) < manhattanDistance(newPos, closestFood)):
                closestFood = food
        
        #if the food is closer, give a better score
        if (manhattanDistance(newPos, closestFood) == 0):
            score = score + 50
        elif (manhattanDistance(currentPos, closestFood) > manhattanDistance(newPos, closestFood)):
            score = score + 30
        elif (manhattanDistance(currentPos, closestFood) == manhattanDistance(newPos, closestFood)):
            score = score - 10
        else:
            score = score
        
        #return the score we got plus the already provided score from gamestate
        return successorGameState.getScore() + score

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        legalActions = gameState.getLegalActions(0)
        bestAction = None
        bestEval = -99999        
        
        #for each possible action, calculate the minimax score and choose the best one
        for action in legalActions:
            depth = self.depth
            successor = gameState.generateSuccessor(0, action)
            
            #call minimax starting with the first ghost (index = 1)   
            miniMaxScore = self.miniMax(successor, 1, depth - 1) 
            
            #take the best action of each possible next action
            if miniMaxScore > bestEval:
                bestEval = miniMaxScore
                bestAction = action
                
        return bestAction          
        util.raiseNotDefined()
    
    #takes the gameState and if the player is a ghost or pacman and returns the minimax score
    def miniMax(self, gameState, index, depth):
        #if depth has been reached, goal state, lost state or no more possible moves, return the evaluation of the position
        if depth < 0 or len(gameState.getLegalActions(index)) == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        
        # max agent
        if index == 0:
            bestEval = -99999
            # recursively call miniMax on all possible next actions
            for action in gameState.getLegalActions(index):
                    successor = gameState.generateSuccessor(index, action)
                    miniMaxScore = self.miniMax(successor, index + 1, depth) 
                    bestEval = max(bestEval, miniMaxScore)
            return bestEval              
        
        # min agent
        if index != 0: 
            bestEval = 99999
            for action in gameState.getLegalActions(index):
                    #recursively call miniMax on all possible next actions
                    successor = gameState.generateSuccessor(index, action)
                    if index + 1 == gameState.getNumAgents():
                        miniMaxScore = self.miniMax(successor, 0, depth -1)
                    else: #if more than one ghost then don't decrement the depth
                        miniMaxScore = self.miniMax(successor, index + 1, depth)
                    bestEval = min(bestEval, miniMaxScore)
            
            return bestEval
    
    
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        legalActions = gameState.getLegalActions(0)
        bestAction = None
        bestEval = -999999   
        alpha = -999999
        beta = 999999     
        
        #for each possible action, calculate the minimax score and choose the best one
        for action in legalActions:
            depth = self.depth
            successor = gameState.generateSuccessor(0, action)
            
            #call miniMaxPrune starting with the first ghost (index = 1)   
            miniMaxScore = self.miniMaxPrune(successor, 1, depth - 1, alpha, beta) 
            
            #take the best action of each possible next action
            if miniMaxScore > bestEval:
                bestEval = miniMaxScore
                bestAction = action
            
            #pruning at the top level also
            alpha = max(alpha, bestEval)
            if beta <= alpha:
                break
                    
        return bestAction        
        util.raiseNotDefined()

    def miniMaxPrune(self, gameState, index, depth, alpha, beta):
        #if depth has been reached, goal state, lost state or no more possible moves, return the evaluation of the position
        if depth < 0 or len(gameState.getLegalActions(index)) == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        
        # max agent
        if index == 0:
            bestEval = -999999
            # recursively call miniMaxPrune on all possible next actions
            for action in gameState.getLegalActions(index):
                    #get the successor and run miniMaxPrune on it
                    successor = gameState.generateSuccessor(index, action)
                    miniMaxPruneScore = self.miniMaxPrune(successor, index + 1, depth, alpha, beta)
                    bestEval = max(bestEval, miniMaxPruneScore)
                    alpha = max(alpha, bestEval)
                    if beta < alpha:
                        break
            return bestEval          
        
        # min agent
        if index != 0: 
            bestEval = 999999
            for action in gameState.getLegalActions(index):
                    #get the successor and run miniMaxPrune on it
                    successor = gameState.generateSuccessor(index, action)
                    if index + 1 == gameState.getNumAgents():
                        miniMaxPruneScore = self.miniMaxPrune(successor, 0, depth -1, alpha, beta)
                    else: #if more than one ghost then don't decrement the depth
                        miniMaxPruneScore = self.miniMaxPrune(successor, index + 1, depth, alpha, beta)
                    bestEval = min(bestEval, miniMaxPruneScore)
                    beta = min(beta, bestEval)
                    if beta < alpha:
                        break
            return bestEval

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        legalActions = gameState.getLegalActions(0)
        bestAction = None
        bestEval = -99999        
        
        #for each possible action, calculate the minimax score and choose the best one
        for action in legalActions:
            depth = self.depth
            successor = gameState.generateSuccessor(0, action)
            
            #call minimax starting with the first ghost (index = 1)   
            expectiMaxScore = self.expectiMax(successor, 1, depth - 1) 
            
            if expectiMaxScore > bestEval:
                bestEval = expectiMaxScore
                bestAction = action
        
        return bestAction
            
        
    def expectiMax(self, gameState, index, depth):
        #if depth has been reached, goal state, lost state or no more possible moves, return the evaluation of the position
        if depth < 0 or len(gameState.getLegalActions(index)) == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        
        # min agent
        if index != 0: 
            # to hold expected value of possible child nodes
            expectedValue = 0
            for action in gameState.getLegalActions(index):
                successor = gameState.generateSuccessor(index, action)  
                if index + 1 == gameState.getNumAgents():
                    value = self.expectiMax(successor, 0, depth - 1)              
                else:
                    value = self.expectiMax(successor, index + 1, depth)
                # take the average of the children's values
                expectedValue += ( 1 / len(gameState.getLegalActions(index))) * value
            return expectedValue
        
        #max agent
        elif index == 0:
            bestEval = -999999
            for action in gameState.getLegalActions(index):
                successor = gameState.generateSuccessor(index, action)
                expectiMaxScore = self.expectiMax(successor, index + 1, depth)
                bestEval = max(bestEval, expectiMaxScore) 
            return bestEval
    
        util.raiseNotDefined()
            

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    currentPos = currentGameState.getPacmanPosition()
    
    #distance to closest food
    closestFood = (100,100)
    distanceToCloseFood = 100
    for food in currentGameState.getFood().asList():
        if (manhattanDistance(currentPos, food) < manhattanDistance(currentPos, closestFood)):
            distanceToCloseFood = manhattanDistance(currentPos, food)
            closestFood = food
    
    #score of the game
    gameScore = currentGameState.getScore()    
    
    #distance to closest ghost
    closestGhost = (100,100)
    distanceToCloseGhost = 100
    for ghost in currentGameState.getGhostPositions():
        if (manhattanDistance(currentPos, ghost)) < manhattanDistance(currentPos, closestGhost):
            closestGhost = ghost
            distanceToCloseGhost = manhattanDistance(currentPos, ghost)
    
    #locations of capsules
    capsules = len(currentGameState.getCapsules())
    
    # amount of food list
    amountOfFoodLeft = len(currentGameState.getFood().asList())
    
    #return a weighted score based on all the above factors and the state of the game
    if distanceToCloseGhost > 12:
        return (gameScore * 2) + (distanceToCloseFood * -3/2) - amountOfFoodLeft
    if distanceToCloseGhost > 8:
        return (gameScore * 2) + (distanceToCloseFood * (-1.5)) - amountOfFoodLeft
    elif  distanceToCloseFood == 1 and distanceToCloseGhost > 3:
        return (gameScore * 1.5) 
    else:
        return (distanceToCloseFood * (-1)) + (distanceToCloseGhost * 1) + (gameScore * 0.1) - (capsules*4) - (amountOfFoodLeft * 0.5)
     

# Abbreviation
better = betterEvaluationFunction
