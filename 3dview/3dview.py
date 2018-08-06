from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as anm
import matplotlib.pyplot as plt
import numpy as np
import get_data as gd
#import sys
from argparse import ArgumentParser


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
addx = 0
addy = 0
addz = 0
# plot
fig = plt.figure()
ax = Axes3D(fig)
# axis label
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
# data
HeightData = []
VelocityData = []
HeightMax = {}
VelocityMax = {}

Points = {"head":0, "R_ear":1, "L_ear":2, "sternum":3, "C7":4, "R_rib":5, "L_rib":6, "R_ASIS":7, "L_ASIS":8, "R_PSIS":9, "L_PSIS":10,
          "R_frontshoulder":11, "R_backshoulder":12, "R_in_elbow":13, "R_out_elbow":14, "R_in_wrist":15, "R_out_wrist":16, "R_hand":17,
          "L_frontshoulder":18, "L_backshoulder":19, "L_in_elbow":20, "L_out_elbow":21, "D_UA?":22, "L_in_wrist":23, "L_out_wrist":24,
          "L_hand":25}

Line = [[0,1],[0,2],[1,2],[7,8],[8,10],[9,10],[7,9],[7,11],[8,18],[9,12],[10,19],[11,12],[12,19],[18,19],[18,11],[11,13],
        [12,14],[13,14],[13,15],[14,16],[15,16],[15,17],[16,17],[18,20],[19,21],[20,21],[20,23],[21,24],[23,24],[23,25],[24,25],
        [3,5],[3,6],[5,6]]

def parser():
    usage = 'Usage: python {} input_filepath option'\
            .format(__file__)
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument(dest='input_filepath', type=str,
                           help='you must designate .csv file you want to watch')
    argparser.add_argument('-w', '--write',
                           nargs='?', action='append', dest='write_video', metavar='filepath',
                           help='write video file')

    argparser.add_argument('-sh', '--showheight',
                           nargs='+', action='append', dest='height_joint', metavar=('joint1', 'joint2'),
                           help='show joints height')

    argparser.add_argument('-sv', '--showvelocity', dest='velocity_joint', metavar=('joint1', 'joint2'),
                           nargs='+', action='append',
                           help='show joints velocity')

    args = argparser.parse_args()

    return args

def update(i):
    if i != 0:
        ax.cla()

    ax.set_xlim([xmin, xmax + addx])
    ax.set_ylim([ymin, ymax + addy])
    ax.set_zlim([zmin, zmax + addz])

    for line in Line:
        ax.plot([x[i][line[0]],x[i][line[1]]],[y[i][line[0]],y[i][line[1]]],[z[i][line[0]],z[i][line[1]]],"-",color='blue')
    ax.scatter3D(x[i], y[i], z[i],".",color='blue')
    for j in range(len(x[i])):
        try:
            ax.text(x[i][j],y[i][j],z[i][j], str(j))
        except ValueError:
            continue
    """
    for line in Line:
        ax.plot([x[0][line[0]], x[0][line[1]]], [y[0][line[0]], y[0][line[1]]], [z[0][line[0]], z[0][line[1]]], "-",
                color='blue')
    ax.scatter3D(x[0], y[0], z[0], ".", color='blue')
    l = 8
    ax.text(x[0][l], y[0][l], z[0][l], str(l))
    """


    # show data
    #height
    ax.text2D(0, 0.95, "height", transform=ax.transAxes)
    for j, key in enumerate(HeightData[0].keys()):
        ax.text2D(0, 0.90-j*0.05, key + ":" + str(HeightData[i][key]), transform=ax.transAxes)
        ax.text2D(0.8, 0.90-j*0.05, "max:" + str(HeightMax[key]), transform=ax.transAxes)
    length = len(HeightData[0].keys())+1
    ax.text2D(0, 0.90-(length+1)*0.05, "velocity", transform=ax.transAxes)
    for j, key in enumerate(VelocityData[0].keys()):
        ax.text2D(0, 0.90-(length-j)*0.05, key + ":" + str(VelocityData[i][key]), transform=ax.transAxes)
        ax.text2D(0.8, 0.90-(length-j)*0.05, "max:" + str(VelocityMax[key]), transform=ax.transAxes)

    plt.title('frame number=' + str(i))

    #plt.axes().set_aspect('equal', 'datalim')


def view_3d(arg):
    data = np.genfromtxt(fname=arg.input_filepath, dtype=float, delimiter=',', skip_header=5)
    data = np.delete(data, [0,1], 1)

    frames = data.shape[0]
    joints = data.shape[1]/3

    global x,y,z,xmax,xmin,ymax,ymin,zmax,zmin,addx,addy,addz,\
        HeightData,VelocityData,HeightMax,VelocityMax

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

    #Data = gd.get_data(x,y,z)


    xmin = np.nanmin(x)
    xmax = np.nanmax(x)
    ymin = np.nanmin(y)
    ymax = np.nanmax(y)
    zmin = np.nanmin(z)
    zmax = np.nanmax(z)

    aspectFT = np.array([xmax - xmin, ymax - ymin, zmax - zmin])
    add_tmp = aspectFT.max()
    addx = add_tmp - (xmax - xmin)
    addy = add_tmp - (ymax - ymin)
    addz = add_tmp - (zmax - zmin)

    joints_height = []
    joints_velocity = []
    # option data
    if arg.height_joint is not None:
        joints_height = arg.height_joint[0]
        for joint in joints_height:
            try:
                tmp = Points[joint]
            except KeyError:
                print '{} is not correct joint name'.format(joint)
                return False
    if arg.velocity_joint is not None:
        joints_velocity = arg.velocity_joint[0]
        for joint in joints_velocity:
            try:
                tmp = Points[joint]
            except KeyError:
                print '{} is not correct joint name'.format(joint)
                return False

    HeightData, VelocityData, HeightMax, VelocityMax = gd.get_data(x, y, z, joints_height, joints_velocity)

    ani = anm.FuncAnimation(fig, update, fargs=(), interval=20, frames=frames-1)

    # option video
    if arg.write_video is not None:
        if arg.write_video[0] is None:
            tmp = arg.input_filepath.split('/')
            Tmp = tmp[len(tmp) - 1].rstrip('.CSV')
            save_filepath = arg.input_filepath.rstrip(tmp[len(tmp) - 1]) + Tmp.rstrip('.csv') + '.MP4'
        else:
            save_filepath = arg.write_video[0]
        ani.save(save_filepath)

    """
    if len(option) - 2 > 0:
        option_num = len(option) - 2
        for i in range(option_num):
            index_tmp = len(option) - 1 - i
            if option[index_tmp] == '--write_video':
                tmp = filename.split('/')
                Tmp = tmp[len(tmp) - 1].rstrip('.CSV')
                save_filepath = filename.rstrip(tmp[len(tmp) - 1]) + Tmp.rstrip('.csv') + '.MP4'

                ani.save(save_filepath)

            else:
                print("option error!: " + option[index_tmp] + " was incrrect option\n")
                return False
    """
    try:
        plt.show()
        return True
    except AttributeError:
        return True

if __name__ == '__main__':
    if view_3d(parser()):
        print("finished")
    else:
        print("An error was occurred")

    """
    arg = sys.argv
    if len(arg) < 2:
        print ("argument error:python 3d_view.py filename --write_video")
    else:
        if view_3d(arg[1], arg):
            print("finished")
        else:
            print("An error was occurred")
    """
