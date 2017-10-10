import numpy as np
import sys
import math
import handle_DP_data as hDP
import time

# global
Limit = 5

class DP:
    def __init__(self):
        self.matching_cost = np.Inf
        self.X_back_track = -1 # no need because limitation is y only
        self.Y_back_track = -1
    def set(self, M_COST, X_BT, Y_BT):
        self.matching_cost = M_COST
        self.X_back_track = X_BT
        self.Y_back_track = Y_BT

class SyncDP:
    def __init__(self, x, y, dim):
        self.__x = x
        #self.x = x[~np.isnan(x).any(axis=1)] # extract only real number
        self.__y = y
        self.__dim = dim
        self.__xtime = x.shape[0]
        self.__ytime = y.shape[0]
        self.__local_cost = np.zeros((self.__xtime, self.__ytime))
        self.__matching_cost = np.ones((self.__xtime, self.__ytime)) * np.Inf
        self.__back_trackX = np.zeros((self.__xtime, self.__ytime), int)
        self.__back_trackY = np.zeros((self.__xtime, self.__ytime), int)
        # limit_inclimen
        self.__limitationY = [i for i in range(-Limit, 1, 1)]
        self.__corr_time = [i for i in range(self.__xtime)]
        self.__F = True

    def calculate(self):
        print("calculating now...")
        start_time = time.time()

        for i in range(self.__xtime):
            for j in range(self.__ytime):
                self.__local_cost[i][j] = local_cost_calculate(self.__x[i], self.__y[j], self.__dim)
                if np.isnan(self.__local_cost[i][j]):
                    self.__F = False
                    duration = time.time() - start_time
                    print("The data include missing value")
                    return False

        self.__matching_cost[0][0] = 0

        for i in range(1, self.__xtime):
            for j in range(self.__ytime):
                tmp = np.ones(len(self.__limitationY)) * np.nan
                for k, value in enumerate(self.__limitationY):
                    if j + value >= 0:
                            tmp[k] = self.__matching_cost[i - 1][j + value]

                self.__matching_cost[i][j] = np.nanmin(tmp) + self.__local_cost[i][j]
                self.__back_trackX[i][j] = i - 1
                self.__back_trackY[i][j] = j + self.__limitationY[np.nanargmin(tmp)]

        self.__corr_time[self.__xtime - 1] = self.__ytime - 1
        for i in range(self.__xtime - 2, -1, -1):
            self.__corr_time[i] = self.__back_trackY[i][self.__corr_time[i + 1]]

        duration = time.time() - start_time
        print("calculated")
        print("{} sec".format(duration))
        return True

    def show_corrPoints(self):
        if not self.__F:
            return False
        for i in range(len(self.__corr_time)):
            print('{},{}'.format(i,self.__corr_time[i]))
        return

    def return_corrPoints(self):
        if not self.__F:
            return False
        return self.__corr_time

    def return_length_limitationY(self):
        return len(self.__limitationY)

def local_cost_calculate(x, y, dim):# L2 norm
    tmp = 0
    for i in range(dim):
        tmp += (x[i] - y[i]) * (x[i] - y[i])
    return math.sqrt(tmp)

def simple_DP_Matching(x, y):# comparision with x and y # x,y must be numpy and their size must be 3 (x[0:3])
    #calculate cost
    if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
        print("x,y must be numpy.ndarray.")
        return False
    dim = x.shape[0]

    if dim != y.shape[0]:
        print("x,y must have same dimension")

    x_time = x.shape[1]
    y_time = y.shape[1]

    local_cost = np.zeros((x_time, y_time))
    # x[dim][time] - > x[time][dim]
    x = x.T
    y = y.T

    DP = SyncDP(x, y, dim)
    if not DP.calculate():
        return [-1 for i in range(x_time)]
    #DP.show_corrPoints()
    return DP.return_corrPoints()


def SIMPLE_DP_MATCHING(filepath1, filepath2):
    data1 = np.genfromtxt(fname=filepath1, dtype=float, delimiter=',', skip_header=5)
    data1 = np.delete(data1, [0, 1], 1)


    data2 = np.genfromtxt(fname=filepath2, dtype=float, delimiter=',', skip_header=5)
    data2 = np.delete(data2, [0, 1], 1)

    diff_detail = []

    if data1.shape[1] != data2.shape[1]:
        print("data's length is different")
        return False, diff_detail, Limit


    data1 = data1.T
    data2 = data2.T

    start_time = time.time()
    for i in range(0, data1.shape[0], 3):
        diff_detail.append(simple_DP_Matching(data1[i:i+3], data2[i:i+3]))# i = 0,1X->0,3,6...

    duration = time.time() - start_time
    print("Calculation time: {} sec".format(duration))

    #print(diff_detail)
    #diff_detail.append(simple_DP_Matching(data1[0:0 + 3], data2[0:0 + 3]))
    #print(diff_detail)
    #simple_DP_Matching(data1[12:12+3], data2[12:12+3])

    hDP.write_simpleDP_data(diff_detail, filepath1, filepath2, Limit)

    return True, diff_detail, Limit

if __name__ == '__main__':
    arg = sys.argv
    if len(arg) != 3:
        print ("argument error:python Simple_DP.py filepath1 filepath2")
    else:
        tmp_bool, tmp_list, tmp_limit = SIMPLE_DP_MATCHING(arg[1], arg[2])
        if tmp_bool:
            print("finished")
        else:
            print("An error was occurred")