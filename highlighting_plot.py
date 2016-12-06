import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0,3,.001)
y = []
"""
x1 = np.arange(-10,10,.001)
y1 = x1
"""

for i in range(len(x)):
    y.append(-x[i]**2+9)
    
plt.plot(x,y)

#plt.fill_between(x, y1, where=(x >= 0) & (x <= 10), facecolor='r')

#plt.plot([0,5],[25,0],color='k',marker='o')

#plt.fill_between(x[200:800],y[200:800], facecolor='r')



Y = []
m = (y[1000]-y[0])/(x[1000]-x[0])
for i in range(len(x)):
    Y.append(m*(x[i] - x[0])+y[0])
    
plt.plot(x[0:1000],Y[0:1000])

plt.fill_between(x[0:1000],y[0:1000], facecolor='r')
plt.fill_between(x[0:1000],Y[0:1000], facecolor='b')