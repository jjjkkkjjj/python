# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import numpy as np
import os
import copy

class VideoEditor(QMainWindow):
    def __init__(self):
        super(VideoEditor, self).__init__()

        self.imgSize = [400, 300]
        self.imgs = []
        self.fps = 50
        self.frame = -1
        self.frameMax = -1

        self.Range = [-1, -1]

        self.initUI()
        self.createMenu()



    def initUI(self):
        self.mainWindow = QWidget()
        self.setFocusPolicy(Qt.ClickFocus)

        vbox = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        vbox.addWidget(self.slider)

        hbox = QHBoxLayout()
        self.labelFrame = QLabel()
        self.labelFrame.setText("Frame Number: -1")
        hbox.addWidget(self.labelFrame)

        self.labelCut = QLabel()
        self.labelCut.setText("{0} ~ {1}".format(self.Range[0], self.Range[1]))
        hbox.addWidget(self.labelCut)

        self.spinFps = QDoubleSpinBox()
        self.spinFps.setMaximum(10000)
        self.spinFps.setMinimum(1)
        self.spinFps.setValue(self.fps)
        self.spinFps.valueChanged.connect(self.spinFpsChanged)
        self.spinFps.setFocusPolicy(Qt.ClickFocus)
        hbox.addWidget(self.spinFps)
        vbox.addLayout(hbox)

        self.imageview = QLabel()
        self.imageview.setFixedSize(self.imgSize[0], self.imgSize[1])
        vbox.addWidget(self.imageview)

        hbox1 = QHBoxLayout()
        self.buttonPlay = QPushButton("Play")
        self.buttonPlay.clicked.connect(self.play)
        self.buttonPlay.setEnabled(False)
        hbox1.addWidget(self.buttonPlay)

        self.buttonStop = QPushButton("Stop")
        self.buttonStop.clicked.connect(self.stop)
        self.buttonStop.setEnabled(False)
        hbox1.addWidget(self.buttonStop)
        vbox.addLayout(hbox1)

        self.mainWindow.setLayout(vbox)
        self.setCentralWidget(self.mainWindow)


    def createMenu(self):
        self.filemenu = self.menuBar().addMenu("&File")

        read_action = self.create_action("Read Video", slot=self.readVideo, shortcut="Ctrl+R", tip="Read Video")
        self.add_actions(self.filemenu, (read_action,))

        self.write_action = self.create_action("Write Video", self.writeVideo, shortcut="Ctrl+W", tip="Write Video")
        self.add_actions(self.filemenu, (self.write_action,))
        self.write_action.setEnabled(False)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False,):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    # menu action
    def readVideo(self):
        filters = "MP4 files(*.mp4);;M4V files(*.m4v);;AVI files(*.avi)"
        selected_filter = "MP4 files(*.mp4)"
        self.path, __ = QFileDialog.getOpenFileName(self, 'load file', '', filters, selected_filter)

        if self.path != "":
            video = cv2.VideoCapture(self.path)

            self.fps = video.get(cv2.CAP_PROP_FPS)
            self.spinFps.setValue(self.fps)
            self.frame = 0
            self.frameMax = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.labelFrame.setText("Frame Number: 0")

            self.Range[0] = 0
            self.Range[1] = self.frameMax - 1
            self.labelCutUpdate()

            progressWindow = QDialog(self)

            hbox = QHBoxLayout()
            progressLabel = QLabel()
            progressLabel.setText("0 %")
            hbox.addWidget(progressLabel)

            progressBar = QProgressBar()
            progressBar.setRange(0, self.frameMax - 1)
            hbox.addWidget(progressBar)
            progressWindow.setLayout(hbox)

            progressWindow.show()

            for t in range(self.frameMax):
                ret, img = video.read()
                self.imgs.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), tuple(self.imgSize)))

                progressLabel.setText("{0} %".format(int((t + 1) * 100 / self.frameMax)))
                progressBar.setValue(t)
                QApplication.processEvents()

            progressWindow.close()
            video.release()

            self.draw()

            self.slider.setEnabled(True)
            self.slider.setMaximum(self.frameMax - 1)
            self.slider.setValue(0)

            self.timer = QTimer()
            self.timer.timeout.connect(self.updateVideo)

            self.buttonPlay.setEnabled(True)
            self.write_action.setEnabled(True)
        else:
            msg = """You should select video file!"""
            QMessageBox.about(self, "Caution", msg.strip())
        pass

    def writeVideo(self):
        #filters = "MP4 files(*.mp4);;M4V files(*.m4v);;AVI files(*.avi)"
        filters = "MP4 files(*.mp4)"
        selected_filter = "MP4 files(*.mp4)"
        self.outpath, extension = QFileDialog.getSaveFileName(self, 'load file', '', filters, selected_filter)

        if self.outpath != "":
            extension = extension[-5:-1]
            print(extension)
            if self.outpath[-4:] != extension:
                self.outpath += extension

            fourcc = cv2.VideoWriter_fourcc(*'MPEG')
            out = cv2.VideoWriter(self.outpath, fourcc, self.fps, tuple(self.imgSize))

            progressWindow = QDialog(self)

            hbox = QHBoxLayout()
            progressLabel = QLabel()
            progressLabel.setText("0 %")
            hbox.addWidget(progressLabel)

            progressBar = QProgressBar()
            progressBar.setRange(self.Range[0], self.Range[1] + 1 - self.Range[0])
            hbox.addWidget(progressBar)
            progressWindow.setLayout(hbox)

            progressWindow.show()

            for t in range(self.Range[0], self.Range[1] + 1):
                out.write(cv2.cvtColor(self.imgs[t], cv2.COLOR_RGB2BGR))

                progressBar.setValue(t)
                progressLabel.setText("{0} %".format(int((t + 1 - self.Range[0]) * 100 / (self.Range[1] + 1 - self.Range[0]))))
                QApplication.processEvents()

            progressWindow.close()

            out.release()


    def checkWriteAction(self):
        if self.Range[0] != -1 and self.Range[1] != -1 or not (self.Range[0] == 0 and self.Range[1] == self.frameMax - 1):
            self.write_action.setEnabled(True)
        else:
            self.write_action.setEnabled(False)

    # UI action
    def draw(self):
        if self.frame == -1:
            self.imageview.clear()
        else:
            img = self.imgs[self.frame]
            qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
            pixcelimg = QPixmap.fromImage(qimg)
            self.imageview.setPixmap(pixcelimg)

    def sliderValueChanged(self):
        self.frame = int(self.slider.value())
        self.labelFrame.setText("Frame Number: {0}".format(self.frame))
        self.update()
        self.draw()

    def play(self):
        self.timer.start(1000.0/self.fps)
        self.buttonPlay.setEnabled(False)
        self.buttonStop.setEnabled(True)

    def updateVideo(self):
        if self.frame < self.frameMax:
            self.frame += 1
            self.slider.setValue(self.frame)
        else:
            self.stop()

    def stop(self):
        self.timer.stop()
        self.buttonPlay.setEnabled(True)
        self.buttonStop.setEnabled(False)

    def spinFpsChanged(self):
        self.fps = float(self.spinFps.value())

    def keyPressEvent(self, QKeyEvent):
        if self.frame != -1:
            if QKeyEvent.key() == Qt.Key_I:
                self.Range[0] = self.frame
                self.labelCutUpdate()

            elif QKeyEvent.key() == Qt.Key_F:
                self.Range[1] = self.frame
                self.labelCutUpdate()

    def labelCutUpdate(self):
        self.labelCut.setText("{0} ~ {1}".format(self.Range[0], self.Range[1]))
        self.checkWriteAction()



    """
    def paintEvent(self, a0: QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        triangle = QPolygonF()

        self.slider.sliderPosition()
        x = self.slider.x() + int((self.slider.value() + 1)*self.slider.width()/self.frameMax)
        y = self.slider.y() + 10

        triangle.append(QPointF(x, y))
        triangle.append(QPointF(x-5, y+10))
        triangle.append(QPointF(x+5, y+10))

        painter.drawPolygon(triangle)

        painter.end()
    """
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoEditor()
    window.show()
    sys.exit(app.exec_())