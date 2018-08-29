import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np

class CutframeWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.cutmin = 0
        self.cutmax = self.parent.frame_max - 1
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)

        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        self.labelMin = QLabel(self)
        self.labelMin.setText("Minimum")
        hbox1.addWidget(self.labelMin)

        self.spinMin = QSpinBox(self)
        self.spinMin.setMaximum(self.parent.frame_max - 1)
        self.spinMin.setMinimum(0)
        self.spinMin.setValue(self.parent.frame)
        hbox1.addWidget(self.spinMin)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.labelMax = QLabel(self)
        self.labelMax.setText("Maximum")
        hbox2.addWidget(self.labelMax)

        self.spinMax = QSpinBox(self)
        self.spinMax.setMaximum(self.parent.frame_max - 1)
        self.spinMax.setMinimum(0)
        self.spinMax.setValue(self.parent.frame)
        hbox2.addWidget(self.spinMax)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.clickedOK)
        self.button_ok.setDefault(True)
        hbox3.addWidget(self.button_ok)

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.clickedCancel)
        hbox3.addWidget(self.button_cancel)
        vbox.addLayout(hbox3)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

    def clickedOK(self):
        self.cutmin = int(self.spinMin.text())
        self.cutmax = int(self.spinMax.text()) + 1

        # cut
        self.parent.frame_max = self.cutmax - self.cutmin
        self.parent.x = self.parent.x[self.cutmin:self.cutmax, :]
        self.parent.y = self.parent.y[self.cutmin:self.cutmax, :]
        self.parent.z = self.parent.z[self.cutmin:self.cutmax, :]
        #self.parent.label = self.parent.label[self.cutmin:self.cutmax]
        self.parent.xnew = self.parent.xnew[self.cutmin:self.cutmax, :]
        self.parent.ynew = self.parent.ynew[self.cutmin:self.cutmax, :]
        self.parent.znew = self.parent.znew[self.cutmin:self.cutmax, :]

        self.parent.xopt = self.parent.xopt[self.cutmin:self.cutmax, :]
        self.parent.yopt = self.parent.yopt[self.cutmin:self.cutmax, :]
        self.parent.zopt = self.parent.zopt[self.cutmin:self.cutmax, :]

        tmp_index_num = [np.sum(self.parent.x[i][self.parent.x[i] != 0]) for i in range(self.parent.frame_max)]

        self.parent.frame = np.argmax(tmp_index_num)

        self.parent.now_select = -1
        self.parent.trajectory_line = None

        self.parent.slider.setMaximum(self.parent.frame_max - 1)
        self.parent.slider.setValue(self.parent.frame)

        self.parent.draw(fix=True)

        self.parent.leftdockwidget.spininit.setMaximum(self.parent.frame_max - 1)
        self.parent.leftdockwidget.spinfin.setValue(self.parent.frame_max - 1)
        self.parent.leftdockwidget.spinfin.setMaximum(self.parent.frame_max - 1)

        self.close()

    def clickedCancel(self):
        self.close()


    def closeEvent(self, QCloseEvent):
        self.parent.setmenuEnabled("menuClick", True)

class ConfigureWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)

        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        self.labelfps = QLabel(self)
        self.labelfps.setText("fps")
        hbox1.addWidget(self.labelfps)

        self.spinFps = QSpinBox(self)
        self.spinFps.setMinimum(0)
        self.spinFps.setMaximum(10000)
        self.spinFps.setValue(self.parent.fps)
        hbox1.addWidget(self.spinFps)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.labelUnits = QLabel(self)
        self.labelUnits.setText("Units")
        hbox2.addWidget(self.labelUnits)

        self.comboBoxUnits = QComboBox(self)
        Units = ["mm", "cm", "m"]
        self.comboBoxUnits.addItems(Units)
        self.comboBoxUnits.setCurrentIndex(Units.index(self.parent.units))
        self.comboBoxUnits.currentIndexChanged.connect(self.unitsChanged)
        hbox2.addWidget(self.comboBoxUnits)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        self.labelSearchRange = QLabel(self)
        self.labelSearchRange.setText("Search Range({0})".format(self.parent.units))
        hbox3.addWidget(self.labelSearchRange)

        self.doublespinSearchRange = QDoubleSpinBox(self)
        self.doublespinSearchRange.setMinimum(0)
        self.doublespinSearchRange.setMaximum(1000)
        self.doublespinSearchRange.setValue(self.parent.searchRange)
        hbox3.addWidget(self.doublespinSearchRange)
        vbox.addLayout(hbox3)

        hbox4 = QHBoxLayout()
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.clickedOK)
        hbox4.addWidget(self.button_ok)

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.clickedCancel)
        hbox4.addWidget(self.button_cancel)
        vbox.addLayout(hbox4)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

    def unitsChanged(self):
        self.labelSearchRange.setText("Search Range({0})".format(str(self.comboBoxUnits.currentText())))

    def clickedOK(self):
        self.parent.fps = int(self.spinFps.text())
        self.parent.units = str(self.comboBoxUnits.currentText())
        self.parent.searchRange = float(self.doublespinSearchRange.text())

        self.close()

    def clickedCancel(self):
        self.close()


class RemoveWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)
        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        self.labelInit = QLabel(self)
        self.labelInit.setText("Init Frame")
        hbox1.addWidget(self.labelInit)

        self.spinInit = QSpinBox(self)
        self.spinInit.setMaximum(self.parent.frame_max - 1)
        self.spinInit.setMinimum(0)
        self.spinInit.setValue(self.parent.frame)
        hbox1.addWidget(self.spinInit)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.labelFin = QLabel(self)
        self.labelFin.setText("Fin Frame")
        hbox2.addWidget(self.labelFin)

        self.spinFin = QSpinBox(self)
        self.spinFin.setMaximum(self.parent.frame_max - 1)
        self.spinFin.setMinimum(0)
        self.spinFin.setValue(self.parent.frame)
        hbox2.addWidget(self.spinFin)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.clickedOK)
        self.button_ok.setDefault(True)
        hbox3.addWidget(self.button_ok)

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.clickedCancel)
        hbox3.addWidget(self.button_cancel)
        vbox.addLayout(hbox3)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

    def clickedOK(self):
        result = QMessageBox.warning(self, "Will you convert selected data into nan?", "This process can't revert latter",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == QMessageBox.Yes:
            if self.parent.leftdockwidget.radioorigin.isChecked():
                self.parent.convertZero(int(self.spinInit.text()), int(self.spinFin.text()) + 1)
            else:
                self.parent.convertNan(int(self.spinInit.text()), int(self.spinFin.text()) + 1)
        else:
            return

        self.close()

    def clickedCancel(self):
        self.close()

    def closeEvent(self, QCloseEvent):
        self.parent.setmenuEnabled("menuClick", True)
"""
class SetLabelforAuto(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)
        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        self.label = QLabel()
        self.label.setText("Joint")
        hbox1.addWidget(self.label)

        self.comboBoxLabel = QComboBox()
        self.comboBoxLabel.addItems(self.parent.Points)
        hbox1.addWidget(self.comboBoxLabel)

        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.clickedOK)
        self.button_ok.setDefault(True)
        hbox2.addWidget(self.button_ok)

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.clickedCancel)
        hbox2.addWidget(self.button_cancel)
        vbox.addLayout(hbox2)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)


    def clickedOK(self):
        self.parent.optimal_select('extrapolate', self.parent.now_select, self.parent.frame, str(self.comboBoxLabel.currentText()))

        self.close()

    def clickedCancel(self):
        self.close()

    def closeEvent(self, QCloseEvent):
        self.parent.setmenuEnabled("menuClick", True)
"""