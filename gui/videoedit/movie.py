# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QLabel, QMessageBox,
    QAction, QFileDialog, QApplication, QWidget, QFormLayout, QPushButton)
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2

from a import video


class FaderWidget(QWidget):
    def __init__(self, old_widget, new_widget):
        QWidget.__init__(self, new_widget)

        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(333)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


class VideoCapture(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.video_label = QLabel()
        parent.layout.addWidget(self.video_label)
        self.ret = False
        self.img = None
        self.timer = QTimer()

    def set_video(self, filename):
        self.video = cv2.VideoCapture(filename.encode('utf-8'))
        self.ret = True

    def next_frame(self):
        self.ret, self.img = self.video.read()
        if self.ret:
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            qimg = QImage(self.img, self.img.shape[1], self.img.shape[0], QImage.Format_RGB888)
            pixcel = QPixmap.fromImage(qimg)
            self.video_label.setPixmap(pixcel)
        else:
            self.timer.stop()

    def start(self):
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(10)  # ミリ秒単位

    def deleteLater(self):
        #self.cap.release()
        super(QWidget, self).deleteLater()


# テキストフォーム中心の画面のためQMainWindowを継承する
class VideoDisplayWidget(QWidget):
    def __init__(self,parent):
        super(VideoDisplayWidget, self).__init__(parent)

        self.layout = QFormLayout(self)

        self.startButton = QPushButton('Start', parent)
        #self.startButton.clicked.connect(parent.startCapture)
        self.startButton.setFixedWidth(50)
        self.pauseButton = QPushButton('Pause', parent)
        self.pauseButton.setFixedWidth(50)
        self.layout.addRow(self.startButton, self.pauseButton)

        self.setLayout(self.layout)

class Example(QMainWindow):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()


    def initUI(self):

        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        # メニューバーのアイコン設定
        openFile = QAction('Open', self)
        # ショートカット設定
        openFile.setShortcut('Ctrl+O')
        # ステータスバー設定
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        quitapplication = QAction('quit', self)
        quitapplication.setShortcut('Ctrl+Q')
        quitapplication.setStatusTip('Close The App')
        quitapplication.triggered.connect(self.quit)

        # メニューバー作成
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(quitapplication)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.Videowidget = VideoDisplayWidget(self)
        self.setCentralWidget(self.Videowidget)
        self.Video = None
        self.show()



    def showDialog(self):

        # 第二引数はダイアログのタイトル、第三引数は表示するパス
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

        # fname[0]は選択したファイルのパス（ファイル名を含む）
        if fname[0]:
            if self.Video == None:
                self.Video = VideoCapture(self.Videowidget)
            self.Video.set_video(fname[0])
            self.Video.start()

            """
            # ファイル読み込み
            f = open(fname[0], 'r')

            # テキストエディタにファイル内容書き込み
            with f:
                data = f.read()
                self.textEdit.setText(data)
                """
    def quit(self):
        choice = QMessageBox.question(self, 'Message', 'Do you really want to exit?', QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def stop_timer(self):
        self.timer.stop()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Example()
    window.show()
    sys.exit(app.exec_())