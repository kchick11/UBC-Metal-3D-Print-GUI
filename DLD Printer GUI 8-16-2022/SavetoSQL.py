from PyQt5 import *
from PyQt5.QtCore import QThread
import sqlite3

global dataRow
dataRow = []

def transmitData(pyrocpu,pyrotime,pyrotemp,IRcpu,IRtime,IRtemp): # Gets array data from GUI script and stores all data in a tuple, which will be used to save the data to SQL database
    global dataRow

    for index in range(len(pyrotime)):
        pyroCPUtime = pyrocpu(index)
        pyrotimeVal = pyrotime(index)
        pyrotempVal = pyrotemp(index)
        IRCPUtime = IRcpu(index)
        IRtimeVal = IRtime(index)
        IRtempVal = IRtemp(index)
        dataRow.append((pyroCPUtime,pyrotimeVal,pyrotempVal,IRCPUtime,IRtimeVal,IRtempVal))

    return


class saveData(QThread): # A thread which saves data to SQL database
    # connect db
    con = sqlite3.connect("DLD Data.db")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS TemperatureData
    (PyroCPUTime text, PyroTime real, PyroTemp real, IRCamCPUTime text, IRCamTime real, IRCamTemp real)''')

    cur.execute('''INSERT INTO TemperatureData VALUES
    (' ',' ',' ',' ',' ',' ')''') # Saves a blank row first to seperate data batches

    cur.executemany("INSERT INTO TemperatureData VALUES (?,?,?,?,?,?)",dataRow) # saves each row in the tuple array into the db
    # there may be issues uploading IRCamTemp because the data stored in that array is large matrices

    con.commit()