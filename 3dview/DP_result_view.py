from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as anm
import matplotlib.pyplot as plt
import numpy as np
import Simple_DP as dp
import handle_DP_data as hDP
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
diff_detail = []
color = []

Points = {"head":0, "R_ear":1, "L_ear":2, "sternum":3, "C7":4, "R_rib":5, "L_rib":6, "R_ASIS":7, "L_ASIS":8, "R_PSIS":9, "L_PSIS":10,
          "R_frontshoulder":11, "R_backshoulder":12, "R_in_elbow":13, "R_out_elbow":14, "R_in_wrist":15, "R_out_wrist":16, "R_hand":17,
          "L_frontshoulder":18, "L_backshoulder":19, "L_in_elbow":20, "L_out_elbow":21, "D_UA?":22, "L_in_wrist":23, "L_out_wrist":24,
          "L_hand":25}

Line = [[0,1],[0,2],[1,2],[7,8],[8,10],[9,10],[7,9],[7,11],[8,18],[9,12],[10,19],[11,12],[12,19],[18,19],[18,11],[11,13],
        [12,14],[13,14],[13,15],[14,16],[15,16],[15,17],[16,17],[18,20],[19,21],[20,21],[20,23],[21,24],[23,24],[23,25],[24,25],
        [3,5],[3,6],[5,6]]


def parser():
    usage = 'Usage: python {} input_filepath reference_filepath [option]'\
            .format(__file__)
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument(dest='input_filepath', type=str,
                           help='you must designate .csv file which is begginer')
    argparser.add_argument(dest='reference_filepath', type=str,
                           help='you must designate .csv file which is expert')
    argparser.add_argument('-w', '--write',
                           nargs='?', action='append', dest='write_video', metavar='filepath',
                           help='write video file')

    argparser.add_argument('-r', '--read',
                           action='store_true', dest='read_DP_data',
                           help='read DP data to shorten calculating time')


    args = argparser.parse_args()

    return args

def update(i):
    if i != 0:
        ax.cla()

    ax.set_xlim([xmin, xmax + addx])
    ax.set_ylim([ymin, ymax + addy])
    ax.set_zlim([zmin, zmax + addz])

    #for j in range(len(x[i])):
    #    ax.scatter3D(x[i][j], y[i][j], z[i][j])
    for line in Line:
        ax.plot([x[i][line[0]],x[i][line[1]]],[y[i][line[0]],y[i][line[1]]],[z[i][line[0]],z[i][line[1]]],"-",color='black')
    ax.scatter3D(x[i], y[i], z[i], c=color[i])

    plt.title('frame number=' + str(i))

    #plt.axes().set_aspect('equal', 'datalim')


def view_3d(arg):
    data1 = np.genfromtxt(fname=arg.input_filepath, dtype=float, delimiter=',', skip_header=5)
    data1 = np.delete(data1, [0,1], 1)

    data2 = np.genfromtxt(fname=arg.reference_filepath, dtype=float, delimiter=',', skip_header=5)
    data2 = np.delete(data2, [0,1], 1)

    if data1.shape[1] != data2.shape[1]:
        print("data's length is different")
        return False


    global x, y, z, xmax, xmin, ymax, ymin, zmax, zmin, addx, addy, addz, \
        diff_detail, color

    frames = data1.shape[0]
    joints = data1.shape[1]/3

    x = np.zeros((frames, joints))
    y = np.zeros((frames, joints))
    z = np.zeros((frames, joints))


    for i, row in enumerate(data1):
        for j, element in enumerate(row):
            if j % 3 == 0:
                x[i][int(j/3)] = element
            elif j % 3 == 1:
                y[i][int(j/3)] = element
            else:
                z[i][int(j/3)] = element

    #data1 = data1.T
    #data2 = data2.T

    # option read DP data
    if arg.read_DP_data:
        tmp_bool, diff_detail, limit_num = hDP.read_simpleDP_data(arg.input_filepath, arg.reference_filepath)
        if tmp_bool == False:
            return False
    else:
        tmp_bool, diff_detail, limit_num = dp.SIMPLE_DP_MATCHING(arg.input_filepath, arg.reference_filepath)
        if tmp_bool == False:
            return False

    # diff_detail[joint][time]

    # color[time][joint][rgb]
    # delay -> blue, fast -> red
    color = [[[0.0, 0.0, 0.0] for j in range(joints)] for i in range(frames)]
    tmp_count_zero = [0 for i in range(joints)]
    for i in range(1, frames):
        for j in range(joints):
            if diff_detail[j][i] == -1:
                color[i][j] = [0.0,0.0,0.0]
            else:
                tmp_diff = diff_detail[j][i] - diff_detail[j][i-1]
                if tmp_diff == 1:
                    color[i][j] = [0.0,0.0,0.0]
                    tmp_count_zero[j] = 0
                # delay
                elif tmp_diff == 0:
                    if tmp_count_zero[j] != limit_num:
                        tmp_count_zero[j] += 1
                    color[i][j] = [0.0,0.0,tmp_count_zero[j]*1.0/limit_num]
                    #print('{},{},{}'.format(tmp_count_zero[j],limit_num,float(tmp_count_zero[j]/limit_num)))
                # fast
                else:
                    color[i][j] = [(tmp_diff-1)*1.0/limit_num,0.0,0.0]
                    tmp_count_zero[j] = 0
                    #print('{},{},{}'.format((tmp_diff-1),limit_num,float((tmp_diff-1)/limit_num)))


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
