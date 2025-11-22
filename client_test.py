import socket
import time
import numpy as np
import matplotlib.pyplot as plt

def client_program():
    host = socket.gethostname()  # Use the same hostname as the server
    port = 5000  # Use the same port as the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # message = input("Enter message to send to server: ")
    dataList=[]
    leftover=''
    i=0
    lastTimeStamp=0
    while len(dataList)<=100:#message.lower().strip() != 'bye':
        t0=time.perf_counter()
        # client_socket.send(message.encode())  # Send the message
        request=str(i).encode()
        client_socket.send(request); i+=1
        message=leftover
        while "\n" not in message:
            packet=client_socket.recv(4).decode()
            message+=packet
        # time.sleep(1)
        message,leftover = message.split('\n')
        message=message.split(",")
        timestamp=message[0]
        if timestamp==lastTimeStamp: continue
        print(message)
        lastTimeStamp=timestamp
        data = [float(datum) for datum in message]
        dataList+=[data]
        t1=time.perf_counter()
        print("time elapsed:", t1-t0)
    datArray=np.array(dataList)
    # print("dataList:\n", np.array(dataList))
    client_socket.close()
    label_list=['time', '399nm', '780nm', 'off']
    for ii in range(1,len(datArray[0,:])):
        plt.plot(datArray[:,0], datArray[:,ii],'-', label=label_list[ii])
    # print(datArray[0])
    plt.title("wm readouts, with 4ms switching delay,\nlive channels only")
    plt.xlabel('epoch time (s)')
    plt.ylabel(r'$\lambda$ (nm)')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    client_program()