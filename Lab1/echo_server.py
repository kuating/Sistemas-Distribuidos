import socket

HOST = "127.0.0.1"
PORT = 5001

with socket.socket() as sock:
    sock.bind((HOST, PORT))
    sock.listen()
    conn, addr = sock.accept()
    with conn:
        print(f"Connected by {addr}")
        while (True):
            data = conn.recv(1024)
            if not data:
                break
            print(f"Recieved {data.decode('UTF-8')}, sending back...")
            conn.sendall(data)
