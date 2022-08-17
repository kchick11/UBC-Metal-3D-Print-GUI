import sys
from turtle import position
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import LaserComms
import IRCam
import Pyrometer
import PrinterGUIFormat
import SavetoSQL
import datetime

# Global Variables to control button states, 0 = OFF
global GUIDE_BEAM_STATE
global LASER_BEAM_STATE
global PYRO_GB_STATE
global CAM_CONNECT_STATE
global IR_PLOT_STATE
global SAMPLING_FREQ # Sample frequency of data collection
GUIDE_BEAM_STATE = 0
LASER_BEAM_STATE = 0
PYRO_GB_STATE = 0
CAM_CONNECT_STATE = 0
IR_PLOT_STATE = 0
SAMPLING_FREQ = 0.1 # Sampling frequency set at 0.1, works smootly when only 2/3 devices are running. When commands are sent to all three, laser box, pyrometer, IR cam, there is some lag in the display.

# Global Variables to log data for pyrometer and IRCam
global pyroIndex
global pyrotimeArr
global pyrotempArr
global pyroCPUtime
global IRIndex
global IRtimeArr
global IRtempArr
global IRCPUtime

pyroIndex = 0.0
IRIndex = SAMPLING_FREQ # IRIndex starts at sampling frequency because the start condition for the index is if pyroIndex is > 0. So they will sync when IRIndex starts one sampling frequency ahead of 0
pyrotimeArr = []
pyrotempArr = []
pyroCPUtime = []
IRtimeArr = []
IRtempArr = []
IRCPUtime = []

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(150,75,1620,930) #Starting Window Size
        self.setWindowTitle("DLD Printer GUI")

        self.UI() # Executes UI
        self.show() 

    def UI(self):
        self.widgets() # Creates widgets
        self.layouts() # Defines and places layouts and widgets
        self.threads() # Starts threads that are run in the background
        self.setSampleFreq() # Sets the sample frequency in the IRCam.py and Pyrometer.py files

################################################################# WIDGETS ######################################################################

    def widgets(self):
        # Laser Button Widget (Top Left Layout)
        self.laserHeaderText = QLabel("Laser Set Power (0-500 W):")
        self.powerSlider = QSlider(Qt.Horizontal)
        self.powerSlider.setMinimum(0)
        self.powerSlider.setMaximum(500)
        self.powerSlider.setTickInterval(25)
        self.powerSlider.setTickPosition(QSlider.TicksAbove)
        self.powerSlider.valueChanged.connect(self.powerSliderInput)
        self.powerInput = QLineEdit()
        self.powerInput.setMaximumSize(60,30)
        self.powerInput.returnPressed.connect(self.setPower)
        self.deliveredPowerText = QLabel("Laser Deliviered Power (W):")
        self.deliveredPowerReading = QLineEdit()
        self.deliveredPowerReading.setMaximumSize(60,30)
        self.deliveredPowerReading.setReadOnly(True)
        self.laserTempText = QLabel("Temperature (Celsius):")
        self.laserTempReading = QLineEdit()
        self.laserTempReading.setMaximumSize(60,30)
        self.laserTempReading.setReadOnly(True)
        self.guideBeamText = QLabel("Guide Beam:")
        self.guideBeamText.setAlignment(Qt.AlignCenter)
        self.guideBeamButton = QPushButton("OFF")
        self.guideBeamButton.setStyleSheet(PrinterGUIFormat.OFFButtonStyle())
        self.guideBeamButton.clicked.connect(self.guideBeamState)
        self.laserBeamText = QLabel("Laser Beam:")
        self.laserBeamText.setAlignment(Qt.AlignCenter)
        self.laserBeamButton = QPushButton("OFF")
        self.laserBeamButton.setStyleSheet(PrinterGUIFormat.OFFButtonStyle())
        self.laserBeamButton.clicked.connect(self.laserBeamState)
        self.cmdLineText = QLabel("Command Line:")
        self.cmdLineInput = QLineEdit()
        self.cmdLineInput.setMaximumHeight(30)
        self.cmdLineInput.returnPressed.connect(self.cmdInput)
        self.responseLineText = QLabel("Response:")

        # IR Camera Display (Top Right Layout)
        self.IRCamFigure = plt.figure()
        self.IRCamCanvas = FigureCanvas(self.IRCamFigure)

        # Pyrometer Display (Bottom Left Layout)
        self.pyrometerFigure = plt.figure()
        self.pyrometerCanvas = FigureCanvas(self.pyrometerFigure)

        # Camera Button Widget (Bottom Right Layout)
        self.IRCamText = QLabel("IR Camera Display:")
        self.IRCamDispButton = QPushButton("Display")
        self.IRCamDispButton.clicked.connect(self.dispIRImg)
        self.IRCamConnectButton = QPushButton("Connect")
        self.IRCamConnectButton.clicked.connect(self.startIRCam)
        self.pyrometerText = QLabel("Pyrometer Display:")
        self.pyrometerStartButton = QPushButton("Start")
        self.pyrometerStartButton.clicked.connect(self.startPyrometer)
        self.pyrometerStopButton = QPushButton("Stop")
        self.pyrometerStopButton.clicked.connect(self.stopPyrometer)
        self.pyrometerLaserButton = QPushButton("Guide: OFF")
        self.pyrometerLaserButton.setStyleSheet(PrinterGUIFormat.OFFButtonStyle())
        self.pyrometerLaserButton.clicked.connect(self.pyroBeamState)
        self.pyrometerClearButton = QPushButton("Clear")
        self.pyrometerClearButton.clicked.connect(self.clearPyroData)
        self.pyrometerSpacer = QLabel(" ")

