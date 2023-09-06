import random
import socket
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import pygame
from data.db_session import global_init, create_session
from data.players import Player
from russian_names import RussianNames
import math

colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']

MOBS_QUANTITY = 25

names = RussianNames(count = MOBS_QUANTITY * 2, patronymic = False, surname = False, rare = True)
names = list(set(names))

engine = create_engine(f"sqlite:///db.sqlite?check_same_thread=False")
#engine = create_engine("postgresql+psycopg2://postgres:sas@localhost/rebotica")
Session = sessionmaker(bind=engine)
Base = declarative_base()
s = Session()

# Настройка констант для pygame
pygame.init()
WIDHT_ROOM, HEIGHT_ROOM = 4000, 4000
WIDHT_SERVER, HEIGHT_SERVER = 300, 300
FPS = 100

# Создание окна сервера
screen = pygame.display.set_mode((WIDHT_SERVER, HEIGHT_SERVER))
pygame.display.set_caption("Сервер")
clock = pygame.time.Clock()


def find(vector: str):
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = list(map(float, vector[first + 1:second].split(",")))
            return result
    return ""
def my_found(vector: str):
    res = list(map(float, vector.split(',')))
    return res

def find_color(info: str):
    first = None
    for num, sign in enumerate(info):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = info[first + 1:second].split(",")
            return result
    return ""


# Декларативный класс таблицы игроков
class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=1)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)
    color = Column(String(250), default="red")  # Добавили цвет
    w_vision = Column(Integer, default=800)
    h_vision = Column(Integer, default=600)  # Добавили размер квадрат

    def __init__(self, name, address):
        self.name = name
        self.address = address


# Локальный класс таблицы игроков
class LocalPlayer:
    def __init__(self, id, name, sock, addr):
        self.id = id
        self.db: Player = s.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0
        self.color = "red"
        self.w_vision = 800
        self.h_vision = 600

    def update(self):
        if self.x - self.size <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        elif self.x + self.size >= WIDHT_ROOM:
            if self.speed_x <= 0:
                self.x += self.speed_x
        else:
            self.x += self.speed_x

        if self.y - self.size <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        elif self.y + self.size >= HEIGHT_ROOM:
            if self.speed_y <= 0:
                self.y += self.speed_y
        else:
            self.y += self.speed_y

    def change_speed(self, vector):
        vector = my_found(vector)
        if vector[0] == 0 and vector[1] == 0:
            self.speed_x = self.speed_y = 0
        else:
            vector = vector[0] * self.abs_speed, vector[1] * self.abs_speed
            self.speed_x = vector[0]
            self.speed_y = vector[1]

    def eat(self):
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
        if distance <= p1.size and p1.size > 1.1 * p2.size:
            p2.size, p2.speed_x, p2.speed_y = 0, 0, 0
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
        if distance <= p2.size and p2.size > 1.1 * p1.size:
            p1.size, p1.speed_x, p1.speed_y = 0, 0, 0

    def load(self):
        self.size = self.db.size
        self.abs_speed = self.db.abs_speed
        self.speed_x = self.db.speed_x
        self.speed_y = self.db.speed_y
        self.errors = self.db.errors
        self.x = self.db.x
        self.y = self.db.y
        self.color = self.db.color
        self.w_vision = self.db.w_vision
        self.h_vision = self.db.h_vision
        return self

    def sync(self):
        self.db.size = self.size
        self.db.abs_speed = self.abs_speed
        self.db.speed_x = self.speed_x
        self.db.speed_y = self.speed_y
        self.db.errors = self.errors
        self.db.x = self.x
        self.db.y = self.y
        self.db.color = self.color
        self.db.w_vision = self.w_vision
        self.db.h_vision = self.h_vision
        s.merge(self.db)
        s.commit()


Base.metadata.create_all(engine)


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Настраиваем сокет
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Отключаем пакетирование
main_socket.bind(("localhost", 10000))  # IP и порт привязываем к порту
main_socket.setblocking(False)  # Непрерывность, не ждём ответа
main_socket.listen(5)  # Прослушка входящих соединений, 5 одновременных подключений
print("Сокет создался")

