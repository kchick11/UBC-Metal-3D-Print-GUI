import socket
import time
from PyQt5.QtCore import QThread, pyqtSignal

# Parameters to connect to laser box
PORT = 10001
SERVER = "192.168.3.230" 
ADDR = (SERVER, PORT)
FORMAT = 'ascii'
DISCONNECT_MESSAGE = "!close"
TIMEOUT = 3 #seconds

def readLaser(msg): # Continuous messaging to the laser
    try: # Tries to connect to laser
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(TIMEOUT)
        client.connect(ADDR)
        command = msg # when connected, send the message
        reading = send(command,client)
        result = reading.partition(':') # format the response
        client.close()

        if command == DISCONNECT_MESSAGE: # For implementation of disconnect funtion if needed
            pass
            # connected = False

        return (result[2]) # returns the result
    except: # If no connection, display N/A
        return("N/A")

def sendCmd(msg): # Single message to the laser. In future when looking to send many signals to control laser power. It may be required to pass the messages in a for loop and keep the channel open to improve response time
    try:
        # same structure as the continous code above
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.settimeout(TIMEOUT)
        client.connect(ADDR)
        command = msg
        reading = send(command,client)
        client.close()
        #print(reading)
        return reading
    except:
        #print("Server Timeout, No Laser Box Dectected")
        return("ERROR")

def send(msg,client): # Function that formats, encodes, and decodes the message
    msg = msg + '\r' # return carrige appended to the end of each message
    message = msg.upper().encode(FORMAT)
    client.send(message)
    data = client.recv(1024)
    data = data.decode(FORMAT)
    return data

class readLaserBoxData(QThread): # A thread that allows background continous reading of the temperature and power
    getTempData = pyqtSignal(object)
    getPowerData = pyqtSignal(object)
    def run(self):
        while True:
            time.sleep(0.5) # Updates every half second
            temperature = readLaser("RCT") # reads temperature
            deliveredPower = readLaser("ROP")  # reads delivered power
            self.getTempData.emit(temperature) # when temp is read, start the display function in the main code
            self.getPowerData.emit(deliveredPower) # when delivered power is read, start the display function in the main code