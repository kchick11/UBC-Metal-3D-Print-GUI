import socket
import sys
import time
from PyQt5.QtCore import QTimer, QThread, pyqtSignal

PORT = 10001
SERVER = "192.168.3.230" 
ADDR = (SERVER, PORT)
FORMAT = 'ascii'
DISCONNECT_MESSAGE = "!close"

def readLaser(msg): # Continuous messaging to the laser
    connected = True
    while connected: # Connect to the laser
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(ADDR)
        command = msg
        reading = send(command,client)
        result = reading.partition(':')
        client.close()

        if command == DISCONNECT_MESSAGE:
            connected = False

        return (result[2])

def sendCmd(msg): # Single message to the laser
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(ADDR)
    command = msg
    reading = send(command,client)
    client.close()
    #print(reading)
    return reading

def send(msg,client): # Function that formats, encodes, and decodes the message
    msg = msg + '\r'
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
            temperature = readLaser("RCT")
            deliveredPower = readLaser("ROP")
            self.getTempData.emit(temperature)
            self.getPowerData.emit(deliveredPower)