import socket

HOST = '127.0.0.1'  # Quer dizer que ao rodar .connect(), consigo acessar qualquer endereço da maquina local
PORT = 5001  # Porta para chegada de conexão

# Cria socket
with socket.socket() as sock:
    sock.connect((HOST, PORT))
    while (True):
        # Recebe Input, OBS: "" não entra no recv do servidor, trata caso
        while(True):
            inp = input()
            if(inp != ""):
                break

        if(inp=="fim"):
            break        

        # Manda msg
        sock.sendall(inp.encode('UTF-8'))
        
        # Recebe eco
        data = sock.recv(1024)
        print(f"Received {data.decode('UTF-8')}")
