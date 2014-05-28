import consensus
import igraph

def exp(fn, g, agents, trials): 
  fd = open(fn, 'w')
  fd.write('consensus,rounds\n')
  sim = consensus.Simulation(g, agents)
  for trial in range(trials):
    while not sim.TestConvergence(): 
      sim.Run(dynamicsModel=consensus.SymmetricGossip, q=0.5, rounds=5000)
    fd.write('%f,%d\n' % (sim.GetConsensus()[0], sim.TimeOfConvergence())) 
    sim.Reset()
  fd.close()


n = 100
p = 0.048
k = 3
trials = 10000

agents = [ consensus.Agent(1) for i in range(n) ]
agents[0] = consensus.ReluctantAgent(100, 50)

unbiased_agents = [ consensus.Agent(1) for i in range(n) ]
unbiased_agents[0] = consensus.UnbiasedReluctantAgent(100, 50)


control_agents = [ consensus.Agent(1) for i in range(n) ]
control_agents[0] = consensus.Agent(100)

g = igraph.Graph.Barabasi(n, k)
print "Barabasi-Ablert"
exp("barabasi.csv", g, agents, trials) 
print "Barabasi-Ablert (unbiased)"
exp("barabasi_unbiased.csv", g, unbiased_agents, trials) 
print "Barabasi-Ablert (control)"
exp("barabasi_control.csv", g, control_agents, 10)





