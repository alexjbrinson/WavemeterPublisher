from mcculw import ul
from mcculw.enums import DigitalIODirection, ULRange, BoardInfo, DigitalIODirection, DigitalPortType
from Bristol.pyBristolSCPI import pyBristolSCPI
from Bristol.digital import DigitalProps, PortInfo
from Bristol.PID.daq import DAQ as PID_DAQ
import time
import matplotlib.pyplot as plt
import socket
import threading
import wmPlotterGUI as GUI

mlc_map = {0:(0,4),
           1:(1,4),
           2:(0,2),
           3:(1,2),
           4:(0,1),
           5:(1,1),
           6:(0,3),
           7:(1,3)}
setpoints={0:398.91111876,
           1:760,
           2:935,
           3:780,
           4:0,
           5:787.62484,
           6:0,
           7:0}
pidVals=  {0:(1000,0,0),
           1:(1,0,0),
           2:(1,0,0),
           3:(1,0,0),
           4:(1,0,0),
           5:(100,10,0),
           6:(1,0,0),
           7:(1,0,0)}
laser_lock = threading.Lock()
def handle_client(conn, address):
  print(f"Connection from: {address}")
  try:
    # data = conn.recv(1024)
    # if data.decode().strip() == "ping":
      # conn.send(b"ready")
      # return
    while True:
      data = conn.recv(1024)
      if not data:
          break
      #data.decode()  # Eventually, actually cater to client's request
      with laser_lock:
        message=''.join([f'{key}:{laser_logs[key]},' for key in laser_logs.keys()]).rstrip(',') + '\n'
      conn.send(message.encode())
  except Exception as e:
    print(f"Client {address} error: {e}")
  finally:
    conn.close()
    print(f"Connection closed: {address}")

def server_program(host, port, fos_ports=[0]):
    print(f"Server listening on {host}:{port}")
    while True:
        conn, address = server_socket.accept()  # Accept a new connection
        print(f"Connection from: {address}")
        client_thread = threading.Thread(target=handle_client, args=(conn, address), daemon=True)
        client_thread.start()  # Handle the client connection in a new thread

def wavemeter_multiplexer(fos_ports):
    global laser_logs
    print('fos_ports:',fos_ports)

    #wavemeter instantiation
    wavemeter=pyBristolSCPI()

    #switcher instantiation:
    board_num=0 
    digital_props=DigitalProps(board_num)
    # Find the first port that supports output, defaulting to None if one is not found.
    port = next(
            (port for port in digital_props.port_info
             if port.supports_output), None)
    if port == None: print("unsupported board"); return(-1)
    # print(port.type)
    if port.is_port_configurable: ul.d_config_port(board_num, port.type, DigitalIODirection.OUT)

    #pid calculator instantiation
    pid_daq = PID_DAQ()
    for port_value in fos_ports:
       pid_daq.setSetPoint(setpoints[port_value], port_value)
       kp,ki,kd = pidVals[port_value]
       pid_daq.setKp(kp, port_value);pid_daq.setKi(ki, port_value);pid_daq.setKd(kd, port_value);
    print("Reached loop")
    now=time.time();then=now
    while True:
        try:
          laser_logs_temp={'time':time.time()}
          for port_value in fos_ports: 
              # print(f"switching to port {port_value}")
              ul.d_out(board_num, port.type, port_value) #switching FOS port
              if len(fos_ports)>1: time.sleep(.025)#this is how I'm implementing a switching delay
              readout=wavemeter.readWL() #reading wavemeter
              # error, voltage = pid_daq.computePID((*mlc_map[port_value],port_value),readout)
              # if port_value==5: print(port_value, readout, error, voltage)
              laser_logs_temp[port_value+1]=readout
          with laser_lock: laser_logs = laser_logs_temp
          # now=time.time(); print("dt=",now-then); then=now
          # print(laser_logs)
        except Exception as e:
          print("Wavemeter thread crashed:", e)
          import traceback
          traceback.print_exc()
          # break
    wavemeter.tn.close()

if __name__ == '__main__':
  fos_ports=[0,1,2,3,5]#,1,2,3]#0
   # Get the hostname (or use '0.0.0.0' to listen on all available interfaces)
  host = '0.0.0.0'#socket.gethostname()  
  port = 5000  # Arbitrary non-privileged port

  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((host, port))
  server_socket.listen(2)  # Listen for up to 2 incoming connections

  wm_thread = threading.Thread(target=wavemeter_multiplexer, args=(fos_ports,))
  server_thread = threading.Thread(target=server_program, args=(host,port), kwargs={'fos_ports':fos_ports})
  wm_thread.start()
  server_thread.start()