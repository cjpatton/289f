# sim.py - Simulation of asynchronous consensus models.
# TODO
#  - RelucatantAgent
#
import igraph
import random

#
# The simulator does integer arithmetic under the hood in order to 
# speed things up. `PRECISION` can be adjusted to increase or 
# decrease precision. 
#

PRECISION = 10 ** 5
SHIFT = lambda(x) : int(x * PRECISION)
UNSHIFT = lambda(x) : float(x) / PRECISION


#
# Asynchronous opnion dynamics models. Nodes of `g` are expected to have 
# an `agency` attribute. `q` in [0 .. 1] is the weight of the alternate
# opinion when updating. 
#

def SymmetricGossip(g, q, round_no):
  # Choose an edge in `g` uniformly and have the nodes exchange opinions,
  (u,v) = g.es[random.randint(0, g.ecount() - 1)].tuple
  opinion = g.vs[u]['agency'].opinion
  g.vs[u]['agency'].UpdateOpinion(g.vs[v], g.vs[v]['agency'].opinion, q, round_no)
  g.vs[v]['agency'].UpdateOpinion(g.vs[u], opinion, q, round_no)

def AsymmetricGossip(g, q, round_no):
  # choose a node from `g` uniformly and have it share its opinion with
  # one of its neighbors, chosen uniformly. 
  u = g.vs[random.randint(0, g.vcount() - 1)]
  if u.degree() > 0:
    v = u.neighbors()[random.randint(0, u.degree() - 1)]
    u['agency'].UpdateOpinion(v, v['agency'].opinion, q, round_no)

def Broadcast(g, q, round_no): 
  # Choose a node from `g` uniformly and update its neighbors' opinions. 
  u = g.vs[random.randint(0, g.vcount() - 1)]
  for v in u.neighbors(): 
    v['agency'].UpdateOpinion(u, u['agency'].opinion, q, round_no)
    
  


#
# Simulate opinion dynamics over `g` given a particular mode. Run 
# until convergence, at most `rounds` times. If no agents are 
# provided, standard agents with initial opinion between 0 and 10 
# are generated. Note that the graph `g` need not be fully connected. 
#

class Simulation: 
 
  def __init__(self, g, agents=None):
    self.g = g
    if agents:
      assert len(agents) == len(g.vs)
      selg.g.vs['agency'] = agents
    else:
      self.g.vs['agency'] = [ 
                  Agent(random.uniform(0,10)) for i in range(len(g.vs)) ]

  def SetOpinionsUnif(self, low, high):
    # Set opinions by selecting a real value uniformly high and low. 
    for agent in self.g.vs['agency']:
      agent.SetOpinion(random.uniform(low, high))

  def RestoreOpinions(self):
    # Restore initial opinion for all agents. 
    for agent in self.g.vs['agency']:
      agent.RestoreInitialOpinion()

  def SetOpinion(self, i, opinion):
    # Set opinion of node `i` to `opinion`. 
    self.g.vs[i]['agency'].SetOpinion(opinion)

  def SetAgentType(self, i, agentType):
    # Configure agency of node `i`.
    self.g.vs[i]['agency'] = agentType(self.g.vs[i]['agency'].initialOpinion)

  def IterAgents(self): 
    # Return a list of (Vertex, Agent) pairs.
    for u in self.g.vs: 
      yield (u, u['agency'])

  def Run(self, dynamicsModel=SymmetricGossip, q=0.5, rounds=1000):
    # Run simulation some number of rounds w/o checking 
    # for convergence. (For efficiency's sake.)
    q = SHIFT(q)
    for r in range(rounds):
      dynamicsModel(self.g, q, r)
    return [ agent.GetOpinion() for agent in self.g.vs['agency'] ]

  def TimeOfConvergence(self, err=0.0001):
    # Compute the number of rounds until convergence. (Note that the 
    # result isn't valid if consensus hasn't been reached.) Look at
    # the transaction histories of the node and find the round 
    # number when their opinion converged to consensus. 
    err = SHIFT(err)
    round_nos = []
    for u in range(len(self.g.vs)):
      agent = self.g.vs[u]['agency']
      consensus = agent.opinion
      i = len(agent.history) - 1
      while i >= 0 and abs(agent.history[i][0] - consensus) <= err:
        i -= 1
      round_nos.append(agent.history[i][1])
    return max(round_nos)

  def TestConvergence(self, err=0.0001):
    # Test if consenus has been reached. 
    err = SHIFT(err)
    for c in self.g.components():
      W = [ self.g.vs[u]['agency'].opinion for u in c ]
      if (max(W) - min(W)) > err: 
        return False
    return True

  def RunUntilConvergence(self, dynamicsModel=SymmetricGossip, 
                                 q=0.5, 
                                 max_rounds=1000, 
                                 err=0.0001):
 
    # Return a tuple (r, W) containing the number of rounds 
    # and the final opinion vector resp. This is way more slow
    # than running a bunch of rounds and tesing for convergence. 

    cc = self.g.components()
    for r in range(max_rounds):
      # Iterate dynamics model. 
      dynamicsModel(self.g, q)

      # Test for convergence.
      convergence = True
      for c in cc:
        W = [ self.g.vs[u]['agency'].opinion for u in c ]
        if (max(W) - min(W)) > err: 
          convergence = False
          break

      if convergence:
        return (r+1, [ agent.opinion for agent in self.g.vs['agency'] ])

    return (r+1, [ agent.opinion for agent in self.g.vs['agency'] ])

