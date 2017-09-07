from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as anm
import matplotlib.pyplot as plt
import numpy as np

import sys

# global
x = []
y = []
z = []
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

    ax.scatter3D(x[i], y[i], z[i])

    plt.title('frame number=' + str(i))

    #plt.axes().set_aspect('equal', 'datalim')


def view_3d(filename):
    data = np.genfromtxt(fname=filename, dtype=float, delimiter=',', skip_header=5)
    data = np.delete(data, [0,1], 1)

    frames = data.shape[0]

    for i, row in enumerate(data):
        count = 0
        tmp = 0
        x.append([])
        y.append([])
        z.append([])
        while count < len(row):
            if row[count] == row[count] or row[count + 1] == row[count + 1] or row[count + 2] == row[count + 2]:
                x[i].append(row[count])
                y[i].append(row[count + 1])
                z[i].append(row[count + 2])


            tmp += 1
            count += 3
    npx = np.array(x)
    npy = np.array(y)
    npz = np.array(z)

    xmin = np.array(npx.min()).min()
    xmax = np.array(npx.max()).max()
    ymin = np.array(npy.min()).min()
    ymax = np.array(npy.max()).max()
    zmin = np.array(npz.min()).min()
    zmax = np.array(npz.max()).max()

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_zlim([zmin, zmax])


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