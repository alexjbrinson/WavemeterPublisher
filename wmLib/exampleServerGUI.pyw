from wmLib.wmServer import AppState, WavemeterSinglet, WavemeterMultiplexer, SocketServer
from wmLib.wmServerGUI import ServerGUI
from PyQt6 import QtWidgets
import sys

if __name__ == '__main__':
  from platformdirs import user_config_dir
  from pathlib import Path
  config_dir = Path(user_config_dir("WavemeterConfigs", "wmLib"))
  config_dir.mkdir(parents=True, exist_ok=True)
  state = AppState()
  wm0=WavemeterSinglet(state, host='1.1.1.5', config=config_dir/'singletConfig.json')
  wm = WavemeterMultiplexer(state,            config=config_dir/'switcherConfig.json')
  server=SocketServer(state)
  print("Starting GUI")
  app = QtWidgets.QApplication(sys.argv)
  window = ServerGUI(state, wm, server)
  window.show()
  sys.exit(app.exec())