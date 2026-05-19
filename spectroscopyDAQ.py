from Devices.CameraLib import CameraManager, ScienceCamera
from Devices.cameraViewer import CameraViewer
from client_class import wavemeterClient, dummyWavemeter
from SinglePortViewer import SinglePortViewer
from liveHistogramWidget import LiveHistogramWidget
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
import os, sys, time
import numpy as np

class DAQViewer(QtWidgets.QMainWindow):
  def __init__(self, camera, wavemeter,fos_port=0, label='', maxLength=10000, color='red'):
    super().__init__()
    self.cw=QtWidgets.QWidget(); self.setCentralWidget(self.cw) #create and set central widget
    self.layout = QtWidgets.QHBoxLayout(); self.cw.setLayout(self.layout)
    self.leftVerticalLayout = QtWidgets.QVBoxLayout(); self.layout.addLayout(self.leftVerticalLayout)
    self.rightVerticalLayout = QtWidgets.QVBoxLayout(); self.layout.addLayout(self.rightVerticalLayout)

    self.maxLength=maxLength
    self.camera=camera
    if type(wavemeter) == list: self.wavemeter_list=wavemeter
    else: self.wavemeter_list=[wavemeter]
    self.fos_port_list=list(wavemeter.data.keys())[1:]#[i for i in range(1,len(wavemeter.data.keys()))] #update for case of multiple wavemeters
    self.data={port:{"Times":[],"Wavelengths":[]} for port in self.fos_port_list}

    self.fos_port=self.fos_port_list[0]
    self.portViewer=SinglePortViewer(fos_port=self.fos_port, label=f'Port {self.fos_port}',
                                     color="blue", data=[[],[]], maxLength=self.maxLength)
    self.rightVerticalLayout.addLayout(self.portViewer.layout)
    
    self.cameraViewer=CameraViewer(self.camera, maxLength=self.maxLength, color="red")
    self.rightVerticalLayout.addLayout(self.cameraViewer.layout)

    self.histogrammer = LiveHistogramWidget(orientation="vertical")
    self.leftVerticalLayout.addLayout(self.histogrammer.layout)
    self.wmTimer = QtCore.QTimer()
    self.wmTimer.timeout.connect(self.updateWM)
    self.lastTime=time.time()
    self.wmTimer.start(1)

    self.camTimer = QtCore.QTimer()
    self.camTimer.timeout.connect(self.updateCam)
    self.camTimer.start(50)

  def updateWM(self):
    self.readout={}
    for wavemeter in self.wavemeter_list:
      self.readout.update(wavemeter.data)
    for fos_port in self.fos_port_list:
      if self.readout[fos_port]==0: continue#print("huh?", self.readout);continue #0 indicates a failed reading, but blows up as a frequency
      if len(self.data[fos_port]['Times'])>0 and self.readout["time"]==self.data[fos_port]['Times'][-1]:continue #ignore duplicate reading
      self.data[fos_port]['Times']+=[self.readout["time"]]
      self.data[fos_port]['Wavelengths']+=[self.readout[fos_port ]]
      if len(self.data[fos_port]['Times'])>self.maxLength:
        self.data[fos_port]['Times'].pop(0)
        self.data[fos_port]['Wavelengths'].pop(0)
      if fos_port == self.fos_port:
        self.portViewer.addData(self.readout["time"], self.readout[fos_port])
        self.currentTime, self.currentFrequency = self.readout["time"], self.readout[fos_port]
      tt=time.time()
      # print('lag:',tt-self.lastTime)
      self.lastTime=tt

  def updateCam(self):
    self.frame=self.camera.get_latest()
    if not (self.frame is None): 
      self.cameraViewer.update(self.frame)
      self.currentSignal=np.sum(self.frame)
      if self.currentFrequency:
        self.histogrammer.update(299792.458/self.currentFrequency, self.currentSignal)

  def safeExit(self):
    for wm in self.wavemeter_list:
      wm.stop()
    self.histogrammer.exit()


if __name__ == '__main__':
  try:
    wmc=wavemeterClient("10.54.6.156", 5000)
    wmc.start(); print("client running")
  except:
    wmc=dummyWavemeter(num_ports=8)
  with CameraManager() as manager:
    with manager.open_camera(0) as cam1:
      cam1.start()
      print("Starting GUI")

      app = QtWidgets.QApplication(sys.argv)
      window = DAQViewer(cam1, wmc, fos_port=0)
      app.aboutToQuit.connect(window.safeExit)
      window.show()
      sys.exit(app.exec())
      wmc.stop()