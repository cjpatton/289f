# sim.py - Simulation of asynchronous consensus models.
#
#
import igraph
import random

#
# Asynchronous opnion dynamics models. Nodes of `g` are expected to have 
# an `Agent` attribute. 
#

def SymmetricGossip(g):
  # Choose an edge in `g` at random and have the nodes exchange opinions,
  (u,v) = random.choice(list(g.es)).tuple
  opinion = g.vs[u]['agency'].opinion
  g.vs[u]['agency'].UpdateOpinion(g.vs[v], g.vs[v]['agency'].opinion)
  g.vs[v]['agency'].UpdateOpinion(g.vs[u], opinion)

def AsymmetricGossip(g):
  pass

def Broadcast(g): 
  pass


#
# Simulate opinion dynamics over `g` given a particular mode. Run 
# until convergence, at most `rounds` times. If no agents are 
# provided, standard agents with initial opinion between 0 and 10 
# and q = 0.5 are generated. 
#

class Simulation: 
  
  def __init__(self, g, agents=None, q=0.5):
    self.g = g
    if agents:
      assert len(agents) == len(g.vs)
      selg.g.vs['agency'] = agents
    else:
      self.g.vs['agency'] = [ 
                  Agent(random.uniform(0,10), q) for i in range(len(g.vs)) ]

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
    pass

  def Simulate(self, DynamicsModel=SymmetricGossip, rounds=1000):
    # TODO check for convergence
    
    for i in range(rounds):
      DynamicsModel(self.g)
    
    return [ agent.opinion for agent in self.g.vs['agency'] ]
      


#
# Agents 
#

class Agent:

  # Standard agent type. Constructor accepts an initial opinion
  # and `q` in [0 .. 1], the weight of alternative opinions. 

  def __init__(self, initialOpinion, q):
    self.initialOpinion = self.opinion = initialOpinion
    self.q = q

  def RestoreInitialOpinion(self):
    self.opinion = self.initialOpinion
  
  def SetOpinion(self, opinion):
    self.opinion = opinion

  def UpdateOpinion(self, anAgent, altOpinion): 
    self.opinion = ((1 - self.q) * self.opinion) + (self.q * altOpinion)


class StubbornAgent (Agent): 
  
  # Stubborn agents simply don't change their minds. 

  def __init__(self, initialOpinion, q):
    Agent.__init__(initialOpinion, q)

  def UpdateOpinion(self, anAgent, altOpinion): 
    pass


def ReluctantAgent (Agent): 

  # Reluctant agents. 
  
  def __init__(self, initialOpinion, q, updateRate):
    Agent.__init__(initialOpinion, q)
    self.tao = updateRate 
     
  def UpdateOpinion(self, anAgent, altOpinion): # TODO
    pass





if __name__ == '__main__': 
  g = igraph.Graph.Barabasi(20, 3)


  sim = Simulation(g)
  print sim.Simulate(rounds=100)


  style = {}
  igraph.plot(g, "graph.png", **style)
  
