import socket
import sys
import time

PORT = 10001
SERVER = "192.168.3.230" 
ADDR = (SERVER, PORT)
FORMAT = 'ascii'
DISCONNECT_MESSAGE = "!close"

def readLaser(msg):
    connected = True
    while connected:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(ADDR)
        command = msg
        reading = send(command,client)
        result = reading.partition(':')
        client.close()

        if command == DISCONNECT_MESSAGE:
            connected = False

        return (result[2])

def sendCmd(msg):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(ADDR)
        command = msg
        reading = send(command,client)
        client.close()
        #print(reading)
        return reading

def send(msg,client):
    msg = msg + '\r'
    message = msg.upper().encode(FORMAT)
    client.send(message)
    data = client.recv(1024)
    data = data.decode(FORMAT)
    return data
   