################################################################# LAYOUTS ######################################################################

    def layouts(self):
        # Defining Layouts
        self.mainLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.botLayout = QHBoxLayout()
        
        # Main Layout Divisions
        self.topLeftLayout = QVBoxLayout()
        self.laserButtonTopLayout = QGridLayout()
        self.laserButtonBotLayout = QGridLayout()
        self.laserButtonFormLayout = QFormLayout()
        self.IRCamDispLayout = QVBoxLayout()
        self.topRightFrame = QFrame()
        self.topRightFrame.setStyleSheet(PrinterGUIFormat.TopRightFrame())
        self.topRightFrame.setLayout(self.IRCamDispLayout)
        self.pyroDispLayout = QVBoxLayout()
        self.botLeftFrame = QFrame()
        self.botLeftFrame.setStyleSheet(PrinterGUIFormat.botLeftFrame())
        self.botLeftFrame.setLayout(self.pyroDispLayout)
        self.botRightLayout = QVBoxLayout()
        self.camButtonLayout = QGridLayout()

        ###################################################### Laser Button Layout (Top Left Layout) #################################################
        
        # First Row
        self.topLeftLayout.addStretch()
        self.laserButtonTopLayout.addWidget(self.laserHeaderText,0,0)
        self.laserButtonTopLayout.addWidget(self.powerInput,0,1)
        self.laserButtonTopLayout.setAlignment(Qt.AlignLeft)
        self.topLeftLayout.addLayout(self.laserButtonTopLayout)

        # Second Row
        self.topLeftLayout.addWidget(self.powerSlider) 

        # Third Row
        self.laserButtonBotLayout.addWidget(self.deliveredPowerText,0,0)
        self.laserButtonBotLayout.addWidget(self.deliveredPowerReading,0,1)
        self.laserButtonBotLayout.addWidget(self.guideBeamText,0,2)
        self.laserButtonBotLayout.addWidget(self.laserBeamText,0,3)

        # Fourth Row
        self.laserButtonBotLayout.addWidget(self.laserTempText,1,0)
        self.laserButtonBotLayout.addWidget(self.laserTempReading,1,1)
        self.laserButtonBotLayout.addWidget(self.guideBeamButton,1,2)
        self.laserButtonBotLayout.addWidget(self.laserBeamButton,1,3)
        self.topLeftLayout.addLayout(self.laserButtonBotLayout)

        # Fifth Row
        self.laserButtonFormLayout.addRow(self.cmdLineText,self.cmdLineInput)
        self.laserButtonFormLayout.addRow(self.responseLineText)
        self.topLeftLayout.addLayout(self.laserButtonFormLayout)
        self.topLeftLayout.addStretch()
        
        #################################################### IR Camera Display (Top Right Layout) ###################################################
        self.IRCamDispLayout.addWidget(self.IRCamCanvas)
        #Testing the layout size
        IRMap = np.random.random((64,64))*4000
        self.IRCamFigure.clear()
        ax1 = self.IRCamFigure.add_subplot(111)
        ax1.set_xticks([0,10,20,30,40,50,60])
        ax1.set_xticklabels([0,100,200,300,400,500,600])
        ax1.set_yticks([60,50,40,30,20,10,0])
        ax1.set_yticklabels([0,100,200,300,400,500,600])
        ax1.set_title("IR Camera")
        ax1.set_xlabel("Pixels")
        ax1.set_ylabel("Pixels")
        im1 = ax1.imshow(IRMap, interpolation = 'nearest', cmap='inferno') # Inferno can be changed to another color map
        self.IRCamFigure.subplots_adjust(right=0.8) # Making room for colorbar
        color_bar_ax = self.IRCamFigure.add_axes([0.85, 0.15, 0.05, 0.7]) # Setting colorbar
        self.IRCamFigure.colorbar(im1,color_bar_ax)
        self.IRCamCanvas.draw()

        #################################################### Pyrometer Display (Bottom Left Layout) #################################################
        self.pyroDispLayout.addWidget(self.pyrometerCanvas)
        #Testing the layout size
        self.pyrometerFigure.clear()
        ax2 = self.pyrometerFigure.add_subplot(111)
        pyrotimeArr = [0,1,2,3,4,5]
        pyrotempArr = [10.1,10.2,10.0,10.2,9.9,10.1]
        ax2.set_title("Pyrometer")
        ax2.set_ylabel("Temperature (°C)")
        ax2.set_xlabel("Time (s)")
        ax2.plot(pyrotimeArr,pyrotempArr)
        self.pyrometerCanvas.draw()

        #################################################### Camera Button Grid (Bottom Right Layout) #############################################
        self.camButtonLayout.addWidget(self.IRCamText,0,0)
        self.camButtonLayout.addWidget(self.IRCamDispButton,1,0)
        self.camButtonLayout.addWidget(self.IRCamConnectButton,1,1)
        self.camButtonLayout.addWidget(self.pyrometerText,2,0)
        self.camButtonLayout.addWidget(self.pyrometerStartButton,3,0)
        self.camButtonLayout.addWidget(self.pyrometerStopButton,3,1)
        self.camButtonLayout.addWidget(self.pyrometerLaserButton,4,0)
        self.camButtonLayout.addWidget(self.pyrometerClearButton,4,1)
        self.camButtonLayout.addWidget(self.pyrometerSpacer,5,0)
        self.botRightLayout.addLayout(self.camButtonLayout)

        # Placing Layouts
        self.topLayout.addLayout(self.topLeftLayout,70)
        self.topLayout.addWidget(self.topRightFrame,30)
        self.botLayout.addWidget(self.botLeftFrame,70)
        self.botLayout.addLayout(self.botRightLayout,30)

        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.botLayout)

        self.setLayout(self.mainLayout)
        self.setMinimumWidth(900)

