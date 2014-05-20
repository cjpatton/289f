# sim.py - Simulation of asynchronous consensus models.
#
#
import igraph

#
# Asynchronous opnion dynamics models. Nodes of `g` are expected to have 
# an `Agent` attribute. 
#

def SymmetricGossip(g):
  pass

def AsymmetricGossip(g):
  pass

def Broadcast(g): 
  pass


#
# Simulate opinion dynamics over `g` given a particular mode. Run 
# until convergence, at most `rounds` times. 
#

class Simulation: 
  
  def __init__(self, g):
    self.g = g



  def Simulate(self, DynamicsModel=SymmetricGossip, rounds=1000):
    for i in range(rounds):
      DynamicsModel(self.g)


#
# Agents 
#

class Agent:

  def __init__(self, initialOpinion):
    self.opinion = initialOpinion

  def UpdateOpinion(self, anAgent): 
    self.opinion = (self.opinion + anAgent.opinion) / 2


class StubbornAgent (Agent): 
  
  def __init__(self, initialOpinion):
    Agent.__init__(initialOpinion)

  def UpdateOpinion(self, anAgent): 
    pass


def ReluctantAgent (Agent): # TODO 
  
  def __init__(self, initialOpinion, updateRate):
    Agent.__init__(initialOpinion)
    self.tao = updateRate 
     






if __name__ == '__main__': 
  g = igraph.Graph.Barabasi(100, 3)

  style = {}
  igraph.plot(g, "graph.png", **style)
  
