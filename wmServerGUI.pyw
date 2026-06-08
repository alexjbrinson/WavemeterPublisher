# import pyqtgraph as pg
from wmServer import AppState, WavemeterMultiplexer, SocketServer
import PyQt6 as qt
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIcon
import threading, sys
from datetime import datetime as datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

class ServerGUI(QtWidgets.QMainWindow):
  def __init__(self, state, wm, server):
    super().__init__()
    self.state=state
    self.bcd={True:"green", False:"white"}#button color dictionary, obviously

    self.cw=QtWidgets.QWidget(); self.setCentralWidget(self.cw) #create and set central widget
    self.verticalLayout = QtWidgets.QVBoxLayout(); self.cw.setLayout(self.verticalLayout) #create horizontal layout, add to central widget
    self.topGridLayout=QtWidgets.QGridLayout(); self.verticalLayout.addLayout(self.topGridLayout)
    self.bottomGridLayout=QtWidgets.QGridLayout(); self.verticalLayout.addLayout(self.bottomGridLayout)
    self.pButtonParams=["read", "pid"]
    self.lEditParams=["kp", "ki", "kd", "setpoint", "gain", "offset","vLow","vHigh"]
    self.labelParams=["reading", "error", "output","time"]
    self.params = self.pButtonParams+self.lEditParams+self.labelParams
    self.topGridLayout.addWidget(QtWidgets.QLabel("Parameter"), 0,0)
    for col, ch in enumerate(state.wavePorts.keys(), start=1):
      self.topGridLayout.addWidget(QtWidgets.QLabel(f"Channel {ch+1}"), 0 ,col)
    for row, param in enumerate(self.params, start=1):
      self.topGridLayout.addWidget(QtWidgets.QLabel(param), row, 0)
    self.widgets={}
    self.lastUpdates={}
    for col, ch in enumerate(state.wavePorts.keys(), start=1):
      wp = self.state.wavePorts[ch]
      read_button = QtWidgets.QPushButton(f"Channel {ch+1}\nreadout")
      pid_button = QtWidgets.QPushButton(f"Channel {ch+1}\nPID")
      self.topGridLayout.addWidget(read_button,1,col)
      self.topGridLayout.addWidget(pid_button,2,col)
      self.widgets[(ch, "read")]= read_button
      self.widgets[(ch, "pid")] = pid_button
      
      active_read = wp.active_read
      active_pid = wp.active_pid
      if active_read: read_button.setStyleSheet("background-color: green")
      if active_pid:  pid_button.setStyleSheet("background-color: green")
      read_button.clicked.connect(lambda checked, ch=ch: self.toggleChannelRead(ch))
      pid_button.clicked.connect( lambda checked, ch=ch: self.toggleChannelPID(ch))
      pid_button.setEnabled(active_read)
      for row_offset, parm in enumerate(self.lEditParams, start=1+len(self.pButtonParams)):
        edit = QtWidgets.QLineEdit(str(wp.getParam(parm)))
        self.widgets[(ch, parm)] = edit
        self.topGridLayout.addWidget(edit, row_offset, col)
        edit.returnPressed.connect(lambda ch=ch, param=parm: self.adjustPID(ch, param))
      for row_offset, parm in enumerate(self.labelParams, start=1+len(self.pButtonParams)+len(self.lEditParams)):
        label = QtWidgets.QLabel(str(wp.getParam(f'latest_{parm}')))
        self.widgets[(ch, parm)] = label
        self.topGridLayout.addWidget(label, row_offset, col)
      self.lastUpdates[ch] = wp.last_config
    self.latestTimes=defaultdict(float)
    self.wm = wm
    self.wm_thread=threading.Thread(target=self.wm.run)
    self.server=server
    self.server_thread=threading.Thread(target=self.server.run)
    self.state.running=True
    self.telemetryUpdatesTimer=QtCore.QTimer(self)
    self.telemetryUpdatesTimer.timeout.connect(self.getTelemetry)
    self.configUpdatesTimer=QtCore.QTimer(self)
    self.configUpdatesTimer.timeout.connect(self.checkForConfigUpdates)
    self.telemetryUpdatesTimer.start(5)
    self.configUpdatesTimer.start(100)
    self.wm_thread.start()
    self.server_thread.start()

  def updateGUIParams(self,ch):
    wp = self.state.wavePorts[ch]
    for parm in self.pButtonParams:
      button=self.widgets[ch,parm]
      active=wp.getParam(f'active_{parm}')
      button.setStyleSheet(f"background-color: {self.bcd[active]}")
      if parm=="read":
        self.widgets[ch, "pid"].setEnabled(active)
        if active==False:
          self.widgets[ch, "pid"].setStyleSheet("background-color: white")
          break
    for parm in self.lEditParams:
      text=str(wp.getParam(parm))
      if self.widgets[ch, parm].text()!=text:
        self.widgets[ch, parm].setText(text)

  def checkForConfigUpdates(self):
    # print("checking for config updates")
    for ch, wp in self.state.wavePorts.items():
      if self.lastUpdates[ch]!=wp.last_config:
        print("found an update!")
        self.lastUpdates[ch] = wp.last_config
        self.updateGUIParams(ch)

  def getTelemetry(self):
    readouts = self.state.telemetry_dict()["telemetry"]
    for ch, channelDict in readouts.items():
      for parm in self.labelParams:
        val=channelDict[f"latest_{parm}"]
        if parm=="time" and val:
          dt = val-self.latestTimes[ch]
          if dt==0:break
          self.latestTimes[ch]=val
          text=datetime.fromtimestamp(val).strftime(f'%y-%m-%d\n%I:%M:%S')+f'.{int((val%1)*1000):03d}\ndt={round(dt,3)}'
        elif not (val is None): text=str(round(val,8))
        else: text=""
        if self.widgets[ch, parm].text()!=text:
          self.widgets[ch, parm].setText(text)
    
  def toggleChannelRead(self, ch):
    with self.state.lock:
      wp = self.state.wavePorts[ch]
      active=wp.getParam("active_read")
      wp.updateParams(**{'active_read':not active})
      wp.getParam("active_pid")
    if active: 
      self.widgets[ch, "read"].setStyleSheet("background-color: green")
    else:      
      self.widgets[ch, "read"].setStyleSheet("background-color: white")
      self.widgets[ch, "pid"].setStyleSheet("background-color: white")
    self.widgets[ch, "pid"].setEnabled(active)

  def toggleChannelPID(self, ch):
    button = self.widgets[ch, "pid"]
    with self.state.lock:
      wp = self.state.wavePorts[ch]
      if wp.getParam("active_pid"): wp.disablePID()
      else: wp.enablePID()
      active=wp.getParam("active_pid")
    if active:
      wp.enablePID()
      button.setStyleSheet("background-color: green")
    else:
      wp.disablePID()      
      button.setStyleSheet("background-color: white")

  def adjustPID(self, ch, param): 
    with self.state.lock:
      wp = self.state.wavePorts[ch]
      oldVal = wp.getParam(param)
      try:
        newVal = float(self.widgets[ch, param].text())
      except:
        print('error. Please provide a float.')
        newVal=oldVal
      wp.updateParams(**{param: newVal})
      self.widgets[ch, param].setText(str(wp.getParam(param)))

  def safeExit(self):
    self.state.running=False
    self.server.close()
    self.wm.close()
    self.server_thread.join(timeout=2)
    self.wm_thread.join(timeout=2)
    print("shutdown completed successfully")

  def closeEvent(self, event):
    print("calling safe exit")
    self.safeExit()
    event.accept()

if __name__ == '__main__':
  state = AppState()
  wm = WavemeterMultiplexer(state)
  server=SocketServer(state)
  print("Starting GUI")
  app = QtWidgets.QApplication(sys.argv)
  window = ServerGUI(state, wm, server)
  window.show()
  sys.exit(app.exec())
  wmc.stop()