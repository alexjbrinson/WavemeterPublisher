from mcculw import ul
from mcculw.enums import DigitalIODirection, ULRange, BoardInfo, DigitalIODirection
from Bristol.pyBristolSCPI import pyBristolSCPI
from Bristol.digital import DigitalProps, PortInfo
import time
import matplotlib.pyplot as plt
import socket
import threading

def server_program(host, port, fos_ports=[0]):
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
    if port.is_port_configurable: ul.d_config_port(board_num, port.type, DigitalIODirection.OUT)
    print(f"Server listening on {host}:{port}")
    conn, address = server_socket.accept()  # Accept a new connection
    print(f"Connection from: {address}")
    while True:
        t0=time.time()
        try:
            input=int(conn.recv(1024).decode())
            print('input:',input)
            laser_logs=[time.time()]
            for port_value in fos_ports:
                ul.d_out(board_num, port.type, port_value) #switching FOS port
                time.sleep(.005)#this is how I'm implementing a switching delay 
                laser_logs+=[wavemeter.readWL()] #reading wavemeter
            message="".join([str(datum)+"," for datum in laser_logs]).rstrip(',')+'\n'
            conn.send(message.encode())  # Send data back to the client
            # print("data: ", data)
            # print("message:", message)
        except: break
        t1=time.time()
        print('time elapsed:', t1-t0)
    wavemeter.tn.close()
    conn.close()
    server_program(host, port, fos_ports=fos_ports)

if __name__ == '__main__':
     # Get the hostname (or use '0.0.0.0' to listen on all available interfaces)
    host = socket.gethostname()  
    port = 5000  # Arbitrary non-privileged port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Listen for up to 2 incoming connections
    fos_ports=[0,1]

    # server_thread = threading.Thread(target=server_program, args=(host,port), kwargs={'fos_ports':fos_ports})
    # server_thread.start()
    server_program(host, port, fos_ports=[0,1])