#
# Agents. Opinion is typically a real scalar, but can be any type 
# that supports addition, scalar multiplication and division, min(), 
# max(), and int(). 
#

class Agent:

  # Standard agent type. Constructor accepts an initial opinion
  # and `q` in [0 .. 1], the weight of alternative opinions. 

  def __init__(self, initialOpinion):
    self.history = [(SHIFT(initialOpinion), 0)]
    self.initialOpinion = self.opinion = SHIFT(initialOpinion)

  def RestoreInitialOpinion(self):
    self.opinion = self.initialOpinion
  
  def SetOpinion(self, opinion):
    self.opinion = SHIFT(opinion)

  def GetOpinion(self):
    return UNSHIFT(self.opinion)

  def UpdateOpinion(self, anAgent, altOpinion, q, round_no): 
    self.opinion = ((PRECISION - q) * self.opinion + q * altOpinion) / PRECISION
    self.history.append((self.opinion, round_no))


class StubbornAgent (Agent): 
  
  # Stubborn agents simply don't change their minds. 

  def __init__(self, initialOpinion):
    Agent.__init__(initialOpinion)

  def UpdateOpinion(self, anAgent, altOpinion, q, round_no): 
    self.history.append((self.opinion, round_no))


def ReluctantAgent (Agent): 

  # Reluctant agents. 
  
  def __init__(self, initialOpinion, updateRate):
    Agent.__init__(initialOpinion)
    self.tao = updateRate 
     
  def UpdateOpinion(self, anAgent, altOpinion, q, round_no): # TODO
    pass





if __name__ == '__main__': 
  #g = igraph.Graph.Barabasi(20, 3)
  #g = igraph.Graph.Erdos_Renyi(2000, 0.1)
  g = igraph.Graph.Erdos_Renyi(2000, 0.1)

  sim = Simulation(g)
  print sim.TestConvergence()
  #print sim.RunUntilConvergence(dynamicsModel=AsymmetricGossip, 
  #        q=0.5, 
  #        max_rounds=500000)#rounds=1000000)
  sim.Run(dynamicsModel=SymmetricGossip, q=0.5, rounds=100000)
  print sim.TestConvergence()
  print sim.TimeOfConvergence()

  #style = {}
  #igraph.plot(g, "graph.png", **style)
  
