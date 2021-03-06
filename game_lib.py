#All libraries for game will be here
#yayuz
import socket
from time import sleep
import pygame
import os
import sys
import threading

#menu_nav scripts
class menu(pygame.Surface):
    def __init__(self, width, height):
        "Initalizes menu with the start screen"
        pygame.Surface.__init__(self, size=(width, height))
        self.state = 0
        self.bg_img = pygame.image.load(misc_img_dir+"stars1.png")
        self.play_button = Button(misc_img_dir+"testbutton.png", (200, 200), "play")
        self.play_button_text = self.play_button.add_text("Play", 32)
        self.instruct_button = Button(misc_img_dir+"testbutton.png", (400, 200), "instructions")
        self.instruct_button_text = self.instruct_button.add_text("Instructions", 20)
        self.buttons = pygame.sprite.LayeredUpdates()
        self.buttons.add(self.play_button, self.instruct_button)

    def instructions(self):
        "Sets menu screen to instructions"
        self.state = 1

    def settings(self):
        "Sets menu screen to settings"
        pass

    def credits(self):
        "Sets menu screen to settings"
        pass

    def back(self):
        "Goes back to previous screen"
        pass

    def star_map(self, key_input):
        "Shows the scrolling star map and passes key_input to it"
        pass

    def render(self, display):
        "Renders the menu on the dislay"
        if self.state == 0:
            self.blit(self.bg_img, (0,0))
            display.blit(self, (0,0))
            self.buttons.draw(display)
            display.blit(self.play_button_text,
             (int((self.play_button.return_pos())[0])+ int((self.play_button.return_rect())[2]//2),
             int((self.play_button.return_pos())[1])+ int((self.play_button.return_rect())[3]//2)))

            display.blit(self.instruct_button_text,
             (int(self.instruct_button.return_pos()[0])+ int((self.instruct_button.return_rect())[2]//2),
              int(self.instruct_button.return_pos()[1])+int((self.play_button.return_rect())[3]//2)))


    def handle_mouse(self, mouse):
        "Passes mouse tuple to buttons currently drawn on menu"
        sprite_list = []
        for sprite in self.buttons:
            test = sprite.ifclick(mouse)
            if test:
                return test

class Button(pygame.sprite.Sprite):
    def __init__(self, img_path, pos, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.place = pos
        self.name = name

    def ifclick(self, mouse):
        "Returns the name of the mouse that was clicked"
        if mouse[0] == 1:
            if ((mouse[1] > self.rect.left) and (mouse[1] < self.rect.right)) and ((mouse[2] < self.rect.bottom) and (mouse[2] > self.rect.top)):
                return self.name

    def add_text(self, text, size):
        "Returns a text surface that will be rendered over the button"
        self.text = text
        self.font = pygame.font.Font("freesansbold.ttf", size)
        self.text_surf = self.font.render(self.text, False, BLACK)
        return self.text_surf

    def return_pos(self):
        "Returns the position attribute"
        return self.place

    def return_rect(self):
        "returns a tuple of (x_pos, y_pos, width, height)""
        return self.rect

#Networking classes
#In progress networking classes
class Server:
    def __init__(self, timeout, max_users):
        socket.setdefaulttimeout(timeout)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = game_port
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)
        self.sock.bind((self.ip, game_port))
        self.sock.listen(max_users)
        self.addresses = []
        self.conns = []

    def work(self):
        "Function that will be run and maintains connections between each Client and is run by thread"
        try:
            c, addr = self.sock.accept()
            self.addresses.append(addr)
            self.conns.append(c)
        except:
            pass


    def recieve(self, connection):
        "Recieves a message from the connection"
        data = connection.recv(1024)
        data = data.decode()
        return data

    def myInfo(self):
        "Returns info about the socket"
        return (self.addresses, (self.host_name, self.ip, self.port))

    def myConns(self):
        "Returns server connections"
        return self.conns

    def broadcast(self, msg):
        "Broadcasts a message to all clients"
        self.sock.sendall(msg.encode())

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = game_port
        self.host = socket.gethostname()
        #Two connection methods self.connect((ip, port)) or self.create_connection((ip, port))

    def make_conn(self, ip):
        "Connects the client socket to the ip"
        self.ip_conn = ip
        self.sock.connect((ip, self.port))

    def myInfo(self):
        "Returns info about the client socket"
        return (self.host, self.port)

    def work(self):
        #Function that maintains a connection with the server class and is controlled by thread
        pass

    def transmit(self, data):
        "Sends information to the server socket"
        data_temp = str(data)
        host_temp = str(self.host)
        data_temp = (data_temp + " " + host_temp)
        self.last_send = data_temp
        data_temp = data_temp.encode()
        self.sock.send(data_temp)


    def recieve(self):
        "Recieves data from the server socket"
        data = self.sock.recv(1024)
        data = tuple(data.decode())
        if data != self.last_send:
            return data

        return data

#entity classes
class Player(pygame.sprite.Sprite):
    def __init__(self, img_file_tuple, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img_file_tuple[0])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        #tuple that will hold all loaded images
        self.idle = 0
        self.death = 1
        self.spawn = 2
        self.reload = 3

        #Parent dictionary that will refrence subdictionaries for file locations for the animations
        self.animations_dict = {
            self.idle:pygame.image.load(img_file_tuple[0]),
            self.death:pygame.image.load(img_file_tuple[1]),
            self.spawn:pygame.image.load(img_file_tuple[2]),
            self.reload:pygame.image.load(img_file_tuple[3])
        }

    def animate(self, type):
        #Animation control that will be done by a thread
        if type == self.idle:
            #Animate idle
            self.image = self.animations_dict[self.idle]
        if type == self.death:
            #animate death
            self.image = self.animations_dict[self.death]
        if type == self.spawn:
            #spawn Animation
            self.image = self.animations_dict[self.spawn]
        if type == self.reload:
            #animate reloading
            self.image = self.animations_dict[self.reload]

    def info(self):
        #Will return a tuple to be used by the multiplayer server
        pass

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def info(self):
        #Will return a tuple to be used by the multiplayer server
        pass

#diff is the enemy difficulty
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, diff):
        pygame.sprite.Sprite.__init__(self)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def info(self):
        #Will return a tuple to be used by the multiplayer server
        pass

class TileMap:
    def __init__(self, file_path):
        tm = load_pygame(file_path, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmx_map = tm

    def render(self):
        "Renders the tilemap upon the specified surface"
        tID = self.tmx_map.get_tile_image_by_gid
        tiles_group = pygame.sprite.LayeredUpdates()
        for layer in self.tmx_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_img = tID(gid)
                    if tile_img:
                        temp_tile = tile_sprite((x*self.tmx_map.tilewidth, y*self.tmx_map.tileheight), tile_img)
                        tiles_group.add(temp_tile)

        return tiles_group

#My personal sprite class code modded for tiles
class tile_sprite(pygame.sprite.Sprite):
    def __init__(self, pos, tile):
        pygame.sprite.Sprite.__init__(self)
        self.image = tile
        self.rect = self.image.get_rect()
        self.place = pos
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.place[0] += dx
        self.place[1] += dy

#personal test tilemap class
class myTilemap(pygame.sprite.Sprite):
    def __init__(self, file_path):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_pygame(file_path, pixelalpha=True)
        self.width = self.image.width * self.image.tilewidth
        self.height = self.image.height * self.image.tileheight
        self.map = self.image

    def return_img(self):
        return self.image

"""How does the game work?
Will the game be the tilemap, or will the tilemap be an attribute of the game?
Planning:
1. Game will be parent wrapper for other classes defined
2. Game must handle key_input
3. Game must handle entities in it
4. Game must handle pauses
5. Game must handle 

"""



class Game(pygame.Surface):
    def __init__(self, width, height, level):
        pygame.Surface.__init__(self, size=(width, height))
        if level == 0:
            #Dev level

    def update(self):
        #Blits and updates positions of sprites
        pass

    def render(self, display):
        display.blit(self)

class DialogueBox(pygame.Surface):
    def __init__(self, width, height):
        pygame.Surface.__init__(self, size=(width, height))
        self.pos = (width, height)
        self.RECT = (0, 0, 800, 150)
        self.INRECT = (5,5, 790, 140)
        pygame.draw.rect(self, WHITE, self.RECT)
        pygame.draw.rect(self, BLACK, self.INRECT)

    def add_text(self, text, size):
        "This function adds and orders text on the screen"
        self.font = pygame.font.Font("freesansbold.ttf", size)
        self.text_img_list = []
        self.text_list = ["helo", "help", "holder", "holder", "holder", "holder"]

        if (len(text) > 71) and (len(text) > 142) and (len(text) < 213):
            self.text_list[0] = text[:71]
            self.text_list[1] = text[71:142]
            self.text_list[2] = text[142:]
            self.text_img = self.font.render(self.text_list[0], True, WHITE)
            self.text_img2 = self.font.render(self.text_list[1], True, WHITE)
            self.text_img3 = self.font.render(self.text_list[2], True, WHITE)
            self.text_img_rect = self.text_img.get_rect()
            self.text_img2_rect = self.text_img2.get_rect()
            self.text_img3_rect = self.text_img2.get_rect()
            self.text_img_list.append(self.text_img)
            self.text_img_list.append(self.text_img2)
            self.text_img_list.append(self.text_img3)

        elif (len(text) > 71) and (len(text) < 142):
            self.text_list[0] = text[:71]
            self.text_list[1] = text[71:]
            print(self.text_list)
            self.text_img = self.font.render(self.text_list[0], True, WHITE)
            self.text_img2 = self.font.render(self.text_list[1], True, WHITE)
            self.text_img_rect = self.text_img.get_rect()
            self.text_img2_rect = self.text_img2.get_rect()
            self.text_img_list.append(self.text_img)
            self.text_img_list.append(self.text_img2)

        elif (len(text) > 71):
            self.text_list[0] = text[:71]
            self.text_img = self.font.render(self.text_list[0], True, WHITE)
            self.text_img_rect = self.text_img.get_rect()
            self.text_img_list.append(self.text_img)

    def render(self, display):
        "Draws surface on the display"
        display.blit(self, (0, self.pos[1]))

    def display_text_th(self, speed):
        "Will draw text on the screen at the speed specified"
        y_pos = 5
        for line in text_img_list:
            for letter in line:
                self.blit(line[:letter], (6, y_pos))
                print("Blitted: %s" % line[:letter])
                sleep(speed//100)
            y_pos += 20

#Functions
def thread_worker(func, arg):
    my_thread = threading.Thread(target=func, args=arg)
    my_thread.setDaemon(True)
    my_thread.start()


#Full line blit
#y_pos = 5
#for x in self.text_img_list:
#self.blit(x, (6, y_pos))
#y_pos += 20

#Game constants
#Colors
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
AQUA = (0, 255, 255)
FUCHSIA = (255, 0, 255)
GRAY = (128, 128, 128)
LIME = (0, 128, 0)
MAROON = (128, 0, 0)
NAVY_BLUE = (0, 0, 128)
OLIVE = (128, 128,   0)
PURPLE =(128,  0, 128)
SILVER = (192, 192, 192)
TEAL = (0, 128, 128)
YELLOW = (255, 255, 0)
BROWN1 = (132, 93, 51)
LGREY = (158, 158, 158)
ORANGE = (219, 118, 24)

#Game and display control
disp_width = 800
disp_height = 600
FPS = 60
dev_mode = True
game_port = 6573
my_ip = socket.gethostbyname(socket.gethostname())

#file paths
g_dir = os.getcwd()
cfig_dir = (os.path.normpath(g_dir+"/config/ ")).strip()
#Image directories
img_dir = (os.path.normpath(g_dir+"/images/ ")).strip()
misc_img_dir = (os.path.normpath(img_dir+"/misc/ ")).strip()
plyr_img_dir = (os.path.normpath(img_dir+"/player/ ")).strip()
ankr_img_dir = (os.path.normpath(img_dir+"/ankar/ ")).strip()
shai_img_dir = (os.path.normpath(img_dir+"/sheekhai/ ")).strip()
olpl_img_dir = (os.path.normpath(img_dir+"/olpel/ ")).strip()
durn_img_dir = (os.path.normpath(img_dir+"/durn/ ")).strip()

music_dir = (os.path.normpath(g_dir+"/music/ ")).strip()
play_anim_dir = (os.path.normpath(g_dir+"/images/player_animations/ ")).strip()