################################################################# MULTI-THREADS #####################################################################

    def threads(self):
        self.laserBoxReadings = LaserComms.readLaserBoxData()
        self.laserBoxReadings.start()
        self.laserBoxReadings.getTempData.connect(self.displayLaserTemp) # Continuous reading of laser head temperature
        self.laserBoxReadings.getPowerData.connect(self.displayLaserPower) # Continuous reading of laser output power
        # Threads found in other sections of code, control F the following functions to find that section of code
        # self.IRCam = IRCam.runCamera() #starts the IRCam thread
        # self.pyrometer = Pyrometer.connectPyro() #starts the pyrometer
        # self.saveData = SavetoSQL.saveData() # Saves and commits data

################################################################ BEAM ON/OFF FUNCTIONS ##############################################################

    def guideBeamState(self): # Keeps the state of the laser guide beam button on the GUI, either ON/1 or OFF/0. Function is called when guide beam button is pressed
        global GUIDE_BEAM_STATE

        if GUIDE_BEAM_STATE == 0:
            GUIDE_BEAM_STATE = 1
            self.guideBeamButton.setText("ON")
            self.guideBeamButton.setStyleSheet(PrinterGUIFormat.ONButtonStyle())
            reply = LaserComms.sendCmd("ABN") # sends the command to the laser box to turn on guide beam 
        elif GUIDE_BEAM_STATE == 1:
            GUIDE_BEAM_STATE = 0
            self.guideBeamButton.setText("OFF")
            self.guideBeamButton.setStyleSheet(PrinterGUIFormat.OFFButtonStyle())
            reply = LaserComms.sendCmd("ABF") # sends the command to turn off guide beam

        if reply == "ERROR": # Throws an error if unable to coneect to laser box
            laserBoxWarning = QMessageBox.information(self,"Warning","Server Timeout. No Laser Box Detected.")

    def laserBeamState(self): # Keeps the state of the laser button on the GUI, ON/1 and OFF/0. Function called when laser beam button is pressed
        global LASER_BEAM_STATE
        # same structure as the guide beam code above
        if LASER_BEAM_STATE == 0:
            LASER_BEAM_STATE = 1
            self.laserBeamButton.setText("ON")
            self.laserBeamButton.setStyleSheet(PrinterGUIFormat.ONButtonStyle())
            reply = LaserComms.sendCmd("EMON")
        elif LASER_BEAM_STATE == 1:
            LASER_BEAM_STATE = 0
            self.laserBeamButton.setText("OFF")
            self.laserBeamButton.setStyleSheet(PrinterGUIFormat.OFFButtonStyle())
            reply = LaserComms.sendCmd("EMOFF")

        if reply == "ERROR":
            laserBoxWarning = QMessageBox.information(self,"Warning","Server Timeout. No Laser Box Detected.")

    def pyroBeamState(self): # Keeps the state of the pyrometer guide beam button on the GUI
        global PYRO_GB_STATE

        if PYRO_GB_STATE == 0:
            Pyrometer.guidebeam(True) # updates the pyrometer guide beam state on the pyrometer sheet
            PYRO_GB_STATE = 1
            self.pyrometerLaserButton.setText("Guide: ON")
            self.pyrometerLaserButton.setStyleSheet(PrinterGUIFormat.ONButtonStyle())
        elif PYRO_GB_STATE == 1:
            Pyrometer.guidebeam(False)
            PYRO_GB_STATE = 0
            self.pyrometerLaserButton.setText("Guide: OFF")
            self.pyrometerLaserButton.setStyleSheet(PrinterGUIFormat.OFFButtonStyle())

