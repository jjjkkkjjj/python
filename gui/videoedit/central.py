# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2


# テキストフォーム中心の画面のためQMainWindowを継承する
class VideoDisplayWidget(QWidget):
    def __init__(self,parent):
        super(VideoDisplayWidget, self).__init__(parent)
        self.parent = parent
        #self.layout = QFormLayout(self)
        hbox = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()

        # show widget
        self.startButton = QPushButton('Start', parent)
        self.startButton.clicked.connect(parent.start_button_clicked)
        hbox.addWidget(self.startButton)

        self.pauseButton = QPushButton('Pause', parent)
        self.pauseButton.clicked.connect(parent.pause_button_clicked)
        hbox.addWidget(self.pauseButton)
        vbox.addLayout(hbox)

        self.video_label = QLabel()
        vbox.addWidget(self.video_label)

        self.checkbox_connect = QCheckBox('Connect', parent)
        self.checkbox_connect.setChecked(True)
        hbox2.addWidget(self.checkbox_connect)
        self.checkbox_overlay = QCheckBox('Overlay', parent)
        self.checkbox_overlay.setChecked(True)
        hbox2.addWidget(self.checkbox_overlay)
        self.savebutton = QPushButton('save', parent)
        self.savebutton.clicked.connect(parent.savevideo)
        hbox2.addWidget(self.savebutton)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

        self.timer = QTimer()

    def draw(self, img=None):
        if img is None:
            self.video_label.clear()
        else:
            qimg = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
            pixcelimg = QPixmap.fromImage(qimg)
            self.video_label.setPixmap(pixcelimg)

    def setprogressvalue(self, i):
        self.progressbar.setValue(i)
        QApplication.processEvents()

    def finishprogress(self):
        self.window.close()

    def show_progressbar(self, frame_num):
        self.window = QDialog(self.parent)
        self.progressbar = QProgressBar(self.parent)
        self.progressbar.setRange(0, frame_num)
        layout = QHBoxLayout()
        layout.addWidget(self.progressbar)
        self.window.setLayout(layout)
        self.window.show()