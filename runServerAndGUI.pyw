import time
import subprocess
import sys
import signal

# import socket
# def wait_for_port(host, port):
#     while True:
#         try:
#             print('testing port')
#             socket.create_connection((host, port), timeout=1).close()
#             return
#         except OSError:
#             time.sleep(0.2)

server = subprocess.Popen([sys.executable, "WavemeterPublisher.py"])
time.sleep(2)
# wait_for_port("10.54.6.173", 5000)
gui = subprocess.Popen([sys.executable, "wmPlotterGUI.py"])

def shutdown(*args):
    gui.terminate()
    server.terminate()

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

gui.wait()
shutdown()