players = {}

for i in range(MOBS_QUANTITY):
    bot = Player(names[i], None)
    bot.color = random.choice(colors)
    bot.x, bot.y = random.randint(0, WIDHT_ROOM), random.randint(0, HEIGHT_ROOM)
    bot.speed_x, bot.speed_y = random.randint(-1, 1), random.randint(-1, 1)
    bot.size = random.randint(10, 100)
    s.add(bot)
    s.commit()
    local_bot = LocalPlayer(bot.id, bot.name, None, None).load()
    players[bot.id] = local_bot



server_works = True
tick = -1
while server_works:
    clock.tick(FPS)
    tick += 1
    if tick % 200 == 0:

        try:
            # проверяем желающих войти в игру
            new_socket, addr = main_socket.accept()  # принимаем входящие
            print('Подключился', addr)
            new_socket.setblocking(False)
            login = new_socket.recv(1024).decode()
            player = Player("Имя", f'({addr[0]},{addr[1]})')
            player.name, player.color = login.split(',')

            s.merge(player)
            s.commit()

            addr = f'({addr[0]},{addr[1]})'
            data = s.query(Player).filter(Player.address == addr)
            for user in data:
                player = LocalPlayer(user.id, "Имя", new_socket, addr).load()
                players[user.id] = player

        except BlockingIOError:
            pass

    # Считываем команды игроков
    for id in list(players):
        if players[id].sock is not None:
            try:
                data = players[id].sock.recv(1024).decode()
                print("Получил", data)
                players[id].change_speed(data)
            except:
                pass
        else:
            if tick % 400 == 0:
                vector = f'{random.randint(-1, 1)}, {random.randint(-1, 1)}'
                players[id].change_speed(vector)
    # Определим, что видит каждый игрок
    visible_bacteries = {}


    
    for id in list(players):
        if players[id].errors >= 500 or players[id].size == 0:
            if players[id].sock is not None:
                players[id].sock.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit
        visible_bacteries[id] = []

    pairs = list(players.items())
    for i in range(0, len(pairs)):
        for j in range(i + 1, len(pairs)):
            # Рассматриваем пару игроков
            p1: Player = pairs[i][1]
            p2: Player = pairs[j][1]
            dist_x = p2.x - p1.x
            dist_y = p2.y - p1.y

            if abs(dist_x) <= p1.w_vision//2 + p2.size and abs(dist_y) <= p1.h_vision//2 + p2.size:
                if players[id].sock is not None:
                    data = f'{round(dist_x)} {round(dist_y)} {round(p2.size)} {p2.color}'
                    visible_bacteries[p1.id].append(data)
            if abs(dist_x) <= p2.w_vision//2 + p1.size and abs(dist_y) <= p2.h_vision//2 + p1.size:
                if players[id].sock is not None:
                    data = f'{round(-dist_x)} {round(-dist_y)} {round(p1.size)} {p1.color}'
                    visible_bacteries[p2.id].append(data)

    # Формируем ответ каждой бактерии
    for id in list(players):
        visible_bacteries[id] = "<" + ",".join(visible_bacteries[id]) + ">"

    # Отправляем статус игрового поля
    for id in list(players):
        if players[id].sock is not None:
            try:
                players[id].sock.send(visible_bacteries[id].encode())
            except:
                players[id].sock.close()
                del players[id]
                # Так же удаляем строчку из БД
                s.query(Player).filter(Player.id == id).delete()
                s.commit()
                print("Сокет закрыт")

    # Отрисовываем серверное окно
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

    screen.fill('black')
    for id in list(players):
        player = players[id]
        x = player.x * WIDHT_SERVER // WIDHT_ROOM
        y = player.y * HEIGHT_SERVER // HEIGHT_ROOM
        size = player.size * WIDHT_SERVER // WIDHT_ROOM
        pygame.draw.circle(screen, player.color, (x, y), size)  # Цвет

    for id in list(players):
        player = players[id]
        players[id].update()

    pygame.display.update()

pygame.quit()
main_socket.close()
s.query(Player).delete()
s.commit()
