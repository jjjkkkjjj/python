# -*- coding: utf-8 -*-
"""
This demo demonstrates how to embed a matplotlib (mpl) plot 
into a PyQt4 GUI application, including:
* Using the navigation toolbar
* Adding data to the plot
* Dynamically modifying the plot's properties
* Processing mpl events
* Saving the plot to a file from a menu
The main goal is to serve as a basis for developing rich PyQt GUI
applications featuring mpl plots (using the mpl OO API).
Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 19.01.2009
"""
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as anm
import numpy as np
import csv
import math


class AppForm(QMainWindow):
    Line = [[0, 1], [0, 2], [1, 2], [7, 8], [8, 10], [9, 10], [7, 9], [7, 11], [8, 18], [9, 12], [10, 19], [11, 12],
            [12, 19], [18, 19], [18, 11], [11, 13],
            [12, 14], [13, 14], [13, 15], [14, 16], [15, 16], [15, 17], [16, 17], [18, 20], [19, 21], [20, 21],
            [20, 23], [21, 24], [23, 24], [23, 25], [24, 25],
            [3, 5], [3, 6], [5, 6]]

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')
        self.create_menu()
        self.create_main_frame()
        self.setUI()
        self.input()
        self.create_status_bar()

        self.on_draw()

    '''
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        path = unicode(QFileDialog.getSaveFileName(self,
                                                   'Save file', '',
                                                   file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    '''
    def input(self):
        file_choices = "CSV files(*.csv)"

        self.path = unicode(QFileDialog.getOpenFileName(self,
                                                   'load file', '',
                                                   file_choices))

        if self.path:
            self.data = ViewOnly(self.path, remove_rows=slice(0,6), remove_cols=slice(0,2))

            self.playing = True
            self.now_select = -1
            self.time = 0

            self.ani = anm.FuncAnimation(self.fig, self.__update, fargs=
            (self.data.data, self.data.exX, self.data.exY, self.data.exZ),
                                         interval=20, frames=self.data.time - 1)
            self.button_play.setEnabled(False)
            self.button_trajectory.setEnabled(False)
            return True
        else:
            msg = """You should select .csv file!"""
            QMessageBox.about(self, "Caution", msg.strip())
            sys.exit()
            return False
            #self.canvas.print_figure(path, dpi=self.dpi)
            #self.statusBar().showMessage('Saved to %s' % path, 2000)

    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:

         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())

    def on_save(self):
        if not self.playing:

            file_choices = "MP4 file(*.MP4)|*.mp4"

            path = unicode(QFileDialog.getSaveFileName(self,
                                                       'Save file', '',
                                                       file_choices)) + '.mp4'
            if path:
                self.ani.save(path)
                self.statusBar().showMessage('Saved to %s' % path, 2000)

    def __update(self, time, data, extX, extY, extZ):
        if time != 0:
            self.axes.cla()

        self.axes.set_xlim(extX)
        self.axes.set_ylim(extY)
        self.axes.set_zlim(extZ)
        self.axes.grid(self.grid_cb.isChecked())

        for line in self.Line:
            self.axes.plot([data[line[0], time, 0], data[line[1], time, 0]],
                           [data[line[0], time, 1], data[line[1], time, 1]],
                           [data[line[0], time, 2], data[line[1], time, 2]], "-", color='black')
        self.axes.scatter3D(data[:, time, 0], data[:, time, 1], data[:, time, 2], ".", color='black')
        self.time = time
        plt.title('frame = ' + str(time + 1))

    def on_draw(self):
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()
        self.axes.set_xlim(self.data.exX)
        self.axes.set_ylim(self.data.exY)
        self.axes.set_zlim(self.data.exZ)
        self.axes.grid(self.grid_cb.isChecked())
        plt.title('frame = ' + str(self.time + 1))
        for line in self.Line:
            self.axes.plot([self.data.data[line[0], self.time, 0], self.data.data[line[1], self.time, 0]],
                           [self.data.data[line[0], self.time, 1], self.data.data[line[1], self.time, 1]],
                           [self.data.data[line[0], self.time, 2], self.data.data[line[1], self.time, 2]], "-",
                           color='black')
        self.scatter = [
            self.axes.scatter3D(self.data.data[i, self.time, 0], self.data.data[i, self.time, 1],
                                self.data.data[i, self.time, 2], ".",
                                color='black', picker=5)
            for i in range(len(self.data.data))]

        self.canvas.draw()

        self.now_select = -1


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

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(True)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [self.grid_cb]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)


    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")

        save_action = self.create_action("&Save", slot=self.on_save,
                                         shortcut="Ctrl+S", tip="Save the MP4")
        quit_action = self.create_action("&Quit", slot=self.close,
                                         shortcut="Ctrl+Q", tip="Close the application")
        self.add_actions(self.file_menu,
                         (None, save_action, quit_action))

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
                                          shortcut='F1', slot=self.on_about,
                                          tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

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

    def setUI(self):
        # button
        self.button_play = QPushButton('play', self)
        self.button_play.move(0,50)
        self.button_pause = QPushButton('pause', self)
        self.button_pause.move(0, 75)
        self.button_trajectory = QPushButton('Trajectory', self)
        self.button_trajectory.move(0, 100)
        self.connect(self.button_play, SIGNAL('clicked()'), self.play_ani)
        self.connect(self.button_pause, SIGNAL('clicked()'), self.pause_ani)
        self.connect(self.button_trajectory, SIGNAL('clicked()'), self.show_trajectory)

    def __button_enabled(self):
        self.button_play.setEnabled(not self.playing)
        self.button_pause.setEnabled(self.playing)
        if not self.playing and self.now_select != -1:
            self.button_trajectory.setEnabled(True)
        else:
            self.button_trajectory.setEnabled(False)

    def play_ani(self):
        if not self.playing:
            self.ani.event_source.start()
            self.playing = not self.playing
            self.now_select = -1
            self.__button_enabled()

    def pause_ani(self):
        if self.playing:
            self.ani.event_source.stop()

            self.axes.clear()
            self.axes.set_xlim(self.data.exX)
            self.axes.set_ylim(self.data.exY)
            self.axes.set_zlim(self.data.exZ)
            self.axes.grid(self.grid_cb.isChecked())
            plt.title('frame = ' + str(self.time + 1))
            for line in self.Line:
                self.axes.plot([self.data.data[line[0], self.time, 0], self.data.data[line[1], self.time, 0]],
                               [self.data.data[line[0], self.time, 1], self.data.data[line[1], self.time, 1]],
                               [self.data.data[line[0], self.time, 2], self.data.data[line[1], self.time, 2]], "-", color='black')
            self.scatter = [
                self.axes.scatter3D(self.data.data[i, self.time, 0], self.data.data[i, self.time, 1], self.data.data[i, self.time, 2], ".",
                                    color='black', picker=5)
                for i in range(len(self.data.data))]
            self.canvas.draw()

            self.playing = not self.playing
            self.__button_enabled()

    def show_trajectory(self):
        if self.now_select != -1:
            self.now_plot = self.axes.plot(self.data.data[self.now_select, :, 0], self.data.data[self.now_select, :, 1],
                                           self.data.data[self.now_select, :, 2], color='red')
            self.canvas.draw()

    def onclick(self, event):
        if not self.playing:
            ind = event.ind[0]
            x0, y0, z0 = event.artist._offsets3d

            self.now_select = np.where(self.data.data[:, self.time, 0] == x0[ind])[0][0]

            self.axes.clear()
            self.axes.set_xlim(self.data.exX)
            self.axes.set_ylim(self.data.exY)
            self.axes.set_zlim(self.data.exZ)
            self.axes.grid(self.grid_cb.isChecked())
            plt.title('frame = ' + str(self.time + 1))
            for line in self.Line:
                self.axes.plot([self.data.data[line[0], self.time, 0], self.data.data[line[1], self.time, 0]],
                               [self.data.data[line[0], self.time, 1], self.data.data[line[1], self.time, 1]],
                               [self.data.data[line[0], self.time, 2], self.data.data[line[1], self.time, 2]], "-", color='black')
            self.scatter = [
                self.axes.scatter3D(self.data.data[i, self.time, 0], self.data.data[i, self.time, 1], self.data.data[i, self.time, 2], ".",
                                    color='black', picker=5)
                for i in range(len(self.data.data))]

            self.scatter[self.now_select].remove()
            self.now_scatter = self.axes.scatter3D(self.data.data[self.now_select, self.time, 0],
                                                   self.data.data[self.now_select, self.time, 1],
                                                   self.data.data[self.now_select, self.time, 2], ".", color='red', picker=5)

            self.canvas.draw()
            self.__button_enabled()

    def onkey(self, event):
        if not self.playing:
            if event.key == ',' and self.time != 0:
                self.time += -1
            elif event.key == '.' and self.time != len(self.data.data):
                self.time += 1
            elif event.key == 'q':
                plt.close(event.canvas.figure)

            self.axes.clear()
            self.axes.set_xlim(self.data.exX)
            self.axes.set_ylim(self.data.exY)
            self.axes.set_zlim(self.data.exZ)
            self.axes.grid(self.grid_cb.isChecked())
            plt.title('frame = ' + str(self.time + 1))
            for line in self.Line:
                self.axes.plot([self.data.data[line[0], self.time, 0], self.data.data[line[1], self.time, 0]],
                               [self.data.data[line[0], self.time, 1], self.data.data[line[1], self.time, 1]],
                               [self.data.data[line[0], self.time, 2], self.data.data[line[1], self.time, 2]], "-",
                               color='black')
            self.scatter = [
                self.axes.scatter3D(self.data.data[i, self.time, 0], self.data.data[i, self.time, 1],
                                    self.data.data[i, self.time, 2], ".",
                                    color='black', picker=5)
                for i in range(len(self.data.data))]

            self.canvas.draw()

            self.now_select = -1


