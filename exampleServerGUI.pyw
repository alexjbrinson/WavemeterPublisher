from wmLib.wmServer import AppState, WavemeterSinglet, WavemeterMultiplexer, SocketServer
from wmLib.wmServerGUI import ServerGUI
from PyQt6 import QtWidgets
import sys

if __name__ == '__main__':
  state = AppState()
  wm0=WavemeterSinglet(state, host='1.1.1.5', config='config/369Config.json')
  wm = WavemeterMultiplexer(state, config="config/switcherConfig.json")
  server=SocketServer(state)
  print("Starting GUI")
  app = QtWidgets.QApplication(sys.argv)
  window = ServerGUI(state, wm, server)
  window.show()
  sys.exit(app.exec())