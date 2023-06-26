import socket
import time
from data.players import Player
from data.db_session import global_init, create_session
import pygame

black = (0, 0, 0)
def find(vector:str):
    if vector == '':
        return ''
    vector_split = vector.split(',')
    #print(float(vector_split[0]), float(vector_split[1]))
    result = list(map(float, vector.split(',')))
    return result

class LocalPlayer:
    def __init__(self, id, name, color, adress, socket):
        self.id = id
        self.adress = adress
        self.name = name
        self.color = color
        self.socket = socket
        self.x = 500
        self.y = 500
        self.speed_y = 0
        self.speed_x = 0
        self.speed_abs = 1
        self.w_vision = 800
        self.h_vision = 600
        self.error = 0
        self.size = 50
        self.db: Player = create_session().get(Player, self.id )

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def change_speed(self, vector):
        vector = find(vector)
        #print(vector)
        if vector[0] and vector[1] == 0:
            self.speed_x = self.speed_y = 0
        else:
            vector = vector[0] * self.speed_abs, vector[1] * self.speed_abs
            self.speed_x = vector[0]
            self.speed_y = vector[1]

        


global_init('db.sqlite')
pygame.init()
height_map = 4000
widht_map = 4000
height_server = 300
width_server = 300
screen = pygame.display.set_mode((width_server, height_server))
pygame.display.set_caption('пакман онлайн')
clock = pygame.time.Clock()
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(False)
main_socket.listen(5)
db_session = create_session()
print('сокет создан')
players = {}
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    dt = clock.tick()/1000

    try:

        new_socket, addr = main_socket.accept()
        print(f'подключился {addr}')
        main_socket.setblocking(False)
        color = new_socket.recv(1024).decode()
        #name = new_socket.recv(1024).decode()
        print(color)
        name = 'sda'
        #print(name)
        addr = f'({addr[0]}, {addr[1]})'
        player = Player(name, addr)
        player.name = name
        player.color = color
        db_session.merge(player)
        db_session.commit()
        user = db_session.query(Player).filter(Player.adress == addr).first()
        player = LocalPlayer(user.id, name, color, addr, new_socket)
        players[user.id] = player


    except BlockingIOError:
        pass
    for id in list(players):
        try:
            
            data = players[id].socket.recv(1024).decode()
            #print(f'получил: {data}')
            players[id].change_speed(data)
        except:
            pass
    for id in list(players):
        try:
            players[id].socket.send('штукатурка'.encode())
        except:
            players[id].socket.close()
            del players[id]

            db_session.query(Player).filter(Player.id == id).delete()
            db_session.commit()
            print('сокет закрыт')   
    screen.fill(black)
    for id in players:
        player = players[id]
        player.update()
        #print(player.speed_x, player.speed_y)
        x = player.x * width_server//widht_map
        y = player.y * height_server//height_map
        size = player.size * height_server//height_map
        pygame.draw.circle(screen, player.color, (x, y), size)
        pygame.display.update()

pygame.quit()
main_socket.close()
db_session.query(Player).delete()
db_session.commit()