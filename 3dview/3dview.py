from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as anm
import matplotlib.pyplot as plt
import numpy as np

import sys

# global
x = np.zeros(1)
y = np.zeros(1)
z = np.zeros(1)
xmin = 99999
xmax = -99999
ymin = 99999
ymax = -99999
zmin = 99999
zmax = -99999
# plot
fig = plt.figure()
ax = Axes3D(fig)
# axis label
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

def update(i):
    if i != 0:
        ax.cla()

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_zlim([zmin, zmax])

    ax.scatter3D(x[i], y[i], z[i])

    plt.title('frame number=' + str(i))

    #plt.axes().set_aspect('equal', 'datalim')


def view_3d(filename):
    data = np.genfromtxt(fname=filename, dtype=float, delimiter=',', skip_header=5)
    data = np.delete(data, [0,1], 1)

    frames = data.shape[0]
    joints = data.shape[1]/3

    global x,y,z,xmax,xmin,ymax,ymin,zmax,zmin

    x = np.zeros((frames, joints))
    y = np.zeros((frames, joints))
    z = np.zeros((frames, joints))

    for i, row in enumerate(data):
        for j, element in enumerate(row):
            if j % 3 == 0:
                x[i][int(j/3)] = element
            elif j % 3 == 1:
                y[i][int(j/3)] = element
            else:
                z[i][int(j/3)] = element

    xmin = np.nanmin(x)
    xmax = np.nanmax(x)
    ymin = np.nanmin(y)
    ymax = np.nanmax(y)
    zmin = np.nanmin(z)
    zmax = np.nanmax(z)


    ani = anm.FuncAnimation(fig, update, interval=20, frames=frames)

    plt.show()
    """
    tmp = filename.split('/')
    Tmp = tmp[len(tmp) - 1].rstrip('.CSV')
    save_filepath = filename.rstrip(tmp[len(tmp) - 1]) + Tmp.rstrip('.csv') + '.MP4'

    ani.save(save_filepath)
    """

    return True


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) != 2:
        print ("argument error:python 3d_view.py filename")
    else:
        if view_3d(arg[1]):
            print("finished")
        else:
            print("An error was occurred")