class ViewOnly:
    Line = [[0, 1], [0, 2], [1, 2], [7, 8], [8, 10], [9, 10], [7, 9], [7, 11], [8, 18], [9, 12], [10, 19], [11, 12],
            [12, 19], [18, 19], [18, 11], [11, 13],
            [12, 14], [13, 14], [13, 15], [14, 16], [15, 16], [15, 17], [16, 17], [18, 20], [19, 21], [20, 21],
            [20, 23], [21, 24], [23, 24], [23, 25], [24, 25],
            [3, 5], [3, 6], [5, 6]]

    def __init__(self, datapath, dim=3, remove_rows=None, remove_cols=None):
        input_data = []

        with open(datapath, "rb") as f:
            reader = csv.reader(f)
            for row in reader:
                if remove_cols is not None:
                    del row[remove_cols]
                if not row:
                    continue
                # input_data.append(row)

                tmp = []
                for data in row:
                    if not data:
                        tmp.append('nan')
                        continue
                    tmp.append(data)
                input_data.append(tmp)


        if remove_rows is not None:
            del input_data[remove_rows]

        input_data = np.array(input_data, dtype=np.float)

        return_inp_data = []

        for data_index in range(0, input_data.shape[1], dim):
            tmp_row = []
            for time in range(0, input_data.shape[0]):
                tmp = []
                for i in range(dim):
                    tmp.append(input_data[time][i + data_index])
                tmp_row.append(tmp)
            return_inp_data.append(tmp_row)

        self.data = np.array(return_inp_data)
        self.time = self.data.shape[1]
        xmax = np.nanmax(self.data[:, :, 0])
        xmin = np.nanmin(self.data[:, :, 0])
        ymax = np.nanmax(self.data[:, :, 1])
        ymin = np.nanmin(self.data[:, :, 1])
        zmax = np.nanmax(self.data[:, :, 2])
        zmin = np.nanmin(self.data[:, :, 2])
        aspectFT = np.array([xmax - xmin, ymax - ymin, zmax - zmin])
        add_tmp = aspectFT.max()
        addx = add_tmp - (xmax - xmin)
        addy = add_tmp - (ymax - ymin)
        addz = add_tmp - (zmax - zmin)
        self.exX = [xmin, xmax + addx]
        self.exY = [ymin, ymax + addy]
        self.exZ = [zmin, zmax + addz]

def main():
    #print "activate qt!"
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
