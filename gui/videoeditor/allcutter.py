# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import glob
import numpy as np
import os
import copy

class VideoEditor(QMainWindow):
    def __init__(self):
        super(VideoEditor, self).__init__()

        self.imgSize = [400, 300]
        self.videonum = -1
        self.videopaths = []
        self.fpses = []
        self.frames = []
        self.frameMaxes = []
        self.videos = []

        self.Ranges = []
        self.extensions = ["mp4", "m4v", "avi"]

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

        self.labelVideopath = QLabel()
        self.labelVideopath.setText("Video: -1")
        vbox.addWidget(self.labelVideopath)

        hbox = QHBoxLayout()

        self.labelFrame = QLabel()
        self.labelFrame.setText("Frame Number: -1")
        hbox.addWidget(self.labelFrame)

        self.labelCut = QLabel()
        self.labelCut.setText("-1 ~ -1")
        hbox.addWidget(self.labelCut)

        self.spinFps = QDoubleSpinBox()
        self.spinFps.setMaximum(10000)
        self.spinFps.setMinimum(1)
        self.spinFps.setValue(50)
        self.spinFps.valueChanged.connect(self.spinFpsChanged)
        self.spinFps.setFocusPolicy(Qt.ClickFocus)
        hbox.addWidget(self.spinFps)
        vbox.addLayout(hbox)

        self.imageview = QLabel()
        self.imageview.setFixedSize(self.imgSize[0], self.imgSize[1])
        vbox.addWidget(self.imageview)


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
        #filters = "MP4 files(*.mp4||*.MP4);;M4V files(*.m4v);;AVI files(*.avi)"
        #selected_filter = "MP4 files(*.mp4)"

        self.path = QFileDialog.getExistingDirectory(self, 'load directory', '')

        if self.path != "":
            extensiondialog = ReadExtensionDialog(self)
            extensiondialog.setWindowModality(Qt.ApplicationModal)

            extensiondialog.show()


            """
                        if extensiondialog.extension == "":
                return
            elif extensiondialog.extension == "MP4":
                self.videopaths.extend(sorted(glob.glob(self.path + "/*.MP4")))
                self.videopaths.extend(sorted(glob.glob(self.path + "/*.mp4")))
            elif extensiondialog.extension == "M4V":
                self.videopaths.extend(sorted(glob.glob(self.path + "/*.m4v")))
                self.videopaths.extend(sorted(glob.glob(self.path + "/*.M4V")))
            elif extensiondialog.extension == "AVI":
                self.videopaths.extend(sorted(glob.glob(self.path + "/*.AVI")))
                self.videopaths.extend(sorted(glob.glob(self.path + "/*.avi")))

            if len(self.videopaths) == 0:
                return
            progressWindow = QDialog(self)

            hbox = QHBoxLayout()
            progressLabel = QLabel()
            progressLabel.setText("0 %")
            hbox.addWidget(progressLabel)

            progressBar = QProgressBar()
            progressBar.setRange(0, len(self.videopaths))
            hbox.addWidget(progressBar)
            progressWindow.setLayout(hbox)

            progressWindow.show()
            progressBar.setValue(0)
            progressLabel.setText("0 %")
            QApplication.processEvents()

            for i, path in enumerate(self.videopaths):
                video = cv2.VideoCapture(path)
                self.videos.append(video)
                self.fpses.append(video.get(cv2.CAP_PROP_FPS))
                self.frames.append(0)
                self.frameMaxes.append(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))
                self.Ranges.append([0, int(video.get(cv2.CAP_PROP_FRAME_COUNT)) - 1])

                #imgs = []
                #for t in range(self.frameMaxes[i]):
                #    ret, img = video.read()
                #    imgs.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), tuple(self.imgSize)))

                #self.imgs.append(imgs)

                #video.release()
                progressBar.setValue(i + 1)
                progressLabel.setText("{0} %".format(int((i + 1)*100/len(self.videopaths))))
                QApplication.processEvents()

            progressWindow.close()

            self.videonum = 0
            self.videoUpdate()

            self.slider.setEnabled(True)
            """

        else:
            msg = """You should select video file!"""
            QMessageBox.about(self, "Caution", msg.strip())
        pass

    def writeVideo(self):
        #filters = "MP4 files(*.mp4);;M4V files(*.m4v);;AVI files(*.avi)"
        #selected_filter = "MP4 files(*.mp4)"
        self.outpath = QFileDialog.getExistingDirectory(self, 'save directory', '')

        if self.outpath != "":
            extensiondialog = WriteExtensionDialog(self)
            extensiondialog.setWindowModality(Qt.ApplicationModal)

            extensiondialog.show()
            """
                        if extensiondialog.extension == "":
                return

            extension = extensiondialog.extension

            if extension == "MP4":
                fourcc = cv2.VideoWriter_fourcc(*'MPEG')
            elif extension == "M4V":
                fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            elif  extension == "AVI":
                fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'MPEG')


            progressWindow = QDialog(self)

            hbox = QHBoxLayout()
            progressLabel = QLabel()
            progressLabel.setText("0 %")
            hbox.addWidget(progressLabel)

            progressBar = QProgressBar()
            progressBar.setRange(1, len(self.videopaths))
            hbox.addWidget(progressBar)
            progressWindow.setLayout(hbox)

            progressWindow.show()

            if self.outpath[-4:] != extension:
                self.outpath += extension

            for i, path in enumerate(self.videopaths):
                outpath = path[:-4] + "-cut." + extension

                size = (int(self.videos[self.videonum].get(cv2.CAP_PROP_FRAME_HEIGHT)),
                        int(self.videos[self.videonum].get(cv2.CAP_PROP_FRAME_WIDTH)))
                out = cv2.VideoWriter(outpath, fourcc, self.fpses[self.videonum], size)

                for t in range(self.Ranges[self.videonum][0], self.Ranges[self.videonum][1] + 1):
                    self.videos[self.videonum].set(cv2.CAP_PROP_POS_FRAMES, t)
                    ret, img = self.videos[self.videonum].read()
                    out.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

                out.release()

                progressBar.setValue(i + 1)
                progressLabel.setText("{0} %".format(int((i + 1) * 100 / len(self.videopaths))))
                QApplication.processEvents()

            progressWindow.close()
            """


    # UI action
    def draw(self):
        if self.frames[self.videonum] == -1:
            self.imageview.clear()
        else:
            self.videos[self.videonum].set(cv2.CAP_PROP_POS_FRAMES, self.frames[self.videonum])
            ret, img = self.videos[self.videonum].read()

            img = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), tuple(self.imgSize))
            #img = self.imgs[self.videonum][self.frames[self.videonum]]
            qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
            pixcelimg = QPixmap.fromImage(qimg)
            self.imageview.setPixmap(pixcelimg)

    def videoUpdate(self):
        self.slider.setMaximum(self.frameMaxes[self.videonum] - 1)
        self.slider.setValue(self.frames[self.videonum])

        self.spinFps.setValue(self.fpses[self.videonum])

        self.labelCutUpdate()
        self.draw()

    def sliderValueChanged(self):
        self.frames[self.videonum] = int(self.slider.value())
        self.labelFrame.setText("Frame Number: {0}".format(self.frames[self.videonum]))
        self.draw()

    def spinFpsChanged(self):
        self.fpses[self.videonum] = float(self.spinFps.value())

    def keyPressEvent(self, QKeyEvent):
        if len(self.frames) != 0:
            if QKeyEvent.key() == Qt.Key_I:
                self.Ranges[self.videonum][0] = self.frames[self.videonum]
                self.labelCutUpdate()

            elif QKeyEvent.key() == Qt.Key_F:
                self.Ranges[self.videonum][1] = self.frames[self.videonum]
                self.labelCutUpdate()

            elif QKeyEvent.key() == Qt.Key_N:
                if self.videonum != len(self.frames) - 1:
                    self.videonum += 1
                    self.videoUpdate()

            elif QKeyEvent.key() == Qt.Key_P:
                if self.videonum != 0:
                    self.videonum += -1
                    self.videoUpdate()

    def labelCutUpdate(self):
        self.labelVideopath.setText("Video: {0}".format(self.videopaths[self.videonum]))
        self.labelCut.setText("{0} ~ {1}".format(self.Ranges[self.videonum][0], self.Ranges[self.videonum][1]))

    def close(self):
        for video in self.videos:
            video.release()


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

