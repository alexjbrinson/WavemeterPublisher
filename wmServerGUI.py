# import pyqtgraph as pg
from wmServer import AppState, WavemeterMultiplexer, SocketServer
import numpy as np
import PyQt6 as qt
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIcon
import threading, sys

class ServerGUI(QtWidgets.QMainWindow):
  def __init__(self, state, wm, server):
    super().__init__()
    self.state=state


    self.cw=QtWidgets.QWidget(); self.setCentralWidget(self.cw) #create and set central widget
    self.verticalLayout = QtWidgets.QVBoxLayout(); self.cw.setLayout(self.verticalLayout) #create horizontal layout, add to central widget
    self.topGridLayout=QtWidgets.QGridLayout(); self.verticalLayout.addLayout(self.topGridLayout)
    self.bottomGridLayout=QtWidgets.QGridLayout(); self.verticalLayout.addLayout(self.bottomGridLayout)
    pButtonParams=["Read", "PID"]
    lEditParams=["kp", "ki", "kd", "setpoint", "gain", "offset"]
    labelParams=["reading", "error", "output"]
    params = pButtonParams+lEditParams+labelParams
    self.topGridLayout.addWidget(QtWidgets.QLabel("Parameter"), 0,0)
    for col, ch in enumerate(state.wavePorts.keys(), start=1):
      self.topGridLayout.addWidget(QtWidgets.QLabel(f"Channel {ch+1}"), 0 ,col)
    for row, param in enumerate(params, start=1):
      self.topGridLayout.addWidget(QtWidgets.QLabel(param), row, 0)
    self.widgets={}

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
      for row_offset, parm in enumerate(lEditParams, start=1+len(pButtonParams)):
        edit = QtWidgets.QLineEdit(str(wp.getParam(parm)))
        self.widgets[(ch, parm)] = edit
        self.topGridLayout.addWidget(edit, row_offset, col)
        edit.returnPressed.connect(lambda ch=ch, param=parm: self.adjustPID(ch, param))
      for row_offset, parm in enumerate(labelParams, start=1+len(pButtonParams)+len(lEditParams)):
        label = QtWidgets.QLabel(str(wp.getParam(f'latest_{parm}')))
        self.widgets[(ch, parm)] = label
        self.topGridLayout.addWidget(label, row_offset, col)

    self.wm = wm
    self.wm_thread=threading.Thread(target=self.wm.run)
    self.server=server
    self.server_thread=threading.Thread(target=self.server.run)
    self.state.running=True
    self.wm_thread.start()
    self.server_thread.start()
    
  def toggleChannelRead(self, ch):
    button = self.widgets[ch, "read"]
    with self.state.lock:
      wp = self.state.wavePorts[ch]
      wp.active_read = not wp.active_read
      active=wp.active_read
    if active: button.setStyleSheet("background-color: green")
    else:      button.setStyleSheet("background-color: white")

  def toggleChannelPID(self, ch):
    button = self.widgets[ch, "pid"]
    with self.state.lock:
      wp = self.state.wavePorts[ch]
      if wp.active_pid: wp.disablePID()
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
    self.widgets[ch, param].setText(str(newVal))

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