###############################################################################
# sim.py - Simulation of asynchronous consensus models.
#    
#  Chris Patton (chrispatton@gmail.com), May 2014
#
# Suppose we have a graph G = (V, E) and a vector X(0) of length |V| 
# corresponding to an observation of each node. The nodes attempt to
# reach consensus by averaging their observations with others'. A 
# synchronus model of opinion dynamics was first proposed in [DeGroot '74].
# In this model, opinions are exchanged between all pairs of nodes at each 
# round. Under mild assumptions, it can be shown that such a system will 
# reach consensus in finite time, and furthermore, the consensus value and 
# the time it takes to reach consensus, have a closed form deriviation. 
# More realisitic models are more complex, however. 
# 
# This program simulates various asynchronous consensus models over a 
# graph. We provide three commonly studied opinion exchange methods
# [Fagnani '14]: symetric gossip, asymetric gossip, and broadcast. We
# introduce a novel agent behavior model, which is designed to adapt to 
# new opinions slower than normal agents. 
#
# This program is based on the python-igraph library. 
#
###############################################################################

import igraph
import random


############# Consensus models ################################################
# Asynchronous opnion dynamics models. Nodes of `g` are expected to have 
# an `agency` attribute. `q` in [0 .. 1] is the weight of the alternate
# opinion when updating. 
###############################################################################

def SymetricGossip(g, q, round_no, trigger_list):
  # Choose an edge in `g` uniformly and have the nodes exchange opinions,
  (u,v) = g.es[random.randint(0, g.ecount() - 1)].tuple
  u = g.vs[u]['agency']
  v = g.vs[v]['agency']
  opinion = u.opinion
  u.UpdateOpinion(v, v.opinion, q, round_no, trigger_list)
  v.UpdateOpinion(u, opinion, q, round_no, trigger_list)

def AsymetricGossip(g, q, round_no, trigger_list):
  # choose a node from `g` uniformly and have it share its opinion with
  # one of its neighbors, chosen uniformly. 
  u = g.vs[random.randint(0, g.vcount() - 1)]
  if u.degree() > 0:
    v = u.neighbors()[random.randint(0, u.degree() - 1)]['agency']
    u['agency'].UpdateOpinion(v, v.opinion, q, round_no, trigger_list)

def Broadcast(g, q, round_no, trigger_list): 
  # Choose a node from `g` uniformly and update its neighbors' opinions. 
  u = g.vs[random.randint(0, g.vcount() - 1)]
  agency = u['agency']
  for v in u.neighbors(): 
    v['agency'].UpdateOpinion(agency, agency.opinion, q, round_no, trigger_list)
    
  


############# Simulation ######################################################

class Simulation: 
  
  # Simulate opinion dynamics over `g` given a particular mode. Run 
  # until convergence, at most `rounds` times. If no agents are 
  # provided, standard agents with initial opinion between 0 and 10 
  # are generated. Note that the graph `g` need not be fully connected. 
 
  def __init__(self, g, agents=None):
    self.g = g
    if agents:
      assert len(agents) == len(g.vs)
      self.g.vs['agency'] = agents
    else:
      self.g.vs['agency'] = [ 
                  Agent(random.uniform(0,10)) for i in range(len(g.vs)) ]

  def SetOpinionsUnif(self, low, high):
    # Set opinions by selecting a real value uniformly between high and low. 
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

  def Run(self, dynamicsModel=SymetricGossip, q=0.5, rounds=1000):
    # Run simulation for some number of rounds and return the opinion vector. 
    q = SHIFT(q)
    trigger_list = []
    for r in range(rounds):
      dynamicsModel(self.g, q, r, trigger_list)
      tmp = []
      for trigger in trigger_list:
        if trigger(): 
          tmp.append(trigger)
      trigger_list = tmp

    return [ agent.GetOpinion() for agent in self.g.vs['agency'] ]

  def TestConvergence(self, err=0.0001):
    # Test if consenus has been reached. 
    err = SHIFT(err)
    for c in self.g.components():
      W = [ self.g.vs[u]['agency'].opinion for u in c ]
      if (max(W) - min(W)) > err: 
        return False
    return True
  
  def TimeOfConvergence(self, err=0.0001):
    # Compute the number of rounds until convergence. (Note that the 
    # result isn't valid if consensus hasn't been reached.) Look at
    # the transaction histories of the nodes and find the round 
    # number when their opinion converged to consensus. The maximum
    # of these is the number of rounds until convergence. 
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

  def GetConsensus(self):
    # Return a list of consensus scores for each component. (Note 
    # that the value isn't valid if consensus hasn't been reached.) 
    consensus = []
    for c in self.g.components(): 
      consensus.append(g.vs[c[0]]['agency'].GetOpinion())
    return consensus


