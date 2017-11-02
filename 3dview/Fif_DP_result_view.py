import matplotlib.pyplot as plt
import numpy as np
import Free_ini_fin_DP as dp
import handle_DP_data as hDP
#import sys
from argparse import ArgumentParser

# plot
fig = plt.figure()

# label
plt.xlabel("input")
plt.ylabel("reference")

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

    argparser.add_argument(nargs='+', action='append', dest='joints', metavar=('joint1', 'joint2'),
                           help='show joints')

    argparser.add_argument('-w', '--write',
                           nargs='?', action='append', dest='write_video', metavar='filepath',
                           help='write figure image')

    argparser.add_argument('-r', '--read',
                           action='store_true', dest='read_DP_data',
                           help='read DP data to shorten calculating time')



    args = argparser.parse_args()

    return args



def view(arg):
    data1 = np.genfromtxt(fname=arg.input_filepath, dtype=float, delimiter=',', skip_header=5)
    data1 = np.delete(data1, [0,1], 1)

    data2 = np.genfromtxt(fname=arg.reference_filepath, dtype=float, delimiter=',', skip_header=5)
    data2 = np.delete(data2, [0,1], 1)

    if data1.shape[1] != data2.shape[1]:
        print("data's length is different")
        return False

    if arg.joints is not None:
        joints = arg.joints[0]
        for joint in joints:
            try:
                tmp = Points[joint]
            except KeyError:
                print '{} is not correct joint name'.format(joint)
                return False

    #data1 = data1.T
    #data2 = data2.T

    # option read DP data
    if arg.read_DP_data:
        tmp_bool, diff_detail = hDP.read_simpleDP_data(arg.input_filepath, arg.reference_filepath)
        if tmp_bool == False:
            return False
    else:
        tmp_bool, diff_detail = dp.FREE_INI_FIN_DP_MATCHING(arg.input_filepath, arg.reference_filepath, joints)
        if tmp_bool == False:
            return False

    for i, joint in enumerate(joints):
        plt.plot(diff_detail[i][0], diff_detail[i][1], label=str(joint))

    try:
        plt.legend()
        plt.show()
        return True
    except AttributeError:
        return True

if __name__ == '__main__':
    if view(parser()):
        print("finished")
    else:
        print("An error was occurred")
