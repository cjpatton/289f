import consensus
import random
import igraph

def exp(fn, g, agents, trials): 
  fd = open(fn, 'w')
  fd.write('consensus,rounds\n')
  sim = consensus.Simulation(g, agents)
  for trial in range(trials):
    print "did this", trial
    while not sim.TestConvergence(): 
      print "got here"
      sim.Run(dynamicsModel=consensus.SymmetricGossip, q=0.5, rounds=100000)
    fd.write('%f,%d\n' % (sim.GetConsensus()[0], sim.TimeOfConvergence())) 
    sim.Reset()
  fd.close()


trials = 1

n = 4039
g = igraph.Graph()
es = []
fd = open("data/facebook_combined.txt", "r")
for line in map(lambda(l) : l.strip().split(' '), fd.readlines()):
  (u, v) = int(line[0]), int(line[1])
  es.append((u,v))
fd.close()
g.add_vertices(n)
g.add_edges(es)

i = random.randint(0,n-1)

agents = [ consensus.Agent(1) for i in range(n) ]
agents[i] = consensus.ReluctantAgent(100, 50)

unbiased_agents = [ consensus.Agent(1) for i in range(n) ]
unbiased_agents[i] = consensus.UnbiasedReluctantAgent(100, 50)

control_agents = [ consensus.Agent(1) for i in range(n) ]
control_agents[i] = consensus.Agent(100)

print "Facebook"
exp("facebook.csv", g, agents, trials) 
print "Facebook (control)"
exp("erdosrenyi_control.csv", g, control_agents, trials)

