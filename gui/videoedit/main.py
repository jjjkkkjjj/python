# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import numpy as np
import os

from leftdock import VideoListDockWidget
from central import VideoDisplayWidget

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        # data
        self.data = []

        # parameter
        self.width = 960
        self.height = 640
        self.framerate = 30

        self.initUI()

    def initUI(self):

        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        # メニューバーのアイコン設定
        openFile = QAction('Open video', self)
        # ショートカット設定
        openFile.setShortcut('Ctrl+O')
        # ステータスバー設定
        openFile.setStatusTip('Open new video')
        openFile.triggered.connect(self.showDialog)

        saveFile = QAction('Save video', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save video')
        saveFile.triggered.connect(self.savevideo)

        quitapplication = QAction('quit', self)
        quitapplication.setShortcut('Ctrl+Q')
        quitapplication.setStatusTip('Close The App')
        quitapplication.triggered.connect(self.quit)

        nextframe = QAction('next frame', self)
        nextframe.setShortcut('Ctrl+N')
        nextframe.setStatusTip('Move next frame')
        nextframe.triggered.connect(lambda: self.showimage(range(len(self.data)), nextframe_num=1))

        previousframe = QAction('previous frame', self)
        previousframe.setShortcut('Ctrl+P')
        previousframe.setStatusTip('Move previous frame')
        previousframe.triggered.connect(lambda: self.showimage(range(len(self.data)), nextframe_num=-1))

        # メニューバー作成
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(quitapplication)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(nextframe)
        editMenu.addAction(previousframe)

        # self.setGeometry(300, 300, 750, 500)
        # self.setWindowTitle('File dialog')

        self.leftdock_videolist = QDockWidget(self)
        self.leftdock_videolist.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.leftdock_videolist.setFloating(False)
        self.leftdock_videowidget = VideoListDockWidget(self)
        self.leftdock_videolist.setWidget(self.leftdock_videowidget)
        self.leftdock_videolist.setMinimumSize(QSize(400, self.maximumHeight()))
        # self.leftdock_videolist.setWidget(SliderTreeView())

        self.addDockWidget(Qt.LeftDockWidgetArea, self.leftdock_videolist)

        self.Videowidget = VideoDisplayWidget(self)
        #self.video = VideoCapture(self.Videowidget)
        self.setCentralWidget(self.Videowidget)

        self.showMaximized()

    def showDialog(self):
        # 第二引数はダイアログのタイトル、第三引数は表示するパス
        fname = QFileDialog.getOpenFileName(self, 'Open file', '')
        # fname[0]は選択したファイルのパス（ファイル名を含む）
        if fname[0]:
            self.add_video(fname[0])

    def add_video(self, videopath):
        video = cv2.VideoCapture(videopath.encode('utf-8'))
        frame_num = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.Videowidget.show_progressbar(frame_num)
        #pixcelimg = []
        imges = []
        for num in range(frame_num):
            ret, img = video.read()
            imges.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (self.width, self.height)))
            self.Videowidget.setprogressvalue(num)
        self.data.append({"img": imges, "now": 0, "max": frame_num})
        self.Videowidget.finishprogress()
        self.leftdock_videowidget.add(videopath, 0)

        self.showimage(range(len(self.data)))

    def remove_video(self, rowIndexes):
        for row in sorted(rowIndexes, reverse=True):
            del self.data[row]
        self.showimage(range(len(self.data)))

    def showimage(self, rowindex, nextframe_num=0):
        # process
        if len(rowindex) != 0:
            for i in range(len(self.leftdock_videowidget.slidertreeview.sliders)):
                if (self.data[i]["now"] == self.data[i]["max"] - 1 and nextframe_num > 0) or (self.data[i]["now"] == 0 and nextframe_num < 0):
                    self.Videowidget.timer.stop()
                else:
                    self.data[i]["now"] += nextframe_num
                    self.leftdock_videowidget.next_slidervalue(i)
            # image process

            img = self.data[rowindex[0]]["img"][self.data[rowindex[0]]["now"]]
            for index in rowindex[1:]:
                img = cv2.hconcat([img, self.data[index]["img"][self.data[index]["now"]]])
            self.Videowidget.draw(cv2.resize(img, (self.width, self.height)))
        else:
            self.Videowidget.draw()

    def sliderchanged(self):
        Slider = self.sender()
        for i, slider in enumerate(self.sliders):
            if slider == Slider:
                print i
                break

    def start_button_clicked(self):
        self.Videowidget.timer.timeout.connect(lambda: self.showimage(range(len(self.data)), nextframe_num=1))
        self.Videowidget.timer.start(10)  # ミリ秒単位

    def pause_button_clicked(self):
        self.Videowidget.timer.stop()

    def savevideo(self):
        if len(self.data) < 2:
            QMessageBox.warning(self, "warning", "choose more than 2 videos")
            return
        if self.Videowidget.checkbox_connect.isChecked() and self.Videowidget.checkbox_overlay.isChecked():
            checknum = 2
        elif not self.Videowidget.checkbox_connect.isChecked() and not self.Videowidget.checkbox_overlay.isChecked():
            QMessageBox.warning(self, "warning", "check either connect or overlay at least")
            return
        else:
            checknum = 1

        savename = QFileDialog.getExistingDirectory(self, 'Save file', '')
        if savename != "":
            nowlist = []
            video_name = ""
            for index in range(len(self.data)):
                nowlist.append(self.data[index]["now"])
                name, ext = os.path.splitext(self.leftdock_videowidget.slidertreeview.items[index]["name"])
                video_name += name + "-"
            nowlist = np.array(nowlist)
            nowmin_index = np.argmin(nowlist)

            new_startframe = np.array([nowlist[index] - nowlist[nowmin_index] for index in range(len(self.data))])
            new_framemax = np.array([self.data[index]["max"] - new_startframe[index] for index in range(len(self.data))])
            min_of_max = np.min(new_framemax)
            hdiv = int((len(self.data) + 1)/2)

            self.Videowidget.show_progressbar(min_of_max*checknum)
            fourcc = cv2.VideoWriter_fourcc(*'MPEG')
            if self.Videowidget.checkbox_connect.isChecked():

                video_out = cv2.VideoWriter(savename + "/" + video_name + "connect.MP4", int(fourcc), self.framerate,
                                            (self.width, self.height))
                for frame in range(min_of_max):
                    himg = [np.zeros((int(self.width / 2), int(self.height), 3), np.uint8) for i in range(hdiv)]
                    for hnum in range(hdiv):
                        time0 = new_startframe[hnum * 2] + frame
                        img0 = cv2.resize(self.data[hnum * 2]["img"][time0], (int(self.width / 2), int(self.height/hdiv)))
                        if hnum * 2 + 1 == len(self.data):
                            img1 = np.zeros((int(self.height/hdiv), int(self.width/2), 3), np.uint8)
                        else:
                            time1 = new_startframe[hnum * 2 + 1] + frame
                            img1 = cv2.resize(self.data[hnum * 2 + 1]["img"][time1], (int(self.width / 2), int(self.height/hdiv)))


                        himg[hnum] = cv2.hconcat([img0, img1])

                        if hnum == 0:
                            output_img = himg[0].copy()
                            continue
                        else:
                            output_img = cv2.vconcat([output_img, himg[hnum]])

                    video_out.write(cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR))
                    self.Videowidget.setprogressvalue(frame)

                video_out.release()

            if self.Videowidget.checkbox_overlay.isChecked():
                video_out = cv2.VideoWriter(savename + "/" + video_name + "overlay.MP4", int(fourcc), self.framerate,
                                            (self.width, self.height))
                for frame in range(min_of_max):
                    time0 = new_startframe[0] + frame
                    output_img = cv2.resize(self.data[0]["img"][time0], (self.width, self.height)).copy()
                    for index in range(1, len(self.data)):
                        timeindex = new_startframe[index] + frame
                        output_img = cv2.addWeighted(output_img, float(index + 1) / (index + 2),
                                                     cv2.resize(self.data[index]["img"][timeindex], (self.width, self.height))
                                                     , float(1) / (index + 2), 0.0)
                    video_out.write(cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR))
                    self.Videowidget.setprogressvalue(min_of_max*(checknum - 1) + frame)
                self.Videowidget.finishprogress()

                video_out.release()

            QMessageBox.information(self, "info", "finished!")


    def quit(self):
        choice = QMessageBox.question(self, 'Message', 'Do you really want to exit?', QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())