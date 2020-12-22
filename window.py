from time import perf_counter
import os
import platform

import pygame
from pygame.locals import *
import tkinter as tk

from entities import Zuikis, Vilkas, Morka

##
#Path must be a list of game states. Each state describes the game completely i.e. it tells where every entity is on the grid.
#Each state has 4 elements: zuikis, wolves, carrots, energy
#Zuikis element is tuple of 2 numbers where zuikis is on the board. In terms of square coordinates
#Wolves element is a list of tuples. Each tuple is square coordinates for each wolf
#Carrot element is a list of tuples for each carrot. Again tuples containt coordinates in the grid.
#Energy is last element and is a number that represents energy of zuikis in the state.
#Diference between each state is one turn. For example game is initialized in state Path[0], then entities make their moves
#and game evolves to state Path[1].
##

class Window:
    def __init__(self, path = None, dim = (30, 30), squaredim = 25):
        self.guilen = 250
        self.path = path
        self.root = tk.Tk() #Main window
        # self.root.iconbitmap('pics/zuikis_con.ico') #Window icon of cool Zuikis. Seems to be slowing launch of the window a lot. Somehow.
        self.root.title('Zuikis adventures') #Name of the window
        self.field = FieldState(field=dim, square=squaredim, nwolves=len(path[0][1]), ncarrots=len(path[0][2])) #Field visualization object init.
        self.field_dims = self.field.get_size()
        self.height, self.width = self.field_dims[0], self.field_dims[1] + self.guilen #Window dims based on the field dims.
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen
        xmid = (ws / 2) - (self.width / 2)
        ymid = (hs / 2) - (self.height / 2)
        self.root.geometry('{}x{}+{}+{}'.format(self.width, self.height, int(xmid), int(ymid))) #Fixes whole window size and starting position
        self.root.resizable(False, False) #Make window unresizable

        self.embed = tk.Frame(self.root, width=self.width-self.guilen, height=self.height) #Embeded pygame frame for field visualization
        self.embed.grid(row = 0, column = 0,columnspan=self.width-self.guilen, rowspan=self.height)
        # self.embed.pack(side=tk.LEFT)

        ##GUI stuff
        ######
        self.gui_font = 'Courier 18 bold'
        self.current_state = 0
        self.playing = True
        self.interval = 1 #Wait time while playing in seconds
        self.speed = 1 #Speed of playing: speed = 1/interval and viceversa
        self.last_gui_update = perf_counter()
        self.gui_bg = 'snow'
        self.gui_fg_text = 'black'
        self.gui_fg_num = '#ff931e'

        anch = 'w'
        info_anch = 'w'
        part_len = 0.6
        first_width = int(self.guilen * part_len)
        second_width = int(self.guilen * part_len)
        ##Labels for total number of moves
        self.total_moves = tk.Label(text = 'Total: ', font = self.gui_font, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.total_moves.grid(row = 0,column = self.width-self.guilen, columnspan = first_width)
        self.total_num = tk.Label(text = int(len(self.path)-1), font = self.gui_font, anchor = info_anch, width = 10,bg = self.gui_bg, fg = self.gui_fg_text)
        self.total_num.grid(row = 0, column = self.width-self.guilen + first_width, columnspan = second_width)
        ##Labels for current move
        self.current_move = tk.Label(text = 'Current:', font = self.gui_font, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.current_move.grid(row = 1, column = self.width-self.guilen,columnspan = first_width)
        self.current_move_num = tk.Label(text = str(1000), font = self.gui_font, anchor = info_anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.current_move_num.grid(row = 1, column = self.width-self.guilen + first_width, columnspan = second_width)
        ##Labels for current energy
        self.current_energy = tk.Label(text = 'Energy:', font = self.gui_font, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.current_energy.grid(row = 2, column = self.width-self.guilen,columnspan = first_width)
        self.current_energy_num = tk.Label(text = str(1000.0), font = self.gui_font, anchor = info_anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_num)
        self.current_energy_num.grid(row = 2, column = self.width-self.guilen + first_width, columnspan = second_width)
        ##Slider for current move/state
        self.path_slider = tk.Scale(self.root, from_ = 1, to = len(self.path), orient = tk.HORIZONTAL, length = self.guilen-10,activebackground = self.gui_fg_num, showvalue = False)
        self.path_slider.bind('<B1-Motion>', self.path_slider_onpressmove)
        self.path_slider.grid(column = self.width-self.guilen, row = 3, columnspan = self.guilen)


        #Play button
        def on_play_press():
            if self.playing:
                self.play_button.config(relief = tk.GROOVE, bg = self.gui_bg)
            else: self.play_button.config(relief = tk.SUNKEN, bg= self.gui_fg_num)
            self.playing = not self.playing
        self.play_button = tk.Button(self.root, text='Play', command = on_play_press, width = 25, relief = tk.SUNKEN, bg= self.gui_fg_num)
        self.play_button.grid(row = 4, column = self.width-self.guilen, columnspan = self.guilen)
        print(self.speed)
        #Animation speed slider
        self.speed_slider = tk.Scale(self.root, label = 'Speed', from_ = 0.5, to = 15,orient = tk.HORIZONTAL, length = self.guilen-10,activebackground = self.gui_fg_num)
        self.speed_slider.bind('<B1-Motion>', self.speed_slider_onpressmove)
        self.speed_slider.grid(row = 5, column = self.width-self.guilen, columnspan = self.guilen)

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
        self.run()#Init main loop

    def run(self):
        """Runs main loop for updating everything inside the window"""
        while self.running:
            self.field.update() #Updates fieldview subwindow
            self.gui_update() #Updates gui
            self.root.update() #Updates whole window

    def gui_update(self):
        """Updates gui elements"""
        if perf_counter() - self.last_gui_update >= self.interval:
            if self.playing:
                next_val = self.current_state + 1
                if next_val >= len(self.path):
                    next_val = 0
                self.current_state = next_val
                self.update_currents()

                self.path_slider.set(self.current_state)
            self.last_gui_update = perf_counter()

    def path_slider_onpressmove(self, event):
        if self.current_state != (self.path_slider.get() - 1):
            self.current_state = self.path_slider.get() - 1
            self.update_currents()

    def speed_slider_onpressmove(self, event):
        if self.speed != (self.speed_slider.get()):
            self.speed = self.speed_slider.get()
            self.interval = 1/self.speed

    def update_currents(self):
        """Update current field and gui elements"""
        self.field.set_state(self.path[self.current_state])
        self.current_move_num.config(text = str(self.current_state))
        self.current_energy_num.config(text = '{:.1f}'.format(float(self.path[self.current_state][-1])))


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
