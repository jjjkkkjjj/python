import sys, os, random, re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from c3d import Reader

from scipy import interpolate
import math
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from leftdock import LeftDockWidget
from subwindow import *
import optimal_selector

class Data:
    def __init__(self):
        self.configurePath = "./__config__/configure.conf"

        self.now_select = -1
        self.frame = 0

        self.Points = ["head", "R_ear", "L_ear", "sternum", "C7", "R_rib", "L_rib", "R_ASIS", "L_ASIS", "R_PSIS",
                       "L_PSIS",
                       "R_frontshoulder", "R_backshoulder", "R_in_elbow", "R_out_elbow", "R_in_wrist", "R_out_wrist",
                       "R_hand",
                       "L_frontshoulder", "L_backshoulder", "L_in_elbow", "L_out_elbow", "D_UA?", "L_in_wrist",
                       "L_out_wrist",
                       "L_hand"]
        self.Line = [[0, 1], [0, 2], [1, 2], [7, 8], [8, 10], [9, 10], [7, 9], [7, 11], [8, 18], [9, 12], [10, 19],
                     [11, 12], [12, 19], [18, 19], [18, 11], [11, 13],
                     [12, 14], [13, 14], [13, 15], [14, 16], [15, 16], [15, 17], [16, 17], [18, 20], [19, 21], [20, 21],
                     [20, 23], [21, 24], [23, 24], [23, 25], [24, 25],
                     [3, 5], [3, 6], [5, 6]]

        # configure
        self.fps = 500
        self.units = "mm"
        self.Threshold_optimal = 50  # mm
        self.StandardJoint_autolabeling = "head"
        self.DefaultTrcPath_autolabeling = "./IMAMURA01.trc"
        self.StandardFrame_autolabeling = -1
        #self.StandardFrame_autolabeling = 218

        self.lastopenedpath = "./"
        self.lastsavedpath = "./"

        if not os.path.isdir("__config__"):
            os.mkdir("__config__")
            with open(self.configurePath, "w") as f:
                return

        with open(self.configurePath, "r") as f:
            lines = f.readlines()
            for line in lines:
                tmp = line.split("\t")
                method = tmp[0]
                value = tmp[1]
                typeOfValue = tmp[2]
                #print "self.{0} = {2}({1})".format(method, value, typeOfValue)
                exec ("self.{0} = {2}(\"{1}\")".format(method, value, typeOfValue))

        pass

    def read_from_csv(self, path):
        data = np.genfromtxt(fname=path, dtype=float, delimiter=',')
        data = np.delete(data, [0], 1)

        self.frame_max = data.shape[0]
        self.joints = data.shape[1] / 3

        self.x = np.zeros((self.frame_max, self.joints))
        self.y = np.zeros((self.frame_max, self.joints))
        self.z = np.zeros((self.frame_max, self.joints))

        self.xnew = np.zeros((self.frame_max, len(self.Points)))
        self.xnew[:, :] = np.nan
        self.ynew = self.xnew.copy()
        self.znew = self.xnew.copy()

        self.xopt = self.x.copy()
        self.xopt[:, :] = np.nan
        self.yopt = self.xopt.copy()
        self.zopt = self.xopt.copy()

        self.label = [["No Label" for j in range(self.joints)] for i in range(self.frame_max)]

        for i, row in enumerate(data):
            for j, element in enumerate(row):
                if j % 3 == 0:
                    self.x[i][int(j / 3)] = element
                elif j % 3 == 1:
                    self.y[i][int(j / 3)] = element
                else:
                    self.z[i][int(j / 3)] = element

        # bone between joints [time][num]

        self.bone1 = [[] for i in range(self.frame_max)]
        self.bone2 = [[] for i in range(self.frame_max)]

        #self.x[self.x == 0.0] = np.nan
        #self.y[self.y == 0.0] = np.nan
        #self.z[self.z == 0.0] = np.nan

        #self.__optimal_select(self.x, self.y, self.z)

    def read_from_c3d(self, path, sep=',', end='\n'):
        input = open(path, 'rb')

        if not os.path.isdir("__cache_csv__"):
            os.mkdir("__cache_csv__")
        output = open("__cache_csv__/tmp.csv", 'w')
        output.close()
        output = open("__cache_csv__/tmp.csv", 'a')
        for frame_no, points, analog in Reader(input).read_frames():
            line = str(frame_no + 1) + sep
            fields = [frame_no]
            for x, y, z, err, tmp in points:
                fields.append(str(x))
                fields.append(str(y))
                fields.append(str(z))
                line += str(x) + sep + str(y) + sep + str(z) + sep
            line = line[:-1] + end
            output.write(line)
        input.close()
        output.close()
        self.read_from_csv("./__cache_csv__/tmp.csv")

    def setLabel(self, var, untilnan=True, auto=True):
        newLabel = var["label"]
        labelIndex = self.Points.index(newLabel)


        if untilnan:
            init = var["init"]
            fin = var["fin"] + 1
            method = var["interpolation"]

            if auto:
                X = self.xopt[init:fin, self.now_select].copy()
                Y = self.yopt[init:fin, self.now_select].copy()
                Z = self.zopt[init:fin, self.now_select].copy()
            else:
                X = self.x[init:fin, self.now_select].copy()
                Y = self.y[init:fin, self.now_select].copy()
                Z = self.z[init:fin, self.now_select].copy()

            zerotimes = np.where(((X == 0.0) & (Y == 0.0) & (Z == 0.0)))

            #self.x[zerotimes, self.now_select] = np.nan
            #self.y[zerotimes, self.now_select] = np.nan
            #self.z[zerotimes, self.now_select] = np.nan
            X[zerotimes] = np.nan
            Y[zerotimes] = np.nan
            Z[zerotimes] = np.nan

            """
            # eliminate outlier
            # the size of diff is small for one to self.x
            diffx = np.diff(self.x[init:fin, self.now_select], n=1)
            diffy = np.diff(self.y[init:fin, self.now_select], n=1)
            diffz = np.diff(self.z[init:fin, self.now_select], n=1)

            outlierIndex = np.where((diffx**2 + diffy**2 + diffz**2) > self.searchRange)[0]
            print(outlierIndex)
            self.x[outlierIndex, self.now_select] = np.nan
            self.y[outlierIndex, self.now_select] = np.nan
            self.z[outlierIndex, self.now_select] = np.nan
            """

            if method == "Linear":
                time = np.where(~np.isnan(self.x[init:fin, self.now_select]))[0]

                #linearX = interpolate.interp1d(time, self.x[init:fin, self.now_select][time], fill_value='extrapolate')
                #linearY = interpolate.interp1d(time, self.y[init:fin, self.now_select][time], fill_value='extrapolate')
                #linearZ = interpolate.interp1d(time, self.z[init:fin, self.now_select][time], fill_value='extrapolate')
                linearX = interpolate.interp1d(time, X[time], fill_value='extrapolate')
                linearY = interpolate.interp1d(time, Y[time], fill_value='extrapolate')
                linearZ = interpolate.interp1d(time, Z[time], fill_value='extrapolate')

                time = [i for i in range(fin - init)]

                self.xnew[init:fin, labelIndex] = linearX(time)
                self.ynew[init:fin, labelIndex] = linearY(time)
                self.znew[init:fin, labelIndex] = linearZ(time)

                #for i in range(init, fin + 1):
                #    self.label[i][labelIndex] = newLabel


            elif method == "Spline":
                pass
                """
                time = np.where(~np.isnan(self.x[init:fin, self.now_select]))[0]

                splineX = interpolate.splrep(time, self.x[time])
                splineY = interpolate.splrep(time, self.y[time])
                splineZ = interpolate.splrep(time, self.z[time])

                time = [i for i in range(fin - init)]

                self.x[init:fin, self.now_select] = splineX[time]
                self.y[init:fin, self.now_select] = splineY[time]
                self.z[init:fin, self.now_select] = splineZ[time]
                """
            else:
                pass

        else:
            if auto:
                self.xnew[self.frame, labelIndex] = self.xopt[self.frame, self.now_select]
                self.ynew[self.frame, labelIndex] = self.yopt[self.frame, self.now_select]
                self.znew[self.frame, labelIndex] = self.zopt[self.frame, self.now_select]
            else:
                self.xnew[self.frame, labelIndex] = self.x[self.frame, self.now_select]
                self.ynew[self.frame, labelIndex] = self.y[self.frame, self.now_select]
                self.znew[self.frame, labelIndex] = self.z[self.frame, self.now_select]
            #self.label[self.frame][labelIndex] = newLabel

        self.setbone()

        """
        if untilnan:
            zerotimes_ori = np.where(self.x[:, self.now_select] == 0.0)[0]
            if zerotimes_ori.shape[0] == 0:
                # all
                for i in range(self.frame_max):
                    self.label[i][self.now_select] = newLabel
                return

            zerotimes = zerotimes_ori - self.frame

            arg = 0
            if np.sum(zerotimes<0) > 0:
                arg = np.argmax(zerotimes_ori[zerotimes<0])
                arg = zerotimes_ori[arg] + 1
            for i in range(arg, self.frame):
                self.label[i][self.now_select] = newLabel

            arg = self.frame_max
            if np.sum(zerotimes>0) > 0:
                arg = np.argmin(zerotimes_ori[zerotimes>0])
                arg = zerotimes_ori[arg]
            for i in range(self.frame, arg):
                self.label[i][self.now_select] = newLabel
        else:
            self.xnew[self.frame, labelIndex] = self.x[self.frame, self.now_select]
            self.ynew[self.frame, labelIndex] = self.y[self.frame, self.now_select]
            self.znew[self.frame, labelIndex] = self.z[self.frame, self.now_select]
            self.label[self.frame][labelIndex] = newLabel

        #print list(map(list, zip(*self.label)))[now_select]
        return
        """

    def deleteLabel(self):
        self.xnew[:, self.now_select] = np.nan
        self.ynew[:, self.now_select] = np.nan
        self.znew[:, self.now_select] = np.nan

    def setbone(self):
        """
        # progress bar?
        Check = [[[0, 1], [0, 2]],
                 [[1, 2]],
                 [],
                 [[3, 5], [3, 6]],
                 [],
                 [[5, 6]],
                 [[7, 8], [7, 9], [7, 11]],
                 [[8, 10], [8, 18]],
                 [[9, 12]],
                 [[10, 19]],
                 [[11, 12], [11, 13]],
                 [[12, 19], [12, 14]],
                 [[13, 14], [13, 15]],
                 [[14, 16]],
                 [[15, 16], [15, 17]],
                 [[16, 17]],
                 [[18, 20]],
                 [[19, 21]],
                 [[20, 21], [20, 23]],
                 [[21, 24]],
                 [],
                 [[23, 24], [23, 25]],
                 [[24, 25]]]


        self.bone1 = [[] for i in range(self.frame_max)]
        self.bone2 = [[] for i in range(self.frame_max)]
        for t in range(self.frame_max):
            for joint_index, label in enumerate(self.label[t]):
                if label == "No Label" or len(Check[joint_index]) == 0:
                    continue
                else:
                    for check in Check[joint_index]:
                        # all we have to do is check only check[1]
                        try:
                            arg = self.label[t].index(self.Points[check[1]])
                            self.bone1[t].append(
                                [self.x[t, joint_index], self.y[t, joint_index], self.z[t, joint_index]])
                            self.bone2[t].append([self.x[t, arg], self.y[t, arg], self.z[t, arg]])
                        except ValueError:
                            continue
        """
        self.bone1 = [[] for i in range(self.frame_max)]
        self.bone2 = [[] for i in range(self.frame_max)]
        for t in range(self.frame_max):
            for line in self.Line:
                if np.isnan(self.xnew[t, line[0]]) or np.isnan(self.xnew[t, line[1]]):
                    continue
                else:
                    self.bone1[t].append([self.xnew[t, line[0]], self.ynew[t, line[0]], self.znew[t, line[0]]])
                    self.bone2[t].append([self.xnew[t, line[1]], self.ynew[t, line[1]], self.znew[t, line[1]]])

    # select optimal data as soon as possible
    """
    def optimal_select(self, method, jointID, startFrame, label):
        tmp_index_num = [np.sum(self.x[i][self.x[i] != 0]) for i in range(self.frame_max)]


        # using extrapolate or DP
        if method == 'extrapolate':
            print(optimal_selector.extrapolate_(jointID, startFrame, self.x, self.y, self.z, self.searchRange))
        elif method == 'DP':
            optimal_selector.DP()
        else:
            optimal_selector.extrapolate()
    """

    def optimal_select(self):
        xtmp, ytmp, ztmp = self.x.copy(), self.y.copy(), self.z.copy()


        # 0 -> time 1 -> joint id
        nanIndex = np.where((self.x == 0.0) & (self.y == 0.0) & (self.z == 0))
        #print nanIndex

        completeJointIdlists = []
        nanJointIdlists = []
        # nanTimelists[joint id] -> nan time list
        nanTimelists = []
        for i in range(self.x.shape[1]):
            if np.sum(nanIndex[1] == i) == 0:
                completeJointIdlists.append(i)
                continue
            else:
                nanJointIdlists.append(i)
                nanTimelists.append(nanIndex[0][nanIndex[1] == i])
                #print nanTimelists[i]

        nanJointIdlists = np.array(nanJointIdlists)

        for nanJointId, nanTimes in zip(nanJointIdlists, nanTimelists):
            #if np.where((nanTimes == 0) | (nanTimes == 1) | (nanTimes == 2)).shape[0] > 0:
            #print (nanTimes)
            if np.where(nanTimes == 0)[0] > 0:
                continue

            nowTime = nanTimes[0]
            while nowTime < self.frame_max - 1:

                Dtmp = (self.x[nowTime, completeJointIdlists] - xtmp[nowTime - 1, nanJointId]) ** 2 \
                       + (self.y[nowTime, completeJointIdlists] - ytmp[nowTime - 1, nanJointId]) ** 2 \
                       + (self.z[nowTime, completeJointIdlists] - ztmp[nowTime - 1, nanJointId]) ** 2

                nearestDistance = math.sqrt(np.min(Dtmp))
                nearestJointId = completeJointIdlists[np.argmin(Dtmp)]

                for time in range(nowTime + 1, self.frame_max):
                    """
                    if nanJointIdlists.size == 0:
                        continue
                    
                    Dtmp = np.sqrt((self.x[time, nanJointIdlists] - self.x[time, nearestJointId]) ** 2 \
                                   + (self.y[time, nanJointIdlists] - self.y[time, nearestJointId]) ** 2 \
                                   + (self.z[time, nanJointIdlists] - self.z[time, nearestJointId]) ** 2)

                    candIndex = nanJointIdlists[np.argmin(Dtmp)]
                    """
                    # looking for previous time which has no nan
                    # extract indices with nan
                    searchJointIdlists = nanJointIdlists[np.where((self.x[time - 1, nanJointIdlists] == 0.0)
                                                                & (self.y[time - 1, nanJointIdlists] == 0.0)
                                                                & (self.z[time - 1, nanJointIdlists] == 0.0))[0]]

                    if searchJointIdlists.size == 0:
                        continue

                    Dtmp = np.sqrt((self.x[time, searchJointIdlists] - self.x[time, nearestJointId]) ** 2 \
                                    + (self.y[time, searchJointIdlists] - self.y[time, nearestJointId]) ** 2 \
                                    + (self.z[time, searchJointIdlists] - self.z[time, nearestJointId]) ** 2)
                                    
                    candIndex = searchJointIdlists[np.argmin(Dtmp)]
                    candMin = np.min(Dtmp)

                    if (nearestDistance - self.Threshold_optimal < candMin and candMin < nearestDistance + self.Threshold_optimal):
                        #XTMP, YTMP, ZTMP = xtmp[time:, candIndex].copy(), ytmp[time:, candIndex].copy(), ztmp[time:, candIndex].copy()

                        #xtmp[time:, candIndex], ytmp[time:, candIndex], ztmp[time:, candIndex] =\
                        #    xtmp[time:, nanJointId].copy(), ytmp[time:, nanJointId].copy(), ztmp[time:, nanJointId].copy()

                        xtmp[time:, nanJointId], ytmp[time:, nanJointId], ztmp[time:, nanJointId] = \
                            self.x[time:, candIndex].copy(), self.y[time:, candIndex].copy(), self.z[time:, candIndex].copy()
                        xtmp[nowTime:time, nanJointId], ytmp[nowTime:time, nanJointId], ztmp[nowTime:time, nanJointId] = 0.0, 0.0, 0.0

                        inds = np.where((xtmp[time:, nanJointId] == 0.0) & (ytmp[time:, nanJointId] == 0.0) & (ztmp[time:, nanJointId] == 0.0))[0]
                        if inds.size == 0:
                            nowTime = self.frame_max
                        else:
                            nowTime = time + inds[0]

                        break

                    if time == self.frame_max - 1:
                        #xtmp[nowTime:, nanJointId], ytmp[nowTime:, nanJointId], ztmp[nowTime:, nanJointId] = 0.0, 0.0, 0.0 # may not be needed
                        nowTime = self.frame_max

        self.xopt, self.yopt, self.zopt = xtmp, ytmp, ztmp

    def auto_labelselect(self):
        with open(self.DefaultTrcPath_autolabeling, 'r') as f:
            data = np.genfromtxt(f, delimiter='\t', skip_header=6, missing_values=' ')
            xStand = data[:, 2::3][self.StandardFrame_autolabeling, :]
            yStand = data[:, 3::3][self.StandardFrame_autolabeling, :]
            zStand = data[:, 4::3][self.StandardFrame_autolabeling, :]

            jointindStand = self.Points.index(self.StandardJoint_autolabeling)

            # correlated coordinates
            xStand = xStand - xStand[jointindStand]
            yStand = yStand - yStand[jointindStand]
            zStand = zStand - zStand[jointindStand]

            indicesStandtmp = np.where(~np.isnan(xStand))[0]
            indicesStandtmp = indicesStandtmp[indicesStandtmp != jointindStand]


            xCand = self.xopt[self.frame, :] - self.xopt[self.frame, self.now_select]
            yCand = self.yopt[self.frame, :] - self.yopt[self.frame, self.now_select]
            zCand = self.zopt[self.frame, :] - self.zopt[self.frame, self.now_select]

            nonnannumlists = []
            for i in range(self.xopt.shape[1]):
                if i == self.now_select:
                    nonnannumlists.append(0) # eliminate selected index
                    continue
                nonnannumlists.append(np.sum((self.xopt[:, i] != 0.0) & (self.yopt[:, i] != 0.0) & (self.zopt[:, i] != 0.0)))
            nonnannumlists = np.argsort(nonnannumlists)[::-1][:indicesStandtmp.size]

            if np.where(np.isnan(xCand))[0].size > 0:
                return False



            # set selected joint
            self.xnew[:, jointindStand], self.ynew[:, jointindStand], self.znew[:, jointindStand] = \
                self.xopt[:, self.now_select], self.yopt[:, self.now_select], self.zopt[:, self.now_select]

            previousJoint = jointindStand
            while indicesStandtmp.size > 0:
                now_iSt = np.argmin((xStand[indicesStandtmp] - xStand[previousJoint])**2
                                    + (yStand[indicesStandtmp] - yStand[previousJoint])**2
                                    + (zStand[indicesStandtmp] - zStand[previousJoint])**2)

                nearestPreviousJoint_StandIndex = indicesStandtmp[now_iSt]

                candidate_nnnl = np.argmin((xCand[nonnannumlists] - xStand[nearestPreviousJoint_StandIndex])**2
                                            + (yCand[nonnannumlists] - yStand[nearestPreviousJoint_StandIndex])**2
                                            + (zCand[nonnannumlists] - zStand[nearestPreviousJoint_StandIndex])**2)

                nearestJoint_OptIndex = nonnannumlists[candidate_nnnl]

                # update
                self.xnew[:, nearestPreviousJoint_StandIndex], self.ynew[:, nearestPreviousJoint_StandIndex], self.znew[:, nearestPreviousJoint_StandIndex] = \
                    self.xopt[:, nearestJoint_OptIndex], self.yopt[:, nearestJoint_OptIndex], self.zopt[:, nearestJoint_OptIndex]

                # delete now joint index
                indicesStandtmp = np.delete(indicesStandtmp, now_iSt)

                # delete candidate point
                nonnannumlists = np.delete(nonnannumlists, candidate_nnnl)

        nanIndices = np.where((self.xnew == 0.0) & (self.ynew == 0.0) & (self.znew == 0.0))
        self.xnew[nanIndices], self.ynew[nanIndices], self.znew[nanIndices] = np.nan, np.nan, np.nan
        self.setbone()

        return True



