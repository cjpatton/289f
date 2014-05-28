# hist.py - Making plots for presentation.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import sys


def readcsv(fn): 

  table = {}
  fd = open(fn, 'r')

  headers = fd.readline().strip().split(',')
  for header in headers:
    table[header] = []

  # Populate the table.
  line_no = 1
  for line in map(lambda l: l.strip().split(','), fd.readlines()):
    if line == ['']: # Skip blank lines
      continue

    elif len(line) != len(headers): # Malformed line
      raise Exception("malformed row in CSV file (%d)" % line_no)
    
    for (col, val) in zip(headers, line):
      table[col].append(val)

  fd.close()
  return table



# "Parse" commandline arguments
data = readcsv(sys.argv[1])
col =          sys.argv[2]
ymax =   float(sys.argv[3])

xlabel = "Time of convergence (rounds)" if col == 'rounds' else 'Consensus'
ylabel = "Frequency"
N = 50


# FIXME 
data['consensus'] = map(lambda(x) : float(x), data['consensus'])
data['rounds'] = map(lambda(x) : int(x), data['rounds'])

fig = plt.figure(figsize=(5,4))
ax = fig.add_subplot(111)

# the histogram of the data
n, bins, patches = ax.hist(data[col], N, facecolor='grey', alpha=0.75)
bincenters = 0.5*(bins[1:]+bins[:-1])
ax.set_xlabel(xlabel)
ax.set_ylabel(ylabel)
ax.set_xlim(min(data[col]), max(data[col]))
ax.set_ylim(0, ymax)
ax.grid(False)

plt.savefig("hist.png")


