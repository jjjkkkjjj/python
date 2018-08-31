import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import csv

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

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return:
            self.clickedOK()

    def closeEvent(self, QCloseEvent):
        self.parent.setmenuEnabled("menuClick", True)

class ConfigureWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)

        VBOX = QVBoxLayout()

        self.groupBasicInfo = QGroupBox("Basic Info")
        vboxBasicInfo = QVBoxLayout()

        hbox1 = QHBoxLayout()
        self.labelfps = QLabel(self)
        self.labelfps.setText("fps")
        hbox1.addWidget(self.labelfps)

        self.spinFps = QSpinBox(self)
        self.spinFps.setMinimum(0)
        self.spinFps.setMaximum(10000)
        self.spinFps.setValue(self.parent.fps)
        hbox1.addWidget(self.spinFps)
        vboxBasicInfo.addLayout(hbox1)

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
        vboxBasicInfo.addLayout(hbox2)

        self.groupBasicInfo.setLayout(vboxBasicInfo)
        VBOX.addWidget(self.groupBasicInfo)

        self.groupOptimalSelection = QGroupBox("Optimal Selection")
        vboxOptimalSelection = QVBoxLayout()

        hbox3 = QHBoxLayout()
        self.labelSearchRange = QLabel(self)
        self.labelSearchRange.setText("Threshold for optimal selection({0})".format(self.parent.units))
        hbox3.addWidget(self.labelSearchRange)

        self.doublespin_Threshold_optimal = QDoubleSpinBox(self)
        self.doublespin_Threshold_optimal.setMinimum(0)
        self.doublespin_Threshold_optimal.setMaximum(1000)
        self.doublespin_Threshold_optimal.setValue(self.parent.Threshold_optimal)
        hbox3.addWidget(self.doublespin_Threshold_optimal)
        vboxOptimalSelection.addLayout(hbox3)

        self.groupOptimalSelection.setLayout(vboxOptimalSelection)
        VBOX.addWidget(self.groupOptimalSelection)

        self.groupAutolabeling = QGroupBox("Auto Labeling")
        vboxAutolabeling = QVBoxLayout()

        hbox4 = QHBoxLayout()
        self.labelStandardJoints = QLabel(self)
        self.labelStandardJoints.setText("Standard Joint for auto-labeling")
        hbox4.addWidget(self.labelStandardJoints)

        self.comboBoxJoints = QComboBox(self)
        self.comboBoxJoints.addItems(self.parent.Points)
        self.comboBoxJoints.setCurrentIndex(self.parent.Points.index(self.parent.StandardJoint_autolabeling))
        hbox4.addWidget(self.comboBoxJoints)
        vboxAutolabeling.addLayout(hbox4)

        labelPath = QLabel(self)
        labelPath.setText("Path as standard:")
        vboxAutolabeling.addWidget(labelPath)
        self.labelDefaultTrcPath = QLabel(self)
        self.labelDefaultTrcPath.setText(self.parent.DefaultTrcPath_autolabeling)
        vboxAutolabeling.addWidget(self.labelDefaultTrcPath)
        self.button_open = QPushButton("Open", self)
        self.button_open.clicked.connect(self.clickedOpen)
        vboxAutolabeling.addWidget(self.button_open)

        hbox5 = QHBoxLayout()
        self.labelStandardFrame = QLabel(self)
        self.labelStandardFrame.setText("Standard Frame")
        hbox5.addWidget(self.labelStandardFrame)

        self.spinStandardFrame = QSpinBox(self)
        self.spinStandardFrame.setMinimum(-1)
        self.spinStandardFrame.setMaximum(self.readTrc(self.parent.DefaultTrcPath_autolabeling))
        self.spinStandardFrame.setValue(self.parent.StandardFrame_autolabeling)
        hbox5.addWidget(self.spinStandardFrame)
        vboxAutolabeling.addLayout(hbox5)

        self.groupAutolabeling.setLayout(vboxAutolabeling)
        VBOX.addWidget(self.groupAutolabeling)

        hbox6 = QHBoxLayout()
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.clickedOK)
        hbox6.addWidget(self.button_ok)

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.clickedCancel)
        hbox6.addWidget(self.button_cancel)
        VBOX.addLayout(hbox6)

        self.main_widget.setLayout(VBOX)
        self.setCentralWidget(self.main_widget)

    def unitsChanged(self):
        self.labelSearchRange.setText("Search Range({0})".format(str(self.comboBoxUnits.currentText())))

    def clickedOpen(self):
        filters = "TRC files(*.trc)"
        path = unicode(QFileDialog.getOpenFileName(self, 'load file', './data/c3d', filters))

        try:
            if path:
                self.labelDefaultTrcPath.setText(path)
                maxFrame = self.readTrc(path)
                self.spinStandardFrame.setMaximum(maxFrame)
            else:
                pass
        except:
            pass

    def readTrc(self, path):
        try:
            with open(path, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                next(reader)
                next(reader)
                next(reader)
                next(reader)

                data = np.genfromtxt(f, delimiter='\t', skip_header=6, missing_values=' ')
                x = data[:, 2::3]
                y = data[:, 3::3]
                z = data[:, 4::3]
                frame_max = x.shape[0]

                self.spinStandardFrame.setMinimum(0)
                return frame_max
        except:
            return -1

    def clickedOK(self):
        self.parent.fps = int(self.spinFps.text())
        self.parent.units = str(self.comboBoxUnits.currentText())
        self.parent.Threshold_optimal = float(self.doublespin_Threshold_optimal.text())

        self.parent.StandardJoint_autolabeling = str(self.comboBoxJoints.currentText())
        self.parent.DefaultTrcPath_autolabeling = str(self.labelDefaultTrcPath.text())
        self.parent.StandardFrame_autolabeling = int(self.spinStandardFrame.value())

        self.close()

    def clickedCancel(self):
        self.close()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return:
            self.clickedOK()

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

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return:
            self.clickedOK()

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