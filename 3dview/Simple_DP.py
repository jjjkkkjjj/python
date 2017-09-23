import numpy as np
import sys
import math

def local_cost_calculate(x, y, dim):
    tmp = 0
    for i in range(dim):
        tmp += (x[i] - y[i]) * (x[i] - y[i])
    return math.sqrt(tmp)

def simple_DP_Matching(x, y):# comparision with x and y # x,y must be numpy
    #calculate cost
    if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
        print("x,y must be numpy.ndarray.")
        return False
    dim = x.shape[0]
    if dim != y.shape[0]:
        print("x,y must have same dimension")

    x_time = x.shape[1]
    y_time = y.shape[1]

    local_cost = np.zeros(x_time, y_time)

    for i in range(x_time):
        for j in range(y_time):
            local_cost[i][j] = local_cost_calculate(x[x_time], y[y_time], dim)

    matching_cost = np.zeros(x_time, y_time)#ここから


def SIMPLE_DP_MATCHING(filepath1, filepath2):
    data1 = np.genfromtxt(fname=filepath1, dtype=float, delimiter=',', skip_header=5)
    data1 = np.delete(data1, [0, 1], 1)


    data2 = np.genfromtxt(fname=filepath2, dtype=float, delimiter=',', skip_header=5)
    data2 = np.delete(data2, [0, 1], 1)

    simple_DP_Matching(data1, data2)

    return True

if __name__ == '__main__':
    arg = sys.argv
    if len(arg) == 3:
        print ("argument error:python Simple_DP.py filepath1 filepath2")
    else:
        if SIMPLE_DP_MATCHING(arg[1], arg[2]):
            print("finished")
        else:
            print("An error was occurred")