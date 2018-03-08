# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2

class VideoListDockWidget(QWidget):
    def __init__(self, parent):
        super(VideoListDockWidget, self).__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        self.delbutton = QPushButton("削除", self)
        self.delbutton.clicked.connect(self.remove)
        self.detailbutton = QPushButton("拡大", self)
        self.detailbutton.clicked.connect(self.expand)

        hbox.addWidget(self.delbutton)
        hbox.addWidget(self.detailbutton)
        vbox.addLayout(hbox)

        self.slidertreeview = SliderTreeView(self)
        vbox.addWidget(self.slidertreeview)

        self.setLayout(vbox)

    def remove(self):
        rows = self.selectedRows()
        self.slidertreeview.delete_item(rows)
        self.parent.remove_video(rows)

    def expand(self):
        rows = self.selectedRows()
        if len(rows) == 0:
            rows = range(len(self.parent.data))
        self.parent.showimage(rows)

    def add(self, videopath, frame_now):
        self.slidertreeview.set_item(videopath, frame_now)

    #def frame(self, index):
     #   return self.parent.data[index]["now"]

    def selectedRows(self):
        rows = []
        for index in self.slidertreeview.selectedIndexes():
            if index.column() == 0:
                rows.append(index.row())
        return rows

    def sliderchanged(self, value):
        Slider = self.sender()
        for i, slider in enumerate(self.slidertreeview.sliders):
            if slider == Slider:
                self.parent.data[i]["now"] = value
                self.expand()
                self.slidertreeview.sliderchanged(i, value)
                break

    def next_slidervalue(self, index):
        self.slidertreeview.sliders[index].setValue(self.parent.data[index]["now"])



class SliderTreeView(QTreeView):
    def __init__(self, parent=None):
        super(SliderTreeView, self).__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self):
        self._datamodel = QStandardItemModel(0, 3)
        self._datamodel.setHeaderData(0, Qt.Horizontal, 'video name')
        self._datamodel.setHeaderData(1, Qt.Horizontal, 'frame/total')
        self._datamodel.setHeaderData(2, Qt.Horizontal, 'slider')
        self.setModel(self._datamodel)

        self.items = []
        self.sliders = []

        #self.model = Model()
        #self.setModel(self.model)
        self.setIndentation(0)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)


    def set_item(self, videopath, frame_now):
        video = cv2.VideoCapture(videopath.encode('utf-8'))
        tmp = videopath.split('/')
        item = { "name":tmp[len(tmp) - 1], "frame_max":int(video.get(cv2.CAP_PROP_FRAME_COUNT))}
        index = len(self.items)
        self.items.append(item)

        videoname = QStandardItem(self.items[index]["name"])
        self._datamodel.setItem(index, 0, videoname)

        frame = QStandardItem(str(frame_now + 1) + '/' + str(self.items[index]["frame_max"]))
        self._datamodel.setItem(index, 1, frame)

        slider = QSlider(Qt.Horizontal, self)
        slider.setRange(0, self.items[index]["frame_max"] - 1)
        slider.setValue(0)
        slider.setFocusPolicy(Qt.NoFocus)
        # slider.valueChanged[int].connect(self.parent.sliderchanged)
        slider.valueChanged[int].connect(self.parent.sliderchanged)
        index = self._datamodel.index(index, 2, QModelIndex())
        self.setIndexWidget(index, slider)
        self.sliders.append(slider)

        #self.update_list()

    def delete_item(self, rowIndexes):
        for row in sorted(rowIndexes, reverse=True):
            self._datamodel.removeRow(row)
            del self.items[row]
            del self.sliders[row]

    def sliderchanged(self, index, value):
        frame = QStandardItem(str(value + 1) + '/' + str(self.items[index]["frame_max"]))
        self._datamodel.setItem(index, 1, frame)
