from PyQt5 import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
import serial.tools.list_ports
import serial
import time
import random

global CHANNEL_STATUS
global SAMPLE_FREQ

def setSampleFreq(x): # Sets the sample frequency using the value from the parent thread
    global SAMPLE_FREQ
    SAMPLE_FREQ = x
    return

def updateChannelStatus(status): # Keeps the channel status of the pyrometer
    global CHANNEL_STATUS
    if status == 1:
        CHANNEL_STATUS = 1
    else:
        CHANNEL_STATUS = 0
    return

def guidebeam(status): # Turns on/off the pyrometer guide beam
    # parameters to connect to pyrometer port
    serialInst = serial.Serial()
    serialInst.baudrate = 115200
    serialInst.port = "COM3"
    serialInst.open()
    if status == True:
        GBcmd = b"\xa5\x01\xa4" # Pyrometer ON command
    elif status == False:
        GBcmd = b"\xa5\x00\xa5" # Pyrometer OFF command
    serialInst.write(GBcmd)
        
class connectPyro(QThread):
    global CHANNEL_STATUS
    getTempData = pyqtSignal(float)
    def run(self):
        # parameters to connect to pyrometer port
        serialInst = serial.Serial()
        serialInst.baudrate = 115200
        serialInst.port = "COM3"
        serialInst.open()

        if (serialInst.isOpen() == True):
            print("Channel Opened")

            while CHANNEL_STATUS == 1:
                # read command 
                cmd = b"\x01\x00\xff\xff\x01" #\command in HEX \Index (00) \READ \READ \Check Sum
                # print(cmd)
                serialInst.write(cmd)  
                time.sleep(SAMPLE_FREQ) # sleep to match the sampling frequency
                if serialInst.in_waiting:
                    packet = serialInst.read(2) # reads the response from the pyrometer
                    # print(packet)
                    temp = (packet[0]*256 + packet[1] - 1000)/10 # Calculates the temp based on the formula found in the device manual
                    # print(f"Temperature: {temp} C\n")
                    self.getTempData.emit(temp) # sends temperature to main code to save and plot
                else:
                    # print("Device not started")
                    serialInst.close()
                    return

            print("Channel Closed")
            serialInst.close()
            return

        else: # dummy data generated for testing purposes
            while CHANNEL_STATUS == 1:
                time.sleep(SAMPLE_FREQ)
                byte1 = random.randint(19,64)
                byte2 = random.randint(19,64)
                temp = (byte1*256 + byte2 - 1000)/10
                self.getTempData.emit(temp)
            
            print("Port not opened")
            return

