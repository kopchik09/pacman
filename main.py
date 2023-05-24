import socket
import time
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(False)
main_socket.listen(5)
print('сокет создан')
players = []
while True:
    try:
        new_socket, addr = main_socket.accept()
        print(f'подключился {addr}')
        main_socket.setblocking(False)
        players.append(new_socket)
    except BlockingIOError:
        pass
    for i in players:
        try:
            data = i.recv(1024).decode()
            print(f'получил: {data}')
        except:
            pass
    for sock in players:
        try:
            sock.send('штукатурка'.encode())
        except:
            players.remove(sock)
            sock.close()
            print('сокет закрыт')
        
    
    time.sleep(0.01)

