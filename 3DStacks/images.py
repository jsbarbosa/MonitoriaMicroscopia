import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

N = 20

x = np.arange(0, N)
y = x.copy()

xx, yy = np.meshgrid(x, y)

zz = np.ones_like(xx)*0

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection='3d')

for i in range(15):
    data = np.random.random((N, N))
    ax.plot_surface(xx, yy, zz + i, facecolors = plt.cm.BrBG(data), alpha = 0.5)

ax.set_axis_off()
plt.show()
