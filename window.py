from time import perf_counter
import os
import platform

import pygame
from pygame.locals import *
import tkinter as tk

from entities import Zuikis, Vilkas, Morka

##
#Path must be a list of game states. Each state describes the game completely i.e. it tells where every entity is on the grid.
#Each state has 3 elements: zuikis, wolves, carrots
#Zuikis element is tuple of 2 numbers where zuikis is on the board. In terms of square coordinates
#Wolves element is a list of tuples. Each tuple is square coordinates for each wolf
#Carrot element is a list of tuples for each carrot. Again tuples containt coordinates in the grid.
#Diference between each state is one turn. For example game is initialized in state Path[0], then entities make their moves
#and game evolves to state Path[1].
##

class Window:
    def __init__(self,path = None, fielddim = (30, 30), squaredim = 25, guilen = 250):
        self.path = path
        self.root = tk.Tk() #Main window
        # self.root.iconbitmap('pics/zuikis_con.ico') #Window icon of cool Zuikis. Seems to be slowing launch of the window a lot. Somehow.
        self.root.title('Zuikis adventures') #Name of the window
        self.field = FieldState(field=fielddim, square=squaredim) #Field visualization object init.
        self.field_dims = self.field.get_size()
        self.height, self.width = self.field_dims[0], self.field_dims[1] + guilen #Window dims based on the field dims.
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen
        xmid = (ws / 2) - (self.width / 2)
        ymid = (hs / 2) - (self.height / 2)
        self.root.geometry('{}x{}+{}+{}'.format(self.width, self.height, int(xmid), int(ymid))) #Fixes whole window size and starting position
        self.root.resizable(False, False) #Make window unresizable

        self.embed = tk.Frame(self.root, width=self.width-guilen, height=self.height) #Embeded pygame frame for field visualization
        self.embed.grid(columnspan=self.width-guilen, rowspan=self.height)
        self.embed.pack(side=tk.LEFT)

        ##GUI stuff
        ######
        self.current_state = 0
        self.playing = True
        self.interval = 0.65 #Wait time while playing in seconds
        self.last_gui_update = perf_counter()
        self.path_slider = tk.Scale(self.root, from_ = 1, to = len(self.path), orient = tk.HORIZONTAL)
        self.path_slider.bind('<B1-Motion>', self.path_slider_onpressmove)
        self.path_slider.pack()

        #Play button stuff
        def on_play_press():
            self.playing = not self.playing
            print(self.playing)
        self.play_button = tk.Button(self.root, text='Play', command = on_play_press)
        self.play_button.pack()


        ##Rest
        ######
        #Stuff for embedding
        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
        if platform.system() == 'Windows':
            os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.field.create()#Creates the field visualization
        self.running = True

        #Window closing func
        def on_close():
            self.running = False
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)
        if self.path is not None:
            self.field.set_state(path[10])
        self.run()#Init main loop

    def run(self):
        """Runs main loop for updating everything inside the window"""
        while self.running:
            self.field.update()
            self.gui_update()
            self.root.update()

    def gui_update(self):
        """Updates gui elements"""
        if perf_counter() - self.last_gui_update >= self.interval:
            if self.playing:
                next_val = self.current_state + 1
                if next_val >= len(self.path):
                    next_val = 0

                self.field.set_state(self.path[next_val])
                self.current_state = next_val
                self.path_slider.set(self.current_state)
            self.last_gui_update = perf_counter()

    def path_slider_onpressmove(self, event):
        if self.current_state != (self.path_slider.get() - 1):
            self.current_state = self.path_slider.get() - 1
            self.field.set_state(self.path[self.current_state])


class FieldState:
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255,255,255)
    GREY1 = pygame.Color(199, 201, 215)

    def __init__(self, field = (30, 30), square = 20, boundthick = 4, innerthick = 2, nwolves = 1, ncarrots = 5):
        self.created = False
        self.n_vilkai, self.n_morkos = nwolves, ncarrots
        self.square = square
        self.field = field
        self.height, self.width = field[0] * square + 2*boundthick, field[1]*square + 2 * boundthick
        self.x0, self.y0 = boundthick, boundthick

        self.grid_thick = boundthick * 2 + 1
        self.grid_inner_thick = innerthick
        self.screen = None
        self.sprites = pygame.sprite.Group()
        self.FramePerSec = None
        self.zuikis = None
        self.vilkai = []
        self.morkos = []
        self.FPS = 60

    def create(self):
        if self.created:
            print('Warning: field visual is already created.')
            return
        self.created = True
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(self.WHITE)
        self.FramePerSec = pygame.time.Clock()


        #Create and deal with entities
        self.zuikis = Zuikis(self)
        for i in range(self.n_vilkai):
            self.vilkai.append(Vilkas(self))
        for i in range(self.n_morkos):
            self.morkos.append(Morka(self))
        # self.move_entity(self.zuikis, 28, 15)
        # self.move_entity(self.morkos[0], 0, 0)
        # self.move_entity(self.vilkai[0], 10, 0)
        self.sprites.add(self.zuikis)
        for v in self.vilkai: self.sprites.add(v)
        for m in self.morkos: self.sprites.add(m)

    def update(self):
        self.FramePerSec.tick(self.FPS)
        self.sprites.draw(self.screen)

        ##Update
        self.sprites.update()
        ##Render
        self.screen.fill((self.WHITE))
        self.draw_grids()
        self.sprites.draw(self.screen)
        ##Flip
        pygame.display.flip()

    def draw_grids(self):
        """Draw grid lines in the field"""
        #Draw horizontal lines
        for i in range(1, self.field[0]):
            pygame.draw.line(self.screen, self.GREY1, (0, self.y0 + self.square * i), (self.width, self.y0 + self.square * i), self.grid_inner_thick)
        for i in range(1, self.field[1]):
            pygame.draw.line(self.screen, self.GREY1, (self.x0 + self.square * i, 0), (self.x0 + self.square * i, self.height), self.grid_inner_thick)

        pygame.draw.line(self.screen, self.BLACK, (0,0), (0,self.height), self.grid_thick)
        pygame.draw.line(self.screen, self.BLACK, (self.width, 0), (self.width, self.height), self.grid_thick)
        pygame.draw.line(self.screen, self.BLACK, (0, 0), (self.width, 0), self.grid_thick)
        pygame.draw.line(self.screen, self.BLACK, (0, self.height), (self.width, self.height), self.grid_thick)

    def move_entity(self, ent,x, y):
        """Moves sprite to different place on the grid"""
        ent.rect.topleft = (self.x0 + x * self.square, self.y0 + y * self.square)

    def set_state(self,state):
        self.move_entity(self.zuikis, state[0][0], state[0][1]) #Move Zuikis
        #Move all Wolfes
        for ind, st in enumerate(state[1]):
            self.move_entity(self.vilkai[ind], st[0],st[1])
        #Move all Carrots
        for ind, st in enumerate(state[2]):
            self.move_entity(self.morkos[ind], st[0],st[1])

    def get_size(self):
        return self.height, self.width
