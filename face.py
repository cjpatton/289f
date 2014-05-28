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
      sim.Run(dynamicsModel=consensus.SymmetricGossip, q=0.5, rounds=100000)
    fd.write('%f,%d\n' % (sim.GetConsensus()[0], sim.TimeOfConvergence())) 
    sim.Reset()
  fd.close()


trials = 1000

vs = set()
es = []
fd = open("data/facebook.edges", "r")
for line in map(lambda(l) : l.strip().split(' '), fd.readlines()):
  (u, v) = int(line[0]), int(line[1])
  vs.add(u)
  vs.add(v)
  es.append((u,v))
fd.close()
fella = {}
for (i, u) in enumerate(vs): 
  fella[u] = i
guy = []
for (u, v) in es: 
  guy.append((fella[u], fella[v]))
es = guy
n = len(vs)

g = igraph.Graph()
g.add_vertices(n)
g.add_edges(es)
print n
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
exp("facebook_control.csv", g, control_agents, trials)