class ReadExtensionDialog(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent

        self.parent.videonum = -1
        self.parent.videopaths = []
        self.parent.fpses = []
        self.parent.frames = []
        self.parent.frameMaxes = []
        self.parent.videos = []

        self.parent.Ranges = []
        self.extension = ""

        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)

        vbox = QVBoxLayout()
        self.comboboxExtension = QComboBox()
        self.comboboxExtension.addItems(self.parent.extensions)
        self.comboboxExtension.setCurrentIndex(0)
        vbox.addWidget(self.comboboxExtension)

        hbox = QHBoxLayout()
        self.buttonCancel = QPushButton("Cancel")
        self.buttonCancel.clicked.connect(self.cancelClicked)
        hbox.addWidget(self.buttonCancel)

        self.buttonOK = QPushButton("OK")
        self.buttonOK.clicked.connect(self.okClicked)
        hbox.addWidget(self.buttonOK)
        vbox.addLayout(hbox)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

    def cancelClicked(self):
        self.close()

    def okClicked(self):
        self.extension = str(self.comboboxExtension.currentText())

        if self.extension == "mp4":
            self.parent.videopaths.extend(sorted(glob.glob(self.parent.path + "/*.MP4")))
            self.parent.videopaths.extend(sorted(glob.glob(self.parent.path + "/*.mp4")))
        elif self.extension == "m4v":
            self.parent.videopaths.extend(sorted(glob.glob(self.parent.path + "/*.m4v")))
            self.parent.videopaths.extend(sorted(glob.glob(self.parent.path + "/*.M4V")))
        elif self.parent.extension == "avi":
            self.parent.videopaths.extend(sorted(glob.glob(self.parent.path + "/*.AVI")))
            self.parent.videopaths.extend(sorted(glob.glob(self.parent.path + "/*.avi")))

        if len(self.parent.videopaths) == 0:
            self.close()

        self.parent.write_action.setEnabled(True)
        progressWindow = QDialog(self)

        hbox = QHBoxLayout()
        progressLabel = QLabel()
        progressLabel.setText("0 %")
        hbox.addWidget(progressLabel)

        progressBar = QProgressBar()
        progressBar.setRange(0, len(self.parent.videopaths))
        hbox.addWidget(progressBar)
        progressWindow.setLayout(hbox)

        progressWindow.show()
        progressBar.setValue(0)
        progressLabel.setText("0 %")
        QApplication.processEvents()

        for i, path in enumerate(self.parent.videopaths):
            video = cv2.VideoCapture(path)
            self.parent.videos.append(video)
            self.parent.fpses.append(video.get(cv2.CAP_PROP_FPS))
            self.parent.frames.append(0)
            self.parent.frameMaxes.append(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))
            self.parent.Ranges.append([0, int(video.get(cv2.CAP_PROP_FRAME_COUNT)) - 1])

            # imgs = []
            # for t in range(self.frameMaxes[i]):
            #    ret, img = video.read()
            #    imgs.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), tuple(self.imgSize)))

            # self.imgs.append(imgs)

            # video.release()
            progressLabel.setText("{0} %".format(int((i + 1) * 100 / len(self.parent.videopaths))))
            progressBar.setValue(i + 1)
            QApplication.processEvents()

        progressWindow.close()

        self.parent.videonum = 0
        self.parent.videoUpdate()

        self.parent.slider.setEnabled(True)
        self.close()