class Annotator(QMainWindow, Data):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        Data.__init__(self)

        self.setWindowTitle('Annotator with matplotlib')
        self.create_menu()
        self.create_main_frame()
        self.setleftDock()
        self.filed = False
        self.xbutton = False
        self.ybutton = False
        self.zbutton = False

    def draw(self, fix=False):
        if self.filed:
            if fix:
                azim = self.axes.azim
                elev = self.axes.elev
                xlim = self.axes.get_xlim().copy()
                ylim = self.axes.get_ylim().copy()
                zlim = self.axes.get_zlim().copy()
                addlim = np.max([xlim[1]-xlim[0], ylim[1]-ylim[0], zlim[1]-zlim[0]])
                xlim[1] = xlim[0] + addlim
                ylim[1] = ylim[0] + addlim
                zlim[1] = zlim[0] + addlim
            # clear the axes and redraw the plot anew
            #
            self.axes.clear()
            plt.title('frame number=' + str(self.frame))
            self.axes.set_xlabel('x')
            self.axes.set_ylabel('y')
            self.axes.set_zlabel('z')
            self.axes.grid(self.grid_cb.isChecked())

            if fix:
                self.axes.set_xlim(xlim)
                self.axes.set_ylim(ylim)
                self.axes.set_zlim(zlim)
                self.axes.view_init(elev=elev, azim=azim)

            if self.trajectory_line is not None:
                self.axes.lines.extend(self.trajectory_line)

            if self.leftdockwidget.radioorigin.isChecked():
                self.scatter = [
                    self.axes.scatter3D(self.x[self.frame, i], self.y[self.frame, i], self.z[self.frame, i], ".",
                                        color='blue', picker=5) for i in range(self.joints)]

                if self.now_select != -1:
                    self.scatter[self.now_select] = self.axes.scatter3D(self.x[self.frame, self.now_select],
                                                                        self.y[self.frame, self.now_select],
                                                                        self.z[self.frame, self.now_select], ".",
                                                                        color='red', picker=5)

            elif self.leftdockwidget.radioauto.isChecked():
                self.scatter = [
                    self.axes.scatter3D(self.xopt[self.frame, i], self.yopt[self.frame, i], self.zopt[self.frame, i], ".",
                                        color='blue', picker=5) for i in range(self.joints)]

                if self.now_select != -1:
                    self.scatter[self.now_select] = self.axes.scatter3D(self.xopt[self.frame, self.now_select],
                                                                        self.yopt[self.frame, self.now_select],
                                                                        self.zopt[self.frame, self.now_select], ".",
                                                                        color='red', picker=5)
            else:
                self.scatter = [
                    self.axes.scatter3D(self.xnew[self.frame, i], self.ynew[self.frame, i], self.znew[self.frame, i], ".",
                                        color='blue', picker=5) for i in range(len(self.Points))]

                if self.now_select != -1:
                    self.scatter[self.now_select] = self.axes.scatter3D(self.xnew[self.frame, self.now_select],
                                                                        self.ynew[self.frame, self.now_select],
                                                                        self.znew[self.frame, self.now_select], ".",
                                                                        color='red', picker=5)

                #if len(self.bone1[self.frame]) != 0:
                if self.leftdockwidget.check_showbone.isChecked():
                    for bone1, bone2 in zip(self.bone1[self.frame], self.bone2[self.frame]):
                        self.axes.plot([bone1[0], bone2[0]], [bone1[1], bone2[1]], [bone1[2], bone2[2]], "-",
                                       color="black")

            self.canvas.draw()


        else:
            self.axes.clear()
            self.axes.grid(self.grid_cb.isChecked())
            self.canvas.draw()

    ###
    # menu
    ###
    def create_menu(self):
        # file
        self.file_menu = self.menuBar().addMenu("&File")

        input_action = self.create_action("&Input", slot=self.input_c3d_or_csvfile, shortcut="Ctrl+I", tip="Input csv file")
        self.add_actions(self.file_menu, (input_action,))

        output_action = self.create_action("&Output", slot=self.output, shortcut="Ctrl+O", tip="Output annotated csv file")
        self.add_actions(self.file_menu, (output_action,))

        quit_action = self.create_action("&Quit", slot=self.close, shortcut="Ctrl+Q", tip="Close the application")
        self.add_actions(self.file_menu, (None, quit_action))

        # help
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", shortcut='F1', slot=self.show_about, tip='About the demo')
        self.add_actions(self.help_menu, (about_action,))

        # edit
        self.edit_menu = self.menuBar().addMenu("&Edit")

        nextframe_action = self.create_action("&Next", slot=self.nextframe, shortcut="Ctrl+N", tip="show next frame")
        self.add_actions(self.edit_menu, (nextframe_action,))

        previousframe_action = self.create_action("&Previous", slot=self.previousframe, shortcut="Ctrl+P", tip="show previous frame")
        self.add_actions(self.edit_menu, (previousframe_action,))

        self.cutframe_action = self.create_action("&Cut frame", slot=self.cutframe, shortcut="Ctrl+C", tip="Remove redundant frames")
        self.add_actions(self.edit_menu, (self.cutframe_action,))
        self.cutframe_action.setEnabled(False)

        self.removePoints_action = self.create_action("Remove Points", slot=self.removePoints, shortcut="Ctrl+D", tip="Convert selected points into nan")
        self.add_actions(self.edit_menu, (self.removePoints_action,))
        self.removePoints_action.setEnabled(False)

        # Automation
        self.automation_menu = self.menuBar().addMenu("&Automation")

        self.autoselection_action = self.create_action("Optimal selection", slot=self.autoSelect, shortcut="Ctrl+Shift+A", tip="Auto selection")
        self.add_actions(self.automation_menu, (self.autoselection_action,))
        self.autoselection_action.setEnabled(False)

        self.autolabeling_action = self.create_action("Auto-Labeling", slot=self.autoLabeling, shortcut="Ctrl+Shift+L", tip="Auto labeling")
        self.add_actions(self.automation_menu, (self.autolabeling_action,))
        self.autolabeling_action.setEnabled(False)
        # Preference
        self.preference_menu = self.menuBar().addMenu("&Preference")

        self.configuration_action = self.create_action("&Configuration", slot=self.configure, shortcut="Ctrl+,", tip="Set configuration")
        self.add_actions(self.preference_menu, (self.configuration_action,))

        # set
        self.set_menu = self.menuBar().addMenu("&Set")

        setinit_action = self.create_action("Init Frame", slot=self.setInit, shortcut="Shift+I", tip="Set now frame to initial frame")
        self.add_actions(self.set_menu, (setinit_action,))

        setinitzero_action = self.create_action("Init 0", slot=self.setInitzero, shortcut="Ctrl+Shift+I",
                                                 tip="Set now frame to initial frame")
        self.add_actions(self.set_menu, (setinitzero_action,))

        setfin_action = self.create_action("Fin Frame", slot=self.setFin, shortcut="Shift+F",
                                                 tip="Set now frame to finish frame")
        self.add_actions(self.set_menu, (setfin_action,))

        setfinmax_action = self.create_action("Fin max", slot=self.setFinmax, shortcut="Ctrl+Shift+F",
                                                tip="Set now frame to finish frame")
        self.add_actions(self.set_menu, (setfinmax_action,))


    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False,
                      signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def input_c3d_or_csvfile(self):
        filters = "CSV files(*.csv);;C3D files(*.c3d)"
        selected_filter = "C3D files(*.c3d)"
        self.path = unicode(QFileDialog.getOpenFileName(self, 'load file', self.lastopenedpath, filters, selected_filter))
        try:
            if self.path:
                if self.path.split('/')[-1].split('.')[-1] in ['csv', 'CSV']:
                    self.read_from_csv(self.path)

                else:  # c3d
                    self.read_from_c3d(self.path)

                self.lastopenedpath = ""
                if os.name == 'nt': # windows
                    for directory in self.path.split('\\')[:-1]:
                        self.lastopenedpath += directory + "\\"
                else:
                    for directory in self.path.split('/')[:-1]:
                        self.lastopenedpath += directory + "/"

            else:
                msg = """You should select .csv file!"""
                QMessageBox.about(self, "Caution", msg.strip())
                return False

            self.now_select = -1
            self.trajectory_line = None

            # search index
            tmp_index_num = [np.sum(self.x[i][self.x[i] != 0]) for i in range(self.frame_max)]

            self.frame = np.argmax(tmp_index_num)
            # self.scatter = [
            #    self.ax.scatter3D(self.x[self.frame][i], self.y[self.frame][i], self.z[self.frame][i], ".", color=color,
            #                     picker=5)
            #    for i in range(self.joints)]
            self.filed = True
            self.draw()

            self.slider.setEnabled(True)
            self.slider.setMaximum(self.frame_max - 1)
            self.slider.setMinimum(0)
            self.slider.setValue(self.frame)

            self.leftdock.setEnabled(True)
            self.leftdockwidget.spininit.setMaximum(self.frame_max - 1)
            self.leftdockwidget.spinfin.setMaximum(self.frame_max - 1)
            self.leftdockwidget.spinfin.setValue(self.frame_max - 1)
            self.cutframe_action.setEnabled(True)

            self.groupxrange.setEnabled(True)
            self.groupyrange.setEnabled(True)
            self.groupzrange.setEnabled(True)

            self.autoselection_action.setEnabled(True)

            return True

        except:
            return False

    def output(self):
        if self.filed:
            filters = "TRC files(*.trc)"
             #selected_filter = "CSV files(*.csv)"
            if os.name == 'nt':
                filename, __ = os.path.splitext(self.path.split('\\')[-1])
            else:
                filename, __ = os.path.splitext(self.path.split('/')[-1])

            filename += '.trc'

            savepath, extension = QFileDialog.getSaveFileNameAndFilter(self, 'Save file', self.lastsavedpath + filename, filters)

            savepath = str(savepath).encode()
            extension = str(extension).encode()
            #print(extension)
            if savepath != "":
                if savepath[-4:] != '.trc':
                    savepath += '.trc'
                with open(savepath, 'wb') as f:
                    f.write("PathFileType\t4\t(X/Y/Z)\t{0}\t\n".format(savepath))
                    f.write("DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\t\n")
                    f.write("{0}\t{0}\t{1}\t{2}\t{3}\t{0}\t1\t{1}\t\n".format(self.fps, self.frame_max + 1, len(self.Points), self.units))

                    line1 = "Frame#\tTime\t"
                    line2 = "\t\t"
                    for index, point in enumerate(self.Points):
                        line1 += "{0}\t\t\t".format(point)
                        line2 += "X{0}\tY{0}\tZ{0}\t".format(index + 1)
                    line1 += "\t\n"
                    line2 += "\t\n"

                    f.write(line1)
                    f.write(line2)
                    f.write("\t\n")

                with open(savepath, 'a') as f:
                    data = np.zeros((self.xnew.shape[0], self.xnew.shape[1]*3 + 2))
                    # frame
                    data[:, 0] = np.arange(1, self.frame_max + 1)
                    # time
                    data[:, 1] = np.arange(0, self.frame_max/float(self.fps), 1/float(self.fps))

                    # x
                    data[:, 2::3] = self.xnew
                    # y
                    data[:, 3::3] = self.ynew
                    # z
                    data[:, 4::3] = self.znew

                    np.savetxt(f, data, delimiter='\t')

                if os.name == 'nt': # windows
                    for directory in savepath.split('\\')[:-1]:
                        self.lastsavedpath += directory + "\\"
                else:
                    for directory in savepath.split('/')[:-1]:
                        self.lastsavedpath += directory + "/"

                QMessageBox.information(self, "Saved", "Saved to {0}".format(savepath))


    def show_about(self): # show detail of this application
        msg = """ A demo of using PyQt with matplotlib:

         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())

    ###
    # main widget
    ###
    def create_main_frame(self):
        self.main_frame = QWidget()

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = Axes3D(self.fig)

        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.onclick)
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        self.canvas.mpl_connect('key_press_event', self.onkey)
        self.canvas.mpl_connect('key_release_event', self.onrelease)

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(True)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), lambda: self.draw(fix=True))

        # x range selector
        self.groupxrange = QGroupBox("x")
        hboxX = QHBoxLayout()
        self.buttonXminus = QPushButton("<")
        self.buttonXminus.clicked.connect(lambda: self.rangeChanger("x", False))
        hboxX.addWidget(self.buttonXminus)

        self.buttonXplus = QPushButton(">")
        self.buttonXplus.clicked.connect(lambda: self.rangeChanger("x", True))
        hboxX.addWidget(self.buttonXplus)
        self.groupxrange.setLayout(hboxX)

        # y range selector
        self.groupyrange = QGroupBox("y")
        hboxY = QHBoxLayout()
        self.buttonYminus = QPushButton("<")
        self.buttonYminus.clicked.connect(lambda: self.rangeChanger("y", False))
        hboxY.addWidget(self.buttonYminus)

        self.buttonYplus = QPushButton(">")
        self.buttonYplus.clicked.connect(lambda: self.rangeChanger("y", True))
        hboxY.addWidget(self.buttonYplus)
        self.groupyrange.setLayout(hboxY)

        # z range changer
        self.groupzrange = QGroupBox("z")
        hboxZ = QHBoxLayout()
        self.buttonZminus = QPushButton("<")
        self.buttonZminus.clicked.connect(lambda: self.rangeChanger("z", False))
        hboxZ.addWidget(self.buttonZminus)

        self.buttonZplus = QPushButton(">")
        self.buttonZplus.clicked.connect(lambda: self.rangeChanger("z", True))
        hboxZ.addWidget(self.buttonZplus)
        self.groupzrange.setLayout(hboxZ)

        self.groupxrange.setEnabled(False)
        self.groupyrange.setEnabled(False)
        self.groupzrange.setEnabled(False)
        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [self.grid_cb, self.groupxrange, self.groupyrange, self.groupzrange]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        self.setslider(vbox)
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)


    def onclick(self, event):
        if self.filed:
            ind = event.ind[0]
            x0, y0, z0 = event.artist._offsets3d
            if self.leftdockwidget.radioorigin.isChecked():
                self.now_select = np.where(self.x[self.frame] == x0[ind])[0][0]
            elif self.leftdockwidget.radioauto.isChecked():
                self.now_select = np.where(self.xopt[self.frame] == x0[ind])[0][0]
            else:
                self.now_select = np.where(self.xnew[self.frame] == x0[ind])[0][0]

            self.leftdockwidget.onclicked_Enabled(True)
            #self.setmenuEnabled("click", True)
            self.setFrameLabel()

            if self.leftdockwidget.check_trajectory.isChecked():
                self.show_trajectory()
                return

            self.draw(fix=True)

    def onrelease(self, event):
        if self.filed:
            if self.xbutton and event.key == '.':
                self.rangeChanger("x", True)
            elif self.xbutton and event.key == ',':
                self.rangeChanger("x", False)
            elif self.ybutton and event.key == '.':
                self.rangeChanger("y", True)
            elif self.ybutton and event.key == ',':
                self.rangeChanger("y", False)
            elif self.zbutton and event.key == '.':
                self.rangeChanger("z", True)
            elif self.zbutton and event.key == ',':
                self.rangeChanger("z", False)

            if event.key == 'x':
                self.xbutton = False
            elif event.key == 'y':
                self.ybutton = False
            elif event.key == 'z':
                self.zbutton = False

    def onkey(self, event):
        if self.filed:
            if event.key == ',' and self.frame != 0 and not self.xbutton and not self.ybutton and not self.zbutton:
                self.frame += -1
                self.sliderSetValue(self.frame)
            elif event.key == '.' and self.frame != self.frame_max and not self.xbutton and not self.ybutton and not self.zbutton:
                self.frame += 1
                self.sliderSetValue(self.frame)
            elif event.key == 'q':
                result = QMessageBox.warning(self, "Will you quit?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if result == QMessageBox.Yes:
                    plt.close(event.canvas.figure)
                else:
                    pass
            elif event.key == 'x':
                self.xbutton = True
            elif event.key == 'y':
                self.ybutton = True
            elif event.key == 'z':
                self.zbutton = True

            self.draw(fix=True)
            """
            self.axes.clear()
            self.axes.grid(self.grid_cb.isChecked())
            plt.title('frame number=' + str(self.frame))
            for i in range(self.joints):
                self.scatter[i] = self.axes.scatter3D(self.x[self.frame][i], self.y[self.frame][i],
                                                      self.z[self.frame][i],
                                                      ".", color='blue', picker=5)
            self.canvas.draw()
            """
            #self.now_select = -1

    def nextframe(self):
        if self.filed:
            if self.frame != self.frame_max:
                self.frame += 1
                self.sliderSetValue(self.frame)

    def previousframe(self):
        if self.filed:
            if self.frame != self.frame_max:
                self.frame += -1
                self.sliderSetValue(self.frame)

    def convertZero(self, init, fin):
        self.x[init:fin, self.now_select] = 0.0
        self.y[init:fin, self.now_select] = 0.0
        self.z[init:fin, self.now_select] = 0.0

        self.draw(fix=True)

    def convertNan(self, init, fin):
        self.xnew[init:fin, self.now_select] = np.nan
        self.ynew[init:fin, self.now_select] = np.nan
        self.znew[init:fin, self.now_select] = np.nan

        self.draw(fix=True)

    def setInit(self):
        self.leftdockwidget.spininit.setValue(self.frame)

    def setFin(self):
        self.leftdockwidget.spinfin.setValue(self.frame)

    def setInitzero(self):
        self.leftdockwidget.spininit.setValue(0)

    def setFinmax(self):
        self.leftdockwidget.spinfin.setValue(self.frame_max - 1)

    # dialog
    def cutframe(self):
        if self.filed:
            cutdialog = CutframeWindow(self)
            #self.cutdialog.setWindowModality(Qt.ApplicationModal)
            self.setmenuEnabled("menuClick", False)
            cutdialog.show()


    def configure(self):
        configdialog = ConfigureWindow(self)
        configdialog.setWindowModality(Qt.ApplicationModal)
        configdialog.show()


    def removePoints(self):
        removedialog = RemoveWindow(self)
        #self.removedialog.setWindowModality(Qt.ApplicationModal)
        self.setmenuEnabled("menuClick", False)
        removedialog.show()

    def rangeChanger(self, coordinates, plus):
        ticks = eval("self.axes.get_{0}ticks()".format(coordinates))
        if plus:
            width = ticks[1] - ticks[0]
        else:
            width = ticks[0] - ticks[1]

        lim = eval("self.axes.get_{0}lim()".format(coordinates))
        lim += width

        self.draw(fix=True)

        pass

    def autoSelect(self):
        self.optimal_select()

        QMessageBox.information(self, "Auto Optimal Selection", "Finished!!!")
        self.autolabeling_action.setEnabled(True)
        #setautolabeldialog = SetLabelforAuto(self)
        #self.setmenuEnabled("menuClick", False)
        #setautolabeldialog.show()

    def autoLabeling(self):
        if self.StandardFrame_autolabeling == -1:
            QMessageBox.warning(self, "Auto Labeling", "you must check preference(Ctrl+,)")
            return

        if not self.leftdockwidget.radioauto.isChecked():
            QMessageBox.warning(self, "Auto Labeling", "you must choose joint of Auto as standard")
            return

        if self.auto_labelselect():
            QMessageBox.information(self, "Auto Labeling", "Finished!!!")
        else:
            QMessageBox.warning(self, "Auto Labeling", "Invalid frame due to lack of real values")

    ###
    # UI
    ###
    # left dock
    def setleftDock(self):
        self.leftdock = QDockWidget(self)
        self.leftdock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.leftdock.setFloating(False)

        self.leftdockwidget = LeftDockWidget(self)
        self.leftdock.setWidget(self.leftdockwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.leftdock)
        self.leftdock.setEnabled(False)

    def show_trajectory(self):
        if self.filed:
            if self.now_select != -1:
                if self.leftdockwidget.radioorigin.isChecked():
                    x_trajectory = self.x.T
                    y_trajectory = self.y.T
                    z_trajectory = self.z.T
                elif self.leftdockwidget.radioauto.isChecked():
                    x_trajectory = self.xopt.T
                    y_trajectory = self.yopt.T
                    z_trajectory = self.zopt.T
                else:
                    x_trajectory = self.xnew.T
                    y_trajectory = self.ynew.T
                    z_trajectory = self.znew.T

                self.trajectory_line = self.axes.plot(x_trajectory[self.now_select], y_trajectory[self.now_select],
                                               z_trajectory[self.now_select], color='red')
                self.draw(fix=True)

                return

        self.trajectory_line = None

    # slider
    def setslider(self, vbox):
        #
        # slider
        #
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.sliderValueChanged)

        vbox.addWidget(self.slider)

        #self.topdock = QDockWidget(self)
        #self.topdock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        #self.topdock.setFloating(False)

        #self.topdock.setWidget(self.slider)
        #self.addDockWidget(Qt.TopDockWidgetArea, self.topdock)

    def sliderValueChanged(self):
        self.frame = self.slider.value()
        self.setFrameLabel()
        self.draw(fix=True)

    def sliderSetValue(self, value):
        self.slider.setValue(value)

    # set label
    def setFrameLabel(self):
        if self.now_select != -1:
            if self.leftdockwidget.radioorigin.isChecked():
                self.leftdockwidget.selectedlabel.setText(str(self.now_select))
            elif self.leftdockwidget.radioauto.isChecked():
                self.leftdockwidget.selectedlabel.setText(str(self.now_select))
            else:
                #self.leftdockwidget.selectedlabel.setText(self.label[self.frame][self.now_select])
                self.leftdockwidget.selectedlabel.setText(self.Points[self.now_select])
        else:
            self.leftdockwidget.selectedlabel.setText("No Selected")

        """
        # check automationbutton
        nolabelnum = 0
        for label in self.label[self.frame]:
            if label != "No Label":
                nolabelnum += 1

        if nolabelnum >= len(self.Points):
            self.leftdockwidget.automationbutton.setEnabled(True)
        else:
            self.leftdockwidget.automationbutton.setEnabled(False)
        """

    # set enabled menu with click event
    def setmenuEnabled(self, EVENT, BOOL):
        if EVENT == "click":
            self.removePoints_action.setEnabled(BOOL)
            #self.autolabeling_action.setEnabled(BOOL)
            #self.autoselection_action.setEnabled(BOOL)
        elif EVENT == "menuClick":
            self.leftdock.setEnabled(BOOL)
            self.file_menu.setEnabled(BOOL)
            self.cutframe_action.setEnabled(BOOL)
            self.configuration_action.setEnabled(BOOL)
            self.removePoints_action.setEnabled(BOOL)
            #self.autolabeling_action.setEnabled(BOOL)
            #self.autoselection_action.setEnabled(BOOL)

    def closeEvent(self, QCloseEvent):
        with open(self.configurePath, "w") as f:
            f.write("fps\t{0}\tint\t\n".format(self.fps))
            f.write("units\t{0}\tstr\t\n".format(self.units))
            f.write("Threshold_optimal\t{0}\tfloat\t\n".format(self.Threshold_optimal))
            f.write("StandardJoint_autolabeling\t{0}\tstr\t\n".format(self.StandardJoint_autolabeling))
            f.write("DefaultTrcPath_autolabeling\t{0}\tstr\t\n".format(self.DefaultTrcPath_autolabeling))
            f.write("StandardFrame_autolabeling\t{0}\tint\t\n".format(self.StandardFrame_autolabeling))

            f.write("lastopenedpath\t{0}\tstr\t\n".format(self.lastopenedpath))
            f.write("lastsavedpath\t{0}\tstr\t\n".format(self.lastsavedpath))


print("activate qt4!")
app = QApplication(sys.argv)
form = Annotator()
form.show()
app.exec_()