################################################################## POWER SLIDER FUNCTIONS ##########################################################

    def powerSliderInput(self): # Changes laser power and adjusts display on the reading input to match
        # function run when slider input is changed
        inputPower = self.powerSlider.value() # gets value from slider
        self.powerInput.setText(str(inputPower))
        inputPowerPercent = round((inputPower/5),1) # % is power/500
        msg = (f"SDC {str(inputPowerPercent)}") # converts the slider input to a string
        reply = LaserComms.sendCmd(msg) # sends the string as a command to the laser box

        if reply == "ERROR": # if error, alert the user
            laserBoxWarning = QMessageBox.information(self,"Warning","Server Timeout. No Laser Box Detected.")

    def setPower(self): # Changes laser power and adjusts display on the slider to match
        # function run when return is pressed in the set power text box, function is the same as the slider funtion above
        inputPower = self.powerInput.text()
        self.powerSlider.setValue(int(inputPower))
        inputPowerPercent = round((int(inputPower)/5),1)
        msg = (f"SDC {str(inputPowerPercent)}")
        reply = LaserComms.sendCmd(msg)

        if reply == "ERROR":
            laserBoxWarning = QMessageBox.information(self,"Warning","Server Timeout. No Laser Box Detected.")

################################################################## COMMAND LINE & READ FUNCTIONS ##########################################################

    def cmdInput(self): # Allows user to send any command found in the manual. A response of BCMD indicates unknown command
        # function executes when return is pressed in the command line box
        msg = self.cmdLineInput.text() # gets message from command line
        response = LaserComms.sendCmd(msg) # sends message
        self.cmdLineInput.clear()
        self.responseLineText.setText(f"Response:          {response}") # gets and prints response

        if response == "ERROR": # if error, alert the user
            laserBoxWarning = QMessageBox.information(self,"Warning","Server Timeout. No Laser Box Detected.")
    
    def displayLaserTemp(self,temp): # Reads and displays the laser head temperature
        self.laserTempReading.setText(temp) # constantly reads laser head temperature

    def displayLaserPower(self,power): # Reads and displays the delivered laser power
        self.deliveredPowerReading.setText(power) # constantly reads delievered power

