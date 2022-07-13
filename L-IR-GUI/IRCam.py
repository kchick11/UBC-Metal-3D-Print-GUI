from PyQt5 import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from matplotlib import image
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import os
from matplotlib.figure import Figure
import PySpin
import matplotlib.pyplot as plt
import numpy as np
import sys
import keyboard
import time

class runCamera(QThread): # Connects and runs IR camera
    getImgData = pyqtSignal(object)
    getConnectState = pyqtSignal(int)
    def run(self):
        # detect cameras
        global system
        global cam
        CAM_CONNECT_STATE = 0
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        num_cameras = cam_list.GetSize()
        if num_cameras > 0: # Checks if a camera is connected if yes, configure camera, if no, do nothing
            cam = cam_list[0]
            print("Camera connected")
            CAM_CONNECT_STATE = 1
            self.getConnectState.emit(CAM_CONNECT_STATE)

            # run camera
            nodemap_tldevice = cam.GetTLDeviceNodeMap()
            cam.Init()
            nodemap = cam.GetNodeMap()

            # configure camera
            sNodemap = cam.GetTLStreamNodeMap()
            # Change bufferhandling mode to NewestOnly
            node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
            if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
                print('Unable to set stream buffer handling mode.. Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
            if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
                print('Unable to set stream buffer handling mode.. Aborting...')
                return False

            # Retrieve integer value from entry node
            node_newestonly_mode = node_newestonly.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_bufferhandling_mode.SetIntValue(node_newestonly_mode)
          
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            print('Acquisition mode set to continuous...')

            cam.BeginAcquisition()

            print('Acquiring images...')
            print("Press Display")
            continue_recording = True

            # recording loop
            while(continue_recording):
                fps = 1/12 # 1/12 is a good fps, faster refresh rates cause lag on our computer
                if 1 == 1: # While true loop, a condition can be placed here
                    image_result = cam.GetNextImage(1000)
                    image_data = image_result.GetNDArray()
                    time.sleep(fps)
                    # print(image_data)
                    self.getImgData.emit(image_data)
                    image_result.Release()

            cam.EndAcquisition()

        else:
            cam_list.Clear()
            system.ReleaseInstance()
            self.getConnectState.emit(CAM_CONNECT_STATE)
            print("No camera detected, please restart and retry")
