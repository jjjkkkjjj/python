import numpy as np
import sys
import math
import handle_DP_data as hDP
import time

# global
#Limit = 5
# x,y
Limit = [[-1,0], [-1,-1], [0,-1]]
Points = {"head":0, "R_ear":1, "L_ear":2, "sternum":3, "C7":4, "R_rib":5, "L_rib":6, "R_ASIS":7, "L_ASIS":8, "R_PSIS":9, "L_PSIS":10,
          "R_frontshoulder":11, "R_backshoulder":12, "R_in_elbow":13, "R_out_elbow":14, "R_in_wrist":15, "R_out_wrist":16, "R_hand":17,
          "L_frontshoulder":18, "L_backshoulder":19, "L_in_elbow":20, "L_out_elbow":21, "D_UA?":22, "L_in_wrist":23, "L_out_wrist":24,
          "L_hand":25}

class DP:
    def __init__(self):
        self.matching_cost = np.Inf
        self.X_back_track = -np.Inf
        self.Y_back_track = -np.Inf
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
        self.__back_trackX = np.zeros((self.__xtime, self.__ytime), int) * -1
        self.__back_trackY = np.zeros((self.__xtime, self.__ytime), int) * -1
        self.__corr_X = []
        self.__corr_Y = []
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

        for j in range(self.__ytime):
            self.__matching_cost[0][j] = self.__local_cost[0][j]
            self.__back_trackX[0][j] = -1
            self.__back_trackY[0][j] = -1

        for i in range(1, self.__xtime):
            for j in range(self.__ytime):
                tmp_min = np.Inf
                tmp_x = -np.Inf
                tmp_y = -np.Inf
                for k in range(len(Limit)):
                    i_ = i + Limit[k][0]
                    j_ = j + Limit[k][1]
                    if i_ >= 0 and i_ < self.__xtime and j_ >= 0 and j_ < self.__ytime:
                        if tmp_min > self.__matching_cost[i_][j_]:
                            tmp_min = self.__matching_cost[i_][j_]
                            tmp_x = i_
                            tmp_y = j_
                if np.isinf(tmp_min):
                    print("An error was occurred")
                    return False
                self.__matching_cost[i][j] = tmp_min + self.__local_cost[i][j]
                self.__back_trackX[i][j] = tmp_x
                self.__back_trackY[i][j] = tmp_y

        backX = self.__xtime - 1
        backY = np.nanargmin(self.__matching_cost[backX])
        tmp = 0
        while backX > -1 and backY > -1:
            self.__corr_X.append(backX)
            self.__corr_Y.append(backY)
            backX = self.__back_trackX[self.__corr_X[tmp]][self.__corr_Y[tmp]]
            backY = self.__back_trackY[self.__corr_X[tmp]][self.__corr_Y[tmp]]
            tmp += 1

        self.__corr_X.reverse()
        self.__corr_Y.reverse()

        duration = time.time() - start_time
        print("calculated")
        print("{} sec".format(duration))
        return True

    def show_corrPoints(self):
        if not self.__F:
            return False
        for i in range(len(self.__corr_X)):
            print('{},{}'.format(self.__corr_X[i],self.__corr_Y[i]))
        return

    def return_corrPoints(self):
        if not self.__F:
            return False
        return self.__corr_X, self.__corr_Y


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


def FREE_INI_FIN_DP_MATCHING(filepath1, filepath2, joints):
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

    for joint in joints:
        diff_detail.append(simple_DP_Matching(data1[Points[joint]*3:Points[joint]*3+3], data2[Points[joint]*3:Points[joint]*3+3]))# i = 0,1X->0,3,6...

    duration = time.time() - start_time
    print("Calculation time: {} sec".format(duration))

    #print(diff_detail)
    #diff_detail.append(simple_DP_Matching(data1[0:0 + 3], data2[0:0 + 3]))
    #print(diff_detail)
    #simple_DP_Matching(data1[51:51+3], data2[51:51+3])

    #hDP.write_simpleDP_data(diff_detail, filepath1, filepath2, Limit)

    return True, diff_detail

if __name__ == '__main__':
    arg = sys.argv
    if len(arg) > 3:
        print ("argument error:python Simple_DP.py filepath1 filepath2")
    else:
        tmp_bool, tmp_list = FREE_INI_FIN_DP_MATCHING(arg[1], arg[2], arg[3])
        if tmp_bool:
            print("finished")
        else:
            print("An error was occurred")