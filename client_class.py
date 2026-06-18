import socket, json, time, threading
from collections import defaultdict, deque

class wavemeterClient():
    def __init__(self, host, port):
        self.host=host; self.port=port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(1)
        self.client_socket.connect((self.host, self.port))
        self.socket_lock = threading.Lock()
        self.leftover=''
        self.lastTimeStamp=-1
        self.reading=False
        self.data = {}
        self.config={}
        self.times=defaultdict(float)
        self.other_lock=threading.Lock()
        self.buffers = {ch: deque(maxlen=100000) for ch in range(1,9)}

    def make_query(self):
        new_data={}
        new_config={}
        dt=0
        t0=time.perf_counter()
        command = {"cmd":"GET"}
        request=(json.dumps(command)+'\n').encode()
        self.client_socket.send(request);
        received=self.leftover
        while "\n" not in received:
            packet=self.client_socket.recv(4096).decode()#recv(4)
            received+=packet
        received, leftover = received.split('\n',1)
        message=json.loads(received)
        if message['type']!='total':return
        messData=message["data"]
        for ch, wp in messData["telemetry"].items():new_data[int(ch)] = wp
        for ch, wp in messData["config"].items():new_config[int(ch)] = wp
        
        with self.socket_lock:
           self.leftover=leftover
           self.data = new_data
           self.config=new_config
        dt+=time.perf_counter()-t0
        # print("time elapsed:", dt)
        # return(self.data)
    def request_change(self, ch, **kwargs):
      command = {"cmd"    :"SET",
                 "channel":ch,
                 "change" :kwargs}
                #  "param"  :param,
                #  "value"  :value}
      request=(json.dumps(command)+'\n').encode()
      with self.socket_lock:
        self.client_socket.send(request)
      pass
    def get_new_samples(self, ch):
      with self.other_lock:
        samples=list(self.buffers[ch])
        self.buffers[ch].clear()
      return samples
    
    def get_config(self):
        new_config={}
        dt=0
        t0=time.perf_counter()
        command = {"cmd":"CONFIG"}
        request=(json.dumps(command)+'\n').encode()
        self.client_socket.send(request);
        received=self.leftover
        while "\n" not in received:
            packet=self.client_socket.recv(4096).decode()#recv(4)
            received+=packet
        received, leftover = received.split('\n',1)
        message=json.loads(received)
        if message['type']!='config':return
        messData=message["data"]
        for ch, wp in messData["config"].items():
          new_config[int(ch)] = wp
        with self.socket_lock:
           self.leftover=leftover
           self.config = new_config
        dt+=time.perf_counter()-t0
        # print("time elapsed:", dt)
        # return(self.data)

    def continuous_readout(self):
      while self.reading: self.make_query()
    def start(self):
      self.reading=True
      self.make_query()
      self.readout_thread=threading.Thread(target=self.continuous_readout, daemon=True)
      self.readout_thread.start()
    def stop(self):
      self.reading=False
      self.readout_thread.join()
      self.data={}

class dummyWavemeter():
  def __init__(self, num_ports=1):
    self.num_ports=num_ports
    self.start()

  def make_query(self):
    self.data={"time":time.time()}
    for key in range(1,self.num_ports+1):
      self.data[key] = -1

  def continuous_readout(self):
    while self.reading:
      self.make_query()
      time.sleep(.03)

  def start(self):
      self.reading=True
      self.make_query()
      self.readout_thread=threading.Thread(target=self.continuous_readout)
      self.readout_thread.start()
      
  def stop(self):
      self.reading=False
      self.readout_thread.join()
      self.data={}
        

if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore
    # wmc=wavemeterClient("10.54.6.173", 5000)
    wmc=wavemeterClient("10.54.6.156", 5000)
    wmc.start(); print("client running")
    wmc.get_config()
    print(wmc.config)
    for i in range(100):
        # print(wmc.data[1])
        # print(wmc.data[2])
        time.sleep(0.01)
    # wmc.stop()
    # print("this", wmc.data)
    quit()
    app = pg.mkQApp("Wavemeter Logger")
    win = pg.GraphicsLayoutWidget(show=True, title="Wavemeter Readouts")
    win.resize(1000,600)
    p1=win.addPlot(title="Port 2")
    data=[]
    curve = p1.plot(pen="y")
    def update():
        global data
        data+=[wmc.data[1]["latest_reading"]]
        if len(data)>1000:data.pop(0)
        curve.setData(data)
    
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1)
    pg.exec()
    quit()