################################################################### IR CAMERA FUNCTIONS ###################################################################

    def startIRCam(self):
        global CAM_CONNECT_STATE

        if CAM_CONNECT_STATE == 0:
            try:
                print("searching")
                self.IRCam = IRCam.runCamera() #starts the IRCam thread
                self.IRCam.start()
                self.IRCam.getConnectState.connect(self.changeIRConnectState) # if camera connects, change the connection state to ON/1
                self.IRCam.getImgData.connect(self.plotIRImg) # when camera returns img data, plot the data
            except:
                CAM_CONNECT_STATE = 0 # if connection failed, alert user
                IRCamWarning = QMessageBox.information(self,"Warning","No Camera Detected. Please Retry. ")

    def dispIRImg(self): # Turns on the image display feed, changes the state of the IR cam button
        global IR_PLOT_STATE

        if IR_PLOT_STATE == 0:
            self.IRCamDispButton.setText("Pause")
            IR_PLOT_STATE = 1
            print("starting feed")

        else:
            self.IRCamDispButton.setText("Display")
            IR_PLOT_STATE = 0
            print("stopping feed")

    def plotIRImg(self,IRMap): # Image display feed
        global IR_PLOT_STATE
        global pyroIndex
        global IRIndex
        global IRtimeArr
        global IRtempArr
        print(IRMap)
        IRMapScaled = (IRMap - np.min(IRMap))/(np.max(IRMap)-np.min(IRMap))*4000 # Scales the heat map to somewhat match temperatures. To be more accurate 4000 can be replaced with a variable which contains the max temp read by the pyrometer

        # val = pyroIndex - IRIndex # For testing the lag between indices
        # print(val)

        if pyroIndex > 0: # if the pyrometer has started logging data, start the IR cam data logging
            now = datetime.datetime.now()
            IRCPUtime.append(now) # gets the CPU time for reliability verification 
            IRtimeArr.append(IRIndex) # appends the index which represents the time step
            IRtempArr.append(IRMapScaled) # appends the IR map array
            IRIndex += SAMPLING_FREQ # increases time step


        if IR_PLOT_STATE == 1:
            min = 0 # These are the min and max values of the img array. The image matrix is normalized to show temps between 0 and 4000
            max = 4000
            self.IRCamFigure.clear()
            # set figure labels
            ax1 = self.IRCamFigure.add_subplot(111) 
            ax1.set_xticks([0,10,20,30,40,50,60])
            ax1.set_xticklabels([0,100,200,300,400,500,600])
            ax1.set_yticks([60,50,40,30,20,10,0])
            ax1.set_yticklabels([0,100,200,300,400,500,600])
            ax1.set_title("IR Camera")
            ax1.set_xlabel("Pixels")
            ax1.set_ylabel("Pixels")
            # plots the IR map and the color bar
            im1 = ax1.imshow(IRMapScaled, vmin = min, vmax = max, interpolation = 'nearest', cmap='inferno') # Inferno can be changed to another color map
            self.IRCamFigure.subplots_adjust(right=0.8)
            color_bar_ax = self.IRCamFigure.add_axes([0.85, 0.15, 0.05, 0.7]) # adds the colorbar
            self.IRCamFigure.colorbar(im1,color_bar_ax)
            self.IRCamCanvas.draw()

    def changeIRConnectState(self,state): # Changes the text on the connect button once camera is successfully connected
        if state == 1:
            self.IRCamConnectButton.setText("Connected")
        elif state == 0:
            self.IRCamConnectButton.setText("Connect")
            IRCamWarning = QMessageBox.information(self,"Warning","No Camera Detected. Please Retry. ")