class WriteExtensionDialog(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent

        self.extension = ""

        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)

        vbox = QVBoxLayout()
        self.comboboxExtension = QComboBox()
        self.comboboxExtension.addItems(self.parent.extensions)
        self.comboboxExtension.setCurrentIndex(0)
        vbox.addWidget(self.comboboxExtension)

        hbox = QHBoxLayout()
        self.buttonCancel = QPushButton("Cancel")
        self.buttonCancel.clicked.connect(self.cancelClicked)
        hbox.addWidget(self.buttonCancel)

        self.buttonOK = QPushButton("OK")
        self.buttonOK.clicked.connect(self.okClicked)
        hbox.addWidget(self.buttonOK)
        vbox.addLayout(hbox)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

    def cancelClicked(self):
        self.close()

    def okClicked(self):
        self.extension = str(self.comboboxExtension.currentText())

        if self.extension == "mp4":
            fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        elif self.extension == "m4v":
            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        elif self.extension == "avi":
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'MPEG')

        progressWindow = QDialog(self)

        hbox = QHBoxLayout()
        progressLabel = QLabel()
        progressLabel.setText("0 %")
        hbox.addWidget(progressLabel)

        progressBar = QProgressBar()
        progressBar.setRange(0, len(self.parent.videopaths))
        hbox.addWidget(progressBar)
        progressWindow.setLayout(hbox)

        progressWindow.show()

        for i, path in enumerate(self.parent.videopaths):
            outpath = self.parent.outpath + "/" + path.split('/')[-1][:-4] + "-cut." + self.extension

            size = (int(self.parent.videos[self.parent.videonum].get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self.parent.videos[self.parent.videonum].get(cv2.CAP_PROP_FRAME_HEIGHT)))
            out = cv2.VideoWriter(outpath, fourcc, self.parent.fpses[self.parent.videonum], size)

            self.parent.videos[self.parent.videonum].set(cv2.CAP_PROP_POS_FRAMES, self.parent.Ranges[self.parent.videonum][0])
            for t in range(self.parent.Ranges[self.parent.videonum][0], self.parent.Ranges[self.parent.videonum][1] + 1):
                ret, img = self.parent.videos[self.parent.videonum].read()
                out.write(img)

            out.release()

            progressLabel.setText("{0} %".format(int((i + 1) * 100 / len(self.parent.videopaths))))
            progressBar.setValue(i + 1)
            QApplication.processEvents()

        progressWindow.close()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoEditor()
    window.show()
    sys.exit(app.exec_())