import socket
import numpy as np

def server_program():
    print(f"Server listening on {host}:{port}")
    conn, address = server_socket.accept()  # Accept a new connection
    print(f"Connection from: {address}")

    i=0
    while True:
        try:
            input=int(conn.recv(1024).decode())
            print('input:',input)
            data=np.array([input**2,i])
            message="".join([str(datum)+"," for datum in data]).rstrip(',')+'\n'
            print(message)
            conn.send(message.encode())  # Send data back to the client
            i+=1
        except:
            conn.close()
            server_program()
    conn.close()
    server_socket.close()

if __name__ == '__main__':
    # Get the hostname (or use '0.0.0.0' to listen on all available interfaces)
    host = socket.gethostname()  
    port = 5000  # Arbitrary non-privileged port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Listen for up to 2 incoming connections

    server_program()