################################################################### PYROMETER FUNCTIONS ###################################################################

    def startPyrometer(self):
        Pyrometer.updateChannelStatus(1) # Lets the child thread know the pyrometer is on
        self.pyrometer = Pyrometer.connectPyro() # Starts pyrometer data logging
        self.pyrometer.start()
        self.pyrometer.getTempData.connect(self.plotPyroData) # plots data when it is recieved from the thread

    def stopPyrometer(self):
        global pyrotimeArr
        global pyrotempArr
        global IRtimeArr
        global IRtempArr
        global pyroCPUtime
        global IRCPUtime

        Pyrometer.updateChannelStatus(0) # Lets the child thread know the pyrometer is off
        SavetoSQL.transmitData(pyroCPUtime,pyrotimeArr,pyrotempArr,IRCPUtime,IRtimeArr,IRtempArr) # Sends data to be saved
        self.saveData = SavetoSQL.saveData() # Saves and commits data
        self.saveData.start()
        # print("stop")

    def clearPyroData(self): # Clears pyrometer and IR camera data
        global pyroIndex
        global IRIndex
        global pyrotimeArr
        global pyrotempArr
        global IRtimeArr
        global IRtempArr
        global pyroCPUtime
        global IRCPUtime

        pyroIndex = 0.0
        pyrotimeArr = []
        pyrotempArr = []  
        IRIndex = SAMPLING_FREQ
        IRtimeArr = []
        IRtempArr = []
        pyroCPUtime = []
        IRCPUtime = []
        
        self.pyrometerFigure.clear()
        self.pyrometerCanvas.draw()

    def plotPyroData(self,temp): # Plots pyrometer data
        global pyrotimeArr
        global pyrotempArr
        global pyroIndex

        #print(temp)
        # print(f"pyrotime = {pyroIndex}")
        now = datetime.datetime.now() # gets CPU time for reliability and cross validation with IR Cam CPU time
        pyroCPUtime.append(now) # saves the CPU time into an array
        pyrotimeArr.append(pyroIndex) # saves the index into the time array
        pyrotempArr.append(temp) # saves the pyrometer reading

        # plot pyrometer data 
        self.pyrometerFigure.clear()
        ax2 = self.pyrometerFigure.add_subplot(111)
        ax2.set_title("Pyrometer")
        ax2.set_ylabel("Temperature (°C)")
        ax2.set_xlabel("Time (s)")
        ax2.plot(pyrotimeArr,pyrotempArr)
        self.pyrometerCanvas.draw()

        pyroIndex += SAMPLING_FREQ # increase index

##################################################### SET SAMPLING FREQUENCY FUNCTION ###################################################

    def setSampleFreq(self): # Connects to other .py files to set the sampling frequencies to match
        IRCam.setSampleFreq(SAMPLING_FREQ)
        Pyrometer.setSampleFreq(SAMPLING_FREQ)

#########################################################################################################################################

App= QApplication(sys.argv)
window=Window()
sys.exit(App.exec_())