import socket
import time
import pygame
import pygame as pg
import math
import tkinter
from tkinter import ttk
import tkinter.messagebox

colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 
        'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 
        'SandyBrown', 'DarkOrange', 'Orange', 'DarkGoldenrod', 
        'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen',
        'GreenYellow', 'Chartreuse', 'LawnGreen',
        'Green', 'Lime', 'Lime Green', 'SpringGreen', 
        'MediumSpringGreen', 'Turquoise', 'LightSeaGreen', 
        'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 
        'Dark Turquoise', 'DeepSkyBlue', 'DodgerBlue', 'RoyalBlue',
        'Navy', 'DarkBlue', 'MediumBlue.']
def scroll(e):
    global color
    color = combo_box.get()
    style.configure("TCombobox", fieldbackground = color, background = 'white')
def login():
    global name
    name = name_input.get()
    if name and color:
        root.destroy()
        root.quit()
    else:
        tkinter.messagebox.showerror('ошибка', 'вы не выбрали цвет или имя')
name = ''
color = ''
root = tkinter.Tk()
root.title('вход')
root.geometry("300x200")
style = ttk.Style()
style.theme_use('clam')
name_lbl = tkinter.Label(root, text='введите своё имя')
name_lbl.pack()
name_input = tkinter.Entry(root, width=30, justify='center')
name_input.pack()
combo_box = ttk.Combobox(root, values = colors, textvariable = color)
combo_box.bind('<<ComboboxSelected>>', scroll)
combo_box.pack()
btn = tkinter.Button(root, text = 'войти', command = login)
btn.pack()
root.mainloop()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))
sock.send((color).encode())
pygame.init()
#sock.send(name.encode())
print(color)
#print(name)
height = 500
width = 500
yellow = (255, 255, 0)
black = (0, 0, 0)
blue = (0, 0, 255)
x = 0
y = 0
xcor = 250
ycor = 250
old = (0, 0)
cc = width/2, height/2
radius = 50
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('пакман онлайн')
run = True
players = []
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

#       if event.type==pg.KEYDOWN:
#           if event.key==pg.K_LEFT:
#               x=-10
#               y=0
#           if event.key==pg.K_RIGHT:
#               x=10
#               y=0
#           if event.key==pg.K_UP:
#               x=0
#               y=-10
#           if event.key==pg.K_DOWN:
#               x=0
#               y=10
    if pygame.mouse.get_focused():
        pos = pygame.mouse.get_pos()
        vector = pos[0] - cc[0], pos[1] - cc[1]
        lenvector = math.sqrt(vector[0]**2 + vector[1]**2)
        vector = vector[0]/lenvector, vector[1]/lenvector
        if lenvector <= radius:
            vector = 0, 0
        if vector != old:
            old = vector
            message = f'{vector[0]}, {vector[1]}'
            sock.send(message.encode())
            
    # sock.send('лукас'.encode())
    data = sock.recv(1024).decode()
    screen.fill(black)
    pygame.draw.circle(screen, color, cc, radius)
    pygame.display.update()


pygame.quit()
