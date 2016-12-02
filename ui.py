import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
 


class Window(QMainWindow):
    
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.build()
        self.show()
        
    def build(self):
        self.main_window()
        self.statusbar()
        self.menubar()
        
    def main_window(self):
        self.setWindowTitle("Wafer Probing")
        self.setGeometry(300, 300, 1200, 600)
        self.setLayout(QHBoxLayout())
        
        central = Central()
        self.setCentralWidget(central)
        
    def statusbar(self):
        statusbar = self.statusBar()
        #statusbar.showMessage('Main Window')
    
    def menubar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        fileMenu = menubar.addMenu("File")
        fileMenu.addAction("New")

        save = QAction("Save", self)
        save.setShortcut("Ctrl+S")
        fileMenu.addAction(save)
        
        quit = QAction("Quit", self)
        fileMenu.addAction(quit)
        
        
        editMenu = menubar.addMenu("Edit")
        editMenu.addAction("copy")
        editMenu.addAction("paste")

        aboutMenu = menubar.addMenu("About")
        aboutMenu.triggered[QAction].connect(self.processtrigger)

    def processtrigger(self):
        print 'hello'



class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)
        self.build()
        
    def build(self):
        fileMenu = self.addMenu("File")
        fileMenu.addAction("New")
    


class Central(QWidget):
    
    def __init__(self, parent=None):
        super(Central, self).__init__(parent)
        self.build()
    
    def build(self):
        #self.main_window()
        #self.buttons()
        #self.statusbar()
        #self.menubar()
        self.checkbox()
        self.terminals()
        self.daq()
        #self.progress_bar()
        #self.combo_box()
    
    def a(self):
        l1 = QLabel("Name")
        nm = QLineEdit()

        l2 = QLabel("Address")
        add1 = QLineEdit()
        add2 = QLineEdit()
        fbox = QFormLayout()
        fbox.addRow(l1,nm)
        vbox = QVBoxLayout()

        vbox.addWidget(add1)
        vbox.addWidget(add2)
        fbox.addRow(l2,vbox)
        hbox = QHBoxLayout()

        r1 = QRadioButton("Male")
        r2 = QRadioButton("Female")
        hbox.addWidget(r1)
        hbox.addWidget(r2)
        hbox.addStretch()
        fbox.addRow(QLabel("sex"),hbox)
        fbox.addRow(QPushButton("Submit"),QPushButton("Cancel"))

        self.setLayout(fbox)
        
    # def buttons(self):
    #     okButton = QPushButton("OK")
    #     cancelButton = QPushButton("Cancel")
    #
    #     hbox = QHBoxLayout()
    #     hbox.addStretch(1)
    #     hbox.addWidget(okButton)
    #     hbox.addWidget(cancelButton)
    #
    #     vbox = QVBoxLayout()
    #     vbox.addStretch(1)
    #     vbox.addLayout(hbox)
    #
    #     self.setLayout(vbox)

        
    def checkbox(self):
        cb = QCheckBox('Show title', self)
        cb.move(20, 20)
        cb.toggle()
        cb.stateChanged.connect(self.changeTitle)
        
    def changeTitle(self, state):
        if state == Qt.Checked:
            self.setWindowTitle('QCheckBox')
        else:
            self.setWindowTitle('')
    
    
    def progress_bar(self):
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.btn = QPushButton('Start', self)
        self.btn.move(40, 80)
        self.btn.clicked.connect(self.doAction)

        self.timer = QBasicTimer()
        self.step = 0
        
    def timerEvent(self, e):
        if self.step >= 100:
            self.timer.stop()
            self.btn.setText('Finished')
            return
            
        self.step = self.step + 1
        self.pbar.setValue(self.step)
        
    def doAction(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn.setText('Start')
        else:
            self.timer.start(100, self)
            self.btn.setText('Stop')
    
    
    def combo_box(self):
        self.lbl = QLabel("Ubuntu", self)
        combo = QComboBox(self)
        combo.addItem("Ubuntu")
        combo.addItem("Mandriva")
        combo.addItem("Fedora")
        combo.addItem("Arch")
        combo.addItem("Gentoo")

        combo.move(50, 50)
        self.lbl.move(50, 150)

        combo.activated[str].connect(self.onActivated)        
        
    def onActivated(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()
        
    def terminals(self):
        terminalsGroup = QGroupBox(self)
        terminalsGroup.setGeometry(QRect(300, 0, 150, 50))
        terminalsGroup.setObjectName("terminalsGroup")
        terminalsGroup.setTitle("Output Terminals")
        
        frontRadio = QRadioButton(terminalsGroup)
        frontRadio.setGeometry(QRect(10, 20, 60, 20))
        frontRadio.setChecked(True)
        frontRadio.setObjectName("frontRadio")
        frontRadio.setText("Front")
        
        rearRadio = QRadioButton(terminalsGroup)
        rearRadio.setGeometry(QRect(80, 20, 60, 20))
        rearRadio.setObjectName("rearRadio")
        rearRadio.setText("Rear")
        
    def daq(self):
        daqGroup = QGroupBox(self)
        daqGroup.setGeometry(QRect(410, 100, 200, 131))
        daqGroup.setObjectName("daqGroup")
        daqGroup.setTitle("Measurement Settings")
        zeroCheck = QCheckBox(daqGroup)
        zeroCheck.setGeometry(QRect(10, 110, 80, 22))
        zeroCheck.setObjectName("zeroCheck")
        speedCombo = QComboBox(daqGroup)
        speedCombo.setGeometry(QRect(80, 50, 110, 20))
        speedCombo.setObjectName("speedCombo")
        speedCombo.addItem("")
        speedCombo.addItem("")
        speedCombo.addItem("")
        speedCombo.addItem("")
        speedCombo.setItemText(0, "Fast")
        speedCombo.setItemText(1, "Medium")
        speedCombo.setItemText(2, "Normal")
        speedCombo.setItemText(3, "High Accuracy")
        label_7 = QLabel(daqGroup)
        label_7.setGeometry(QRect(10, 50, 62, 20))
        label_7.setObjectName("label_7")
        label_7.setText("Speed")
        averageSpin = QSpinBox(daqGroup)
        averageSpin.setEnabled(True)
        averageSpin.setGeometry(QRect(130, 80, 60, 20))
        averageSpin.setMinimum(0)
        averageSpin.setMaximum(100)
        averageSpin.setObjectName("averageSpin")
        label_8 = QLabel(daqGroup)
        label_8.setGeometry(QRect(10, 80, 121, 20))
        label_8.setObjectName("label_8")
        saveModeCombo = QComboBox(daqGroup)
        saveModeCombo.setGeometry(QRect(110, 20, 80, 20))
        saveModeCombo.setObjectName("saveModeCombo")
        saveModeCombo.addItem("")
        saveModeCombo.addItem("")
        label_10 = QLabel(daqGroup)
        label_10.setGeometry(QRect(10, 20, 90, 20))
        label_10.setObjectName("label_10")
        
       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = Window()
    sys.exit(app.exec_())