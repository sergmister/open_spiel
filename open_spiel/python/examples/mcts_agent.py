import random
import numpy as np

from open_spiel.python.algorithms import mcts
import pyspiel

class MCTS:
  def __init__(self, rollout_count=5, max_simulations=4000):
    rng = np.random.RandomState(None)
    evaluator = mcts.RandomRolloutEvaluator(rollout_count, rng)
    self.game = pyspiel.load_game("geodesic_y")
    self.state = self.game.new_initial_state()
    self.agent = mcts.MCTSBot(
      self.game,
      2,
      max_simulations,
      evaluator,
      random_state=rng,
      solve=True,
      verbose=False)
    
  def AGENTmove(self):
    action = self.agent.step(self.state)
    self.state.apply_action(action)
    return action
    
  def OPPONENTmove(self, action):
    self.agent.inform_action(self.state, self.state.current_player(), action)
    self.state.apply_action(action)

  def reset(self):
    self.agent.restart()

if __name__ == "__main__":
  agent = MCTS(rollout_count=5, max_simulations=2000)
  agent.OPPONENTmove(10)
  print(agent.AGENTmove())
  print(agent.state)