# The simulator does integer arithmetic under the hood in order to 
# speed things up. `PRECISION` can be adjusted to increase or 
# decrease precision. 

PRECISION = 10 ** 8 
SHIFT = lambda(x) : int(x * PRECISION)
UNSHIFT = lambda(x) : float(x) / PRECISION


############# Agents ##########################################################
# Opinion is typically a real scalar, but can be any type that supports 
# addition, scalar multiplication and division, min(), max(), int(), and 
# float(). 
###############################################################################

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

  def UpdateOpinion(self, agent, altOpinion, q, round_no, trigger_list=None): 
    self.opinion = ((PRECISION - q) * self.opinion + q * altOpinion) / PRECISION
    self.history.append((self.opinion, round_no))


class StubbornAgent (Agent): 
  
  # Stubborn agents simply don't change their minds. 

  def __init__(self, initialOpinion):
    Agent.__init__(initialOpinion)

  def UpdateOpinion(self, agent, altOpinion, q, round_no, trigger_list=None): 
    self.history.append((self.opinion, round_no))


class ReluctantAgent (Agent): 

  # Reluctant agents adapt to new opinions slowly, i.e., in `rate` time
  # steps. When its opinion is updated, it creates a trigger which increments
  # its opinion by a fixed amount at each round until a counter reaches 
  # `rate`. A reluctant agent can be adapting to many opinions at the same 
  # time; to deal with this, the increment is adjusted to adapt to the 
  # opinion that will *eventually* be reached by the last update trigger.
  
  def __init__(self, initialOpinion, rate):
    Agent.__init__(self, initialOpinion)
    self.rate = rate 
    self.next_target = self.opinion
     
  def UpdateOpinion(self, agent, altOpinion, q, round_no, trigger_list):
    trigger_list.append(ReluctantTrigger(self, round_no,
        q * (altOpinion - self.next_target) / (PRECISION * self.rate)))
    self.next_target = ((PRECISION - q) * self.next_target + q * altOpinion) / PRECISION


############# Triggers ########################################################

class BaseTrigger:
  
  # Simulation.Run() processes a list of triggers at each round. If the 
  # trigger returns False when called, it should be removed from the 
  # list.
  
  def __init__(self, agent):
    self.agent = agent

  def __call__(self): 
    return False

class ReluctantTrigger (BaseTrigger):
  
  # Trigger for a reluctant agent. 

  def __init__(self, agent, round_no, inc): 
    BaseTrigger.__init__(self, agent)
    self.round_no = round_no
    self.inc = inc
    self.count = 0

  def __call__(self):
    self.agent.opinion += self.inc
    self.count += 1
    if (self.agent.rate == self.count):
      self.agent.history.append(
        (self.agent.opinion, self.round_no + self.agent.rate))
      return False
    else: 
      return True
    



############# Testing, testing ... ############################################

if __name__ == '__main__': 
  #g = igraph.Graph.Barabasi(20, 3)
  #g = igraph.Graph.Erdos_Renyi(2000, 0.1)

  n = 20; p = 0.3

  # Graph
  g = igraph.Graph.Erdos_Renyi(n, p)
  
  # Agents. 
  agents = [ Agent(1) for i in range(n) ] 
  agents[13] = ReluctantAgent(100, 10)

  sim = Simulation(g, agents)
  
  sim.Run(dynamicsModel=SymetricGossip, q=0.5, rounds=1000)
  if sim.TestConvergence():
    print "Consensus %s reached after %d rounds." % (
        sim.GetConsensus(), sim.TimeOfConvergence())
  else: 
    print "Consensus not reached."
  
  #style = {}
  #igraph.plot(g, "graph.png", **style)
  
