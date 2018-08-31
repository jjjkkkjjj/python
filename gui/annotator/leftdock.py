from PyQt4.QtCore import *
from PyQt4.QtGui import *

class LeftDockWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent

        self.initUI()

    def initUI(self):
        VBOX = QVBoxLayout(self)

        # annotator
        self.groupAnnotator = QGroupBox("Annotator")
        vboxannotator = QVBoxLayout()
        # label
        self.selectedlabel = QLabel()
        self.selectedlabel.setText("No Label")
        vboxannotator.addWidget(self.selectedlabel)

        # selector
        self.selectedcombobox = QComboBox()
        self.selectedcombobox.addItem("No Label")
        self.selectedcombobox.addItems(self.parent.Points)
        self.selectedcombobox.currentIndexChanged.connect(self.changeComboBox)
        vboxannotator.addWidget(self.selectedcombobox)

        # configure
        self.radio1frame = QRadioButton("Only one frame")
        self.radio1frame.setEnabled(True)
        self.radio1frame.toggled.connect(self.radio1frameChanged)
        vboxannotator.addWidget(self.radio1frame)

        self.radioUntilNan = QRadioButton("Interplate nan")
        self.radioUntilNan.setChecked(True)
        self.radioUntilNan.setEnabled(True)
        vboxannotator.addWidget(self.radioUntilNan)

        self.groupsetting = QGroupBox("Setting")
        vboxsetting = QVBoxLayout()
        hbox = QHBoxLayout()
        self.labelinit = QLabel()
        self.labelinit.setText("Init frame")
        hbox.addWidget(self.labelinit)

        self.spininit = QSpinBox()
        # self.spininit.setMaximum(self.parent.frame_max - 1)
        self.spininit.setMinimum(0)
        self.spininit.setValue(0)
        hbox.addWidget(self.spininit)
        vboxsetting.addLayout(hbox)

        hbox2 = QHBoxLayout()
        self.labelfin = QLabel()
        self.labelfin.setText("Fin frame")
        hbox2.addWidget(self.labelfin)

        self.spinfin = QSpinBox()
        # self.spininit.setMaximum(self.parent.frame_max - 1)
        self.spinfin.setMinimum(0)
        self.spinfin.setValue(1)
        hbox2.addWidget(self.spinfin)
        vboxsetting.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        self.labelinterpolation = QLabel()
        self.labelinterpolation.setText("Interpolation")
        hbox3.addWidget(self.labelinterpolation)

        self.comboboxinterpolation = QComboBox()
        Interpolations = ["Linear", "Spline"]
        self.comboboxinterpolation.addItems(Interpolations)
        self.comboboxinterpolation.setCurrentIndex(0)
        hbox3.addWidget(self.comboboxinterpolation)
        vboxsetting.addLayout(hbox3)

        self.groupsetting.setLayout(vboxsetting)
        vboxannotator.addWidget(self.groupsetting)

        # enter button
        self.button_setlabel = QPushButton("Set Label")
        self.button_setlabel.setEnabled(False)
        self.button_setlabel.clicked.connect(self.setLabel)
        vboxannotator.addWidget(self.button_setlabel)

        # delete label
        #self.button_deletelabel = QPushButton("Delete Label")
        #self.button_deletelabel.setEnabled(False)
        #self.button_deletelabel.clicked.connect(self.deleteLabel)
        #vboxannotator.addWidget(self.button_deletelabel)

        self.groupAnnotator.setLayout(vboxannotator)
        self.groupAnnotator.setEnabled(False)

        # viewer
        self.groupViewer = QGroupBox("Viewer")
        vboxviewer = QVBoxLayout()

        self.check_trajectory = QCheckBox("trajectory", self)
        self.check_trajectory.toggled.connect(self.show_trajectory_child)
        vboxviewer.addWidget(self.check_trajectory)

        self.button_noselect = QPushButton("Release", self)
        self.button_noselect.clicked.connect(self.release_select)
        self.button_noselect.setEnabled(False)
        vboxviewer.addWidget(self.button_noselect)

        self.check_showbone = QCheckBox("Show Bone", self)
        self.check_showbone.toggled.connect(self.check_showboneChanged)
        self.check_showbone.setEnabled(False)
        vboxviewer.addWidget(self.check_showbone)

        self.groupshowradio = QGroupBox("Data type")
        vboxshowradio = QVBoxLayout()
        self.radioorigin = QRadioButton("Original")
        vboxshowradio.addWidget(self.radioorigin)

        self.radioauto = QRadioButton("Auto")
        self.radioauto.toggled.connect(self.radioautoChanged)
        vboxshowradio.addWidget(self.radioauto)

        self.radiolabeled = QRadioButton("Labeled")
        self.radiolabeled.toggled.connect(self.radiolabeledChanged)
        vboxshowradio.addWidget(self.radiolabeled)

        self.groupshowradio.setLayout(vboxshowradio)
        self.radioorigin.setChecked(True)

        vboxviewer.addWidget(self.groupshowradio)

        self.groupViewer.setLayout(vboxviewer)

        VBOX.addWidget(self.groupAnnotator)
        VBOX.addWidget(self.groupViewer)

        self.setLayout(VBOX)

    # clicked trajectory checkbox
    def show_trajectory_child(self):
        if self.check_trajectory.isChecked():
            self.parent.show_trajectory()
        else:
            self.parent.trajectory_line = None
            self.parent.draw(fix=True)

    # clicked release button
    def release_select(self):
        self.parent.now_select = -1
        self.parent.trajectory_line = None
        self.onclicked_Enabled(False)
        self.parent.setFrameLabel()
        self.parent.draw(fix=True)

    # clicked set Label button
    def setLabel(self):
        if self.radioorigin.isChecked() or self.radioauto.isChecked():
            var = {}
            var["label"] = str(self.selectedcombobox.currentText())
            if self.radioUntilNan.isChecked():
                var["init"] = int(self.spininit.text())
                var["fin"] = int(self.spinfin.text())
                var["interpolation"] = str(self.comboboxinterpolation.currentText())
            self.parent.setLabel(var, self.radioUntilNan.isChecked(), self.radioauto.isChecked())
            self.parent.setFrameLabel()
        else:
            self.parent.deleteLabel()
            self.parent.draw(fix=True)

    # clicked show bone
    #def showbone(self):
    #    self.parent.setbone()
    #    self.parent.draw(fix=True)

    def check_showboneChanged(self):
        self.parent.draw(fix=True)

    # change label combobox
    def changeComboBox(self):
        if self.selectedcombobox.currentText() == "No Label":
            self.button_setlabel.setEnabled(False)
        else:
            self.button_setlabel.setEnabled(True)

    # function for leaving off to change enabled
    def onclicked_Enabled(self, BOOL):
        self.button_noselect.setEnabled(BOOL)
        self.groupAnnotator.setEnabled(BOOL)
        self.parent.setmenuEnabled("click", BOOL)

    def radio1frameChanged(self):
        if self.radio1frame.isChecked():
            self.groupsetting.setEnabled(False)
        else:
            self.groupsetting.setEnabled(True)

    def radiolabeledChanged(self):
        if self.radiolabeled.isChecked():
            self.check_showbone.setEnabled(True)
            self.selectedcombobox.setVisible(False)
            self.labelinterpolation.setVisible(False)
            self.comboboxinterpolation.setVisible(False)
            self.radioUntilNan.setText("Select deleted frames")
            self.button_setlabel.setText("Delete Label")
        else:
            self.check_showbone.setEnabled(False)
            self.selectedcombobox.setVisible(True)
            self.labelinterpolation.setVisible(True)
            self.comboboxinterpolation.setVisible(True)
            self.radioUntilNan.setText("Interpolate nan")
            self.button_setlabel.setText("Set Label")

        self.parent.now_select = -1
        self.parent.setmenuEnabled("click", False)
        self.parent.trajectory_line = None
        self.groupAnnotator.setEnabled(False)
        self.parent.draw(fix=True)


    def radioautoChanged(self):
        if self.radiolabeled.isChecked():
            self.check_showbone.setEnabled(True)
            self.selectedcombobox.setVisible(False)
            self.labelinterpolation.setVisible(False)
            self.comboboxinterpolation.setVisible(False)
            self.radioUntilNan.setText("Select deleted frames")
            self.button_setlabel.setText("Delete Label")
        else:
            self.check_showbone.setEnabled(False)
            self.selectedcombobox.setVisible(True)
            self.labelinterpolation.setVisible(True)
            self.comboboxinterpolation.setVisible(True)
            self.radioUntilNan.setText("Interpolate nan")
            self.button_setlabel.setText("Set Label")

        self.parent.now_select = -1
        self.parent.setmenuEnabled("click", False)
        self.parent.trajectory_line = None
        self.groupAnnotator.setEnabled(False)
        self.parent.draw(fix=True)