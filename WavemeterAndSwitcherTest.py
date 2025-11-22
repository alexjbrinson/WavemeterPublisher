from mcculw import ul
from mcculw.enums import DigitalIODirection, ULRange, BoardInfo, DigitalIODirection
from Bristol.pyBristolSCPI import pyBristolSCPI
from Bristol.digital import DigitalProps, PortInfo
import time
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':

    #wavemeter instantiation
    wavemeter=pyBristolSCPI()
    #switcher instantiation:
    board_num=0
    digital_props=DigitalProps(board_num)
    # Find the first port that supports output, defaulting to None if one is not found.
    port = next(
            (port for port in digital_props.port_info
             if port.supports_output), None)
    if port == None:
        print("unsupported board")
        print(-1)
    if port.is_port_configurable:
        ul.d_config_port(board_num, port.type, DigitalIODirection.OUT)

    port_value = 0
    print("change to channel {}".format(port_value + 1))
    ul.d_out(board_num, port.type, port_value)
    wl=wavemeter.readWL()
    print('wavelength = {}'.format(wl))

    channel_index=0
    fos_ports=[0,1]
    num_ports=len(fos_ports)
    laser_logs=[]
    t0=time.perf_counter()
    nn=100
    for ii in range(nn):
        timeArray=[time.time()]
        readout=[timeArray[0]]
        for port_value in fos_ports:
            ul.d_out(board_num, port.type, port_value)
            timeArray+=[time.time()]
            time.sleep(.004)
            timeArray+=[time.time()]
            wl=wavemeter.readWL()
            timeArray+=[time.time()]
            # print(f"channel {port_value+1}: {wl}nm")
            readout+=[wl]
        print("Timings:", [timeArray[i+1]-timeArray[i] for i in range(len(timeArray)-1)], timeArray[-1]-timeArray[0])
        laser_logs+=[readout]
    t1=time.perf_counter()
    print(f"time_elapsed: {(t1-t0)/nn} per read cycle")
    
    laser_logs=np.array(laser_logs)
    # print(laser_logs)
    ul.d_out(board_num, port.type, 1)
    for ii in range(num_ports):
        plt.plot(laser_logs[:,ii+1])
